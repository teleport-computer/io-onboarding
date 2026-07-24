# Feedling ↔ QQ 桥接插件 · 安装指南

> 解决的问题:QQ 里回复你的不是你的 ds,而是 AstrBot 自带的模型在抢答("双脑"),
> 且 QQ 与 IO App 上下文不通。
>
> 装完后:QQ 变成你 ds 的第二个入口——QQ 里回复你的就是 IO 里那个 ds 本人,
> 对话在 App 里也看得到,上下文完全互通。

---

## 第 1 步:把插件装进 AstrBot

在跑 AstrBot 的机器上执行:

```bash
wget https://github.com/teleport-computer/io-onboarding/archive/refs/heads/main.zip -O /tmp/io.zip
unzip -o /tmp/io.zip -d /tmp/
cp -r /tmp/io-onboarding-main/astrbot-feedling-bridge <你的AstrBot目录>/data/plugins/
```

然后打开 AstrBot WebUI → 插件管理 → **重载插件**(依赖 `httpx`、`cryptography` 会自动安装)。

## 第 2 步:填配置

WebUI → 该插件的配置页,共 5 项。

**前 3 项直接从你 VPS 上 resident consumer 的启动配置(env 文件)里原样抄**,
不要手打、不要用别处的地址:

| 插件配置项 | 抄 consumer env 里的哪个值 |
|---|---|
| `feedling_api_url` | `FEEDLING_API_URL` |
| `feedling_api_key` | `FEEDLING_API_KEY` |
| `feedling_enclave_url` | `FEEDLING_ENCLAVE_URL` |
| `owner_qq` | 填**你自己的 QQ 号**(白名单,可多个) |
| 其余(轮询间隔等) | 保持默认 |

> ⚠️ API key 是高敏感凭据:不要截图、不要发群里。

保存并再次重载插件。

## 第 3 步:关掉 AstrBot 自带的模型

在 WebUI 里把这个机器人的 **provider / LLM 禁用**。

插件本身带第二道保险(收到你的私聊会自动拦截 AstrBot 的默认回答),
但从源头关掉最干净——这是消灭"双脑"的关键一步。

## 第 4 步:验证

1. 用你的 QQ 给机器人**私聊**发送:

   ```
   /feedling_selftest
   ```

   会返回四步自检结果(✓ / ✗ / △,附修复提示):
   ① API 与账号 ② 解密通道 ③ 加密信封 ④ QQ 会话捕获

2. 自检通过后,正常发一句话。**回复要等几秒到几分钟**(agent 是异步回合,
   不是插件卡了)。回你的将是 IO 里那个 ds 本人,并且这段对话在 IO App 里同步可见。

## 已知边界

- 暂只支持**文字**;发图片/语音会收到"暂只支持文本"的提示
- 只桥接你白名单里的 QQ **私聊**;群聊和陌生人永远进不来(安全设计,不是 bug)
- 机器人不会主动找你说话以外的行为;所有回复都来自你自己的 ds

## 卡住了?

把 `/feedling_selftest` 的**完整输出**发回来即可,一分钟定位。

想了解原理(单脑桥接原则、排查表):同仓库的
[`im-bridge-guide.md`](https://github.com/teleport-computer/io-onboarding/blob/main/im-bridge-guide.md)。
