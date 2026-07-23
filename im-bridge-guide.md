# 把 Feedling IO 接入 QQ / IM：单脑桥接指南

## 一句话原则

**IM 框架只当门，Feedling resident agent 才是唯一的脑。**

QQ、微信、Telegram 等 adapter 负责收消息和发消息；它们不应再运行一套独立
LLM、persona 或上下文。否则不是“多入口访问同一个人”，而是两个没有共享记忆的
机器人抢着扮演同一个人。

## 为什么“双脑”一定会出问题

典型错误拓扑：

```text
QQ -> AstrBot 自带 LLM --------> 回复 A
  \-> 手搓 HTTP -> Feedling agent -> 回复 B
```

两条路径拥有不同的：

- system prompt / persona；
- 会话上下文；
- Feedling memory、perception 与工具状态；
- 重试、幂等和回复认领状态。

所以它们会产生两种语气、重复回复、前后矛盾，甚至一条路径已经处理完，另一条还在
重试。把同一份 prompt 复制两遍也解决不了状态分叉。

正确拓扑：

```text
主人 QQ 私聊
  -> AstrBot adapter（白名单、无 LLM）
  -> Feedling shared v1 envelope
  -> 用户自己的 resident consumer
  -> 用户自己的 agent
  -> enclave decrypted history
  -> AstrBot 主动发送
  -> 主人 QQ
```

## QQ：使用官方 AstrBot-Feedling 插件

仓库内的 [`astrbot-feedling-bridge/`](./astrbot-feedling-bridge/) 是纯搬运插件：

- 只监听白名单主人的私聊；
- `event.stop_event()` 阻断 AstrBot 默认 LLM；
- 入站使用共享 v1 信封与 `client_msg_id` 幂等；
- 出站轮询 enclave decrypted history；
- 保存 AstrBot UMO 后用 `context.send_message` 主动发送；
- 群聊、非白名单和 AstrBot provider 都不进入 Feedling。

AstrBot 官方 API 依据：

- [监听消息与停止事件传播](https://docs.astrbot.app/dev/star/guides/listen-message-event.html)
- [保存 UMO 并主动发送](https://docs.astrbot.app/dev/star/guides/send-message.html)
- [插件配置 schema](https://docs.astrbot.app/dev/star/guides/plugin-config.html)
- [插件 KV 存储](https://docs.astrbot.app/dev/star/guides/storage.html)

安装、配置、自检和测试命令见
[`astrbot-feedling-bridge/README.md`](./astrbot-feedling-bridge/README.md)。

## 其他 IM：裸桥必须满足的契约

如果目标平台没有官方插件，可以写一个小桥，但必须同时满足下面各项。

### 入站

1. 只接受私聊或明确设计过的会话类型。
2. 在进入 Feedling 前做稳定 ID 白名单；昵称、显示名不可作为身份。
3. 每个逻辑消息只生成一次 `client_msg_id`，所有网络重试复用它。
4. 从 `/v1/users/whoami` 获取当前 `public_key` 与
   `enclave_content_public_key_hex`。
5. 用 `visibility=shared` 的 v1 envelope POST `/v1/chat/message`。
6. 收到 409 `content_pk_fpr_mismatch` 时，强制刷新 whoami、重封并最多重试一次。
7. 投递完成就返回；不要同步等待 agent。

### 出站

1. 从与 resident consumer 相同的 enclave
   `/v1/chat/history?since=<cursor>` 读取明文 history。
2. 只转发 agent / assistant 角色；不要回显桥自身写入的 user 消息。
3. cursor 与已处理 message ID 必须持久化；timestamp 查询保留小重叠窗口。
4. IM 发送失败时不能推进 cursor。
5. 多目标发送要记录每个 `(message_id, target)` 的完成状态。
6. 如果只想转发桥接会话，记录入站 parent ID，只接受匹配的
   `reply_to_message_id`。
7. 首次启用先用最新 history 播种 cursor，避免把多年历史一次性推到 IM。

### 生命周期与安全

1. 插件停用/重载时取消 poll task、关闭 HTTP client。
2. API 使用正常 TLS 校验；只有明确的自签 enclave client 才可局部
   `verify=False`。
3. API key 不进日志、不进代码、不进截图。
4. 外人、群聊、机器人自己的消息都不能注入 companion。
5. IM 框架的 provider/LLM 必须关闭；代码层再做一次 stop/consume。

## 排查表

| 症状 | 最可能原因 | 修复 |
| --- | --- | --- |
| 同一条消息收到两次、语气不同 | 双脑：IM 框架 LLM 与 Feedling 同时回复 | 关闭 IM provider/LLM，并确认入站 handler 会 stop/consume |
| QQ 能发，Feedling 没有 user turn | owner 白名单、API key、共享信封或 409 key mismatch | 跑 `/feedling_selftest`，查看 API/whoami 与 envelope dry-run |
| Feedling 已回复，QQ 没消息 | 没保存 UMO、adapter 不支持主动发送、poller 已停 | 主人先发普通私聊；检查主动消息能力和插件日志 |
| 重启后重复推旧回复 | cursor / processed IDs 没持久化，或先发送后崩溃 | 使用插件 KV；保留 delivery ledger |
| 重启后永远收不到回复 | cursor 初始化过大或 timestamp 边界跳过 | `since=cursor-ε` 加 message ID 去重 |
| App 的聊天也出现在 QQ | 开启了全量镜像 | 设置 `forward_app_messages=false` |
| 只有群里不工作 | 设计如此，不是 bug | 官方桥明确不支持群聊，避免群成员注入 |
| 发送后等很久 | agent 是异步回合，poll 默认 20 秒 | 确认 resident consumer 在线；按需降低到不小于 10 秒 |
| 频繁 409 `content_pk_fpr_mismatch` | 内容公钥已轮换或账号/API key 配错 | 刷新 whoami 重封；核对当前账号 |
| 自检 API 绿、enclave 红 | TEE URL、网络或自签入口问题 | 核对 resident consumer 使用的 enclave URL 与 TEE 状态 |

## 上线前验收

- [ ] IM provider/LLM 已关闭。
- [ ] 非白名单 ID 无法产生 Feedling chat row。
- [ ] 群聊无法产生 Feedling chat row。
- [ ] 同一个 `client_msg_id` 重试不会产生两行。
- [ ] 共享 envelope 能从 enclave history 读回原文。
- [ ] agent 回复只主动发送一次。
- [ ] IM 发送失败后下一轮会重试。
- [ ] 插件重载后 cursor、UMO、pending parent 仍在。
- [ ] 测试账号已通过 `/v1/account/reset` 删除。
