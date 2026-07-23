# Feedling IO Bridge for AstrBot

把 AstrBot 当成 QQ 的“门”，把 Feedling resident agent 当成唯一的“脑”。

这款插件只做两件事：

1. 白名单主人的 QQ 私聊文本 → Feedling `POST /v1/chat/message`（共享 v1
   加密信封，带 `client_msg_id` 幂等键）。
2. Feedling enclave 解密后的 agent 回复 → AstrBot 主动消息 → 主人 QQ。

插件不会调用 AstrBot provider、LLM、Agent Runner 或 persona。群聊和非白名单
QQ 不会进入 Feedling。

## 兼容性

- AstrBot `>=4.9.2,<5`。
- 按 2026-07-24 的 AstrBot v4 官方文档开发：
  [监听私聊与阻断事件传播](https://docs.astrbot.app/dev/star/guides/listen-message-event.html)、
  [持久化 UMO 后主动发送](https://docs.astrbot.app/dev/star/guides/send-message.html)、
  [插件配置](https://docs.astrbot.app/dev/star/guides/plugin-config.html)、
  [插件 KV 存储](https://docs.astrbot.app/dev/star/guides/storage.html)。
- 已声明 OneBot v11 (`aiocqhttp`) 与 QQ Official 两种 QQ adapter。不同 adapter
  的主动发送能力仍受 QQ 平台本身限制。

## 安装：三步

### 1. 安装插件

把整个 `astrbot-feedling-bridge/` 目录复制到 AstrBot 的
`data/plugins/astrbot-feedling-bridge/`，在 WebUI 重载插件。AstrBot 会按照
`requirements.txt` 安装 `httpx` 与 `cryptography`。

目录必须至少包含：

```text
main.py
metadata.yaml
requirements.txt
_conf_schema.json
content_encryption.py
```

### 2. 填配置

在 WebUI 的插件配置页填写：

| 配置 | 说明 |
| --- | --- |
| `feedling_api_url` | Feedling API，例如 `https://test-api.feedling.app` |
| `feedling_api_key` | 这个用户自己的 API key |
| `feedling_enclave_url` | 同一用户 resident consumer 使用的 TEE history 地址 |
| `owner_qq` | 可注入 Feedling 对话的主人 QQ 白名单，支持多个 |
| `poll_interval` | 默认 20 秒，最小 10 秒 |
| `forward_app_messages` | 默认开；关闭后只把 QQ 桥接消息对应的回复发回 QQ |

保存并重载插件。主人第一次给机器人发普通私聊后，插件会捕获
`event.unified_msg_origin` 并写入 AstrBot 插件 KV；后续后台任务才能主动发回
该 QQ 会话。cursor、幂等状态和会话地址都不会写进插件源码目录。

### 3. 关闭 AstrBot 自带的脑

必须禁用这个 QQ 会话的 AstrBot provider/LLM，避免 AstrBot 和 Feedling agent
同时回答：

- AstrBot v4.7+：在 WebUI 的 Custom Rules 中对该 UMO 关闭 LLM。
- 不需要 AstrBot AI 的专用桥实例：直接移除/禁用默认 chat provider。
- 插件本身也会在主人普通私聊进入时立即设置 `event.call_llm = False` 并调用
  `event.stop_event()`，这是第二层防线。

## 自检

主人在 QQ 私聊发送：

```text
/feedling_selftest
```

自检依次验证：

1. API 与 `/v1/users/whoami`，包括 32-byte user/enclave 内容公钥。
2. enclave `/v1/chat/history`。
3. 在内存中构造共享 v1 信封（dry-run，不污染聊天、不唤醒 agent）。
4. 是否已经捕获 QQ 的 UMO，可否主动发送。

每步返回 `✓` / `✗` / `△` 和修复提示。日志不会打印 API key 或明文信封密钥。

## 消息语义

- 入站 handler 只投递，不等待 agent；回复可能在几秒到几分钟后由后台轮询送达。
- 目前只桥接文本；主人发送图片、语音或其他无文本消息时会收到明确提示。
- `client_msg_id` 在网络重试和 `content_pk_fpr_mismatch` 刷 key 重封时保持不变，
  所以一次 QQ 消息最多产生一个 Feedling user turn。
- 插件在 409 `content_pk_fpr_mismatch` 时强制重取 whoami、公钥重封并只重试一次。
- 初次捕获 QQ 会话前先以 enclave 最新 history 时间播种 cursor，不回放安装前的
  历史消息。
- history 使用 1ms 重叠窗口与持久化 message ID 去重，避免同 timestamp 边界丢信。
- QQ 主动发送失败时不推进 cursor；下一轮会重试。
- 多个主人 UMO 使用逐目标 delivery ledger，第二个目标失败不会让第一个目标重复收到。
- `forward_app_messages=false` 时，仅转发 `reply_to_message_id` 属于本插件入站消息的回复。

## 安全边界

- 仅 `PRIVATE_MESSAGE`，仅 `owner_qq`；群聊永不桥接。
- API TLS 正常校验。只有配置的 dstack enclave client 使用 `verify=False`，与
  Feedling resident consumer 当前的自签入口用法一致。
- 明文只在 AstrBot 进程内短暂停留，后端收到的是共享 v1 ciphertext envelope。
- `content_encryption.py` 是从 Feedling 后端原样 vendor 的 wire-compatible 实现；
  Feedling 加密协议变化时必须同步更新。
- API key 属于高敏感凭据：不要截图、不要提交到 Git、不要贴到群聊。

## 测试

纯逻辑测试不需要安装 AstrBot：

```bash
python -m pip install -r requirements.txt -r tests/requirements.txt
python -m pytest -q
```

真实 test 环境信封往返（只允许 `test-api.feedling.app`）：

```bash
python tests/real_roundtrip.py
```

脚本会创建一次性账号，完成“共享信封 → send → enclave history 明文取回”，并在
`finally` 中调用 `/v1/account/reset` 硬删除账号。进程意外死亡时，0600 权限的
清理凭据会留在 `~/.feedling-e2e-orphans/astrbot-bridge-<user_id>.json`。

## 常见问题

| 症状 | 检查 |
| --- | --- |
| QQ 同时出现两种语气的回复 | AstrBot provider/LLM 没关；见安装第 3 步 |
| QQ 发出后完全没反应 | 先跑 `/feedling_selftest`；确认 owner QQ、API key、enclave URL |
| Feedling 有回复但 QQ 没收到 | 主人先发普通私聊捕获 UMO；检查 adapter 是否支持主动发送 |
| App 回复不想出现在 QQ | 关闭 `forward_app_messages` |
| 409 key mismatch | 插件会自动重取 whoami 重封一次；持续出现时检查账号/API key 是否配错 |
| 重载插件卡住 | 检查网络；插件最多给 poller 2 秒优雅退出，随后会取消任务 |
