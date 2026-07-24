# 从「托管」切换到「你的 VPS Agent」 · Switch to Your VPS Agent

把 IO 从**由我们托管帮你跑 agent**，换成**你自己 VPS（或 Mac mini）上的 agent** 来跑。

> 🟢 **你的数据不会丢、也不会搬家。** 你的身份卡、记忆、聊天历史，一直以密文
> 存在云端；切换只是换「谁来跑你的 agent」，不碰你的任何数据。你的账号和登录
> 密钥都**不变**。

---

## 中文

### 🚫 最重要的一条

**整个过程里，绝对不要点 app 里的「删除账号 / Delete Account & Reset」。**
按了它会重置你的密钥，老账号和记忆就找不回来了。切换**不需要**删除任何东西。

### 你需要什么

- 一台**一直在线的 VPS**（或 Mac mini），上面跑着你的 agent（Claude Code / OpenClaw / Hermes 等）。
- 你平时就用这个 agent 帮你操作 IO。这次切换，也是**让这个 VPS 上的 agent 来做**——你不用自己敲命令。

### 3 步

**第 1 步 · 从 app 复制连接信息**

打开 IO → **设置** → 「**账号凭据**」→ 「**导出与备份凭据**」。复制其中的
**服务器地址（Server URL）** 和 **API Key** 两项。

> ⚠️ 那张卡里还显示一个「**私钥**」——**不要复制、不要发给任何人**，这次切换用不到它。

解密源（enclave）地址不在那张卡里，它是固定值，按你在用的环境从下表取：

| 环境 | `FEEDLING_ENCLAVE_URL` |
|---|---|
| 正式版 (App Store) | `https://9798850e096d770293c67305c6cfdceed68c1d28-5003s.dstack-pha-prod9.phala.network` |
| test 内测版 | `https://173c7f49aeb54acb424676b17b17f78e5e2b2938-5003s.dstack-pha-prod9.phala.network` |

（不确定自己在哪个环境？看你刚复制的服务器地址：`https://api.feedling.app` = 正式版，
`https://test-api.feedling.app` = test。）

**第 2 步 · 把下面这段话，连同配置，发给你 VPS 上的 agent**

```
我要把 IO 从托管模式切换到用你（我 VPS 上的 agent）来跑。这是我的连接配置：

FEEDLING_API_URL=<第 1 步复制的服务器地址>
FEEDLING_API_KEY=<第 1 步复制的 API Key>
FEEDLING_ENCLAVE_URL=<第 1 步表格里对应环境的地址>

请先读 https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-resident-agent.md
里「Switching a user from hosted to their VPS agent」一节，严格按那套流程切换：
先确认能解密我云端的数据，再停掉托管并把账号切成 resident 模式，等托管确认停了，
再把你自己作为常驻服务启动，最后确认切换完成。
我的账号已经有身份卡和记忆——不要注册新账号、不要重新初始化身份。
过程中的命令、日志都留在我们这个对话里，别动我在 IO 里的任何聊天和记忆。
```

你 VPS 上的 agent 会自己完成：验证 → 停托管 → 启动自己 → 确认。这中间可能要**等几分钟**，
属于正常（要等托管那边干净地停下来，避免两个 agent 同时服务你）。

**第 3 步 · 在 app 里确认切换成功**

回到 IO → Chat，**发一条消息**。大约 30 秒内收到一条**正常的、像平时那样的回复**
（不是模板/系统提示），就说明你已经在用**你 VPS 上的 agent** 了，切换完成。🎉

### 万一出问题

- **发消息半天没人回**：多半是托管已停、但你 VPS 上的 agent 还没接上。
  让你的 agent 检查它的常驻服务是否在运行、日志里有没有报错。
- **想变回托管**：在 app 里重新填写一次你的模型 API key（「我有模型 API key」设置），
  验证通过后我们会自动重新接管，你的数据同样一点不动。
- 还搞不定 → 看 [troubleshooting.md](./troubleshooting.md)，或联系我们。

---

## English

### 🚫 The one rule that matters most

**Never tap "Delete Account & Reset" in the app during this process.**
It resets your key and your old account and memories become unrecoverable.
Switching does **not** require deleting anything.

### What you need

- An **always-on VPS** (or Mac mini) running your agent (Claude Code / OpenClaw / Hermes, etc.).
- You already use this agent to operate IO. For this switch, **let your VPS agent do the work** —
  you don't type any commands yourself.

### 3 steps

**Step 1 · Copy your connection info from the app**

Open IO → **Settings** → "**Account keys**" → "**Export / back up keys**". Copy the
**Server URL** and the **API Key**.

> ⚠️ That card also shows a "**private key**" — **do not copy it or send it to anyone**;
> the switch doesn't need it.

The decrypt-source (enclave) address is not on that card; it's a fixed per-environment
value — pick yours from this table:

| Environment | `FEEDLING_ENCLAVE_URL` |
|---|---|
| Production (App Store) | `https://9798850e096d770293c67305c6cfdceed68c1d28-5003s.dstack-pha-prod9.phala.network` |
| test (beta) | `https://173c7f49aeb54acb424676b17b17f78e5e2b2938-5003s.dstack-pha-prod9.phala.network` |

(Not sure which environment you're on? Check the Server URL you just copied:
`https://api.feedling.app` = production, `https://test-api.feedling.app` = test.)

**Step 2 · Send this message, plus the config, to your VPS agent**

```
I want to switch IO from hosted mode to running on you (my agent on my VPS).
Here is my connection config:

FEEDLING_API_URL=<the Server URL copied in Step 1>
FEEDLING_API_KEY=<the API Key copied in Step 1>
FEEDLING_ENCLAVE_URL=<the address for my environment from the Step 1 table>

First read the "Switching a user from hosted to their VPS agent" section of
https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-resident-agent.md
and follow that procedure exactly: first confirm you can decrypt my cloud data,
then stop the hosted agent and switch my account to resident mode, wait until
hosted is confirmed stopped, then start yourself as a resident service, and
finally confirm the switch is done.
My account already has an identity card and memories — do NOT register a new
account and do NOT re-initialize identity.
Keep all commands and logs here in our chat; don't touch any of my IO chats or memories.
```

Your VPS agent handles it all: verify → stop hosted → start itself → confirm. This can take
**a few minutes** — that's normal (it waits for the hosted side to stop cleanly so two
agents never serve you at once).

**Step 3 · Confirm in the app**

Back in IO → Chat, **send a message**. If you get a **normal reply** (not a template/system
notice) within ~30 seconds, you're now running on **your VPS agent**. Done. 🎉

### If something goes wrong

- **No reply for a while**: usually the hosted side stopped but your VPS agent hasn't
  connected yet. Ask your agent to check whether its resident service is running and look
  at the logs.
- **Want to go back to hosted**: just re-enter your model API key in the app
  ("I have a model API key" setup); once it verifies, we take over again automatically,
  and your data stays untouched.
- Still stuck → see [troubleshooting.md](./troubleshooting.md) or contact us.
