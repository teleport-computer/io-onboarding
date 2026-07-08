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

**第 1 步 · 从 app 复制连接配置**

打开 IO → Chat → 选「**我有自己的服务器**」。复制它给你的那段 `resident consumer config`
（里面有 `FEEDLING_API_URL`、`FEEDLING_API_KEY`、以及一个 enclave 地址）。**整段复制，别改。**

**第 2 步 · 把下面这段话，连同配置，发给你 VPS 上的 agent**

```
我要把 IO 从托管模式切换到用你（我 VPS 上的 agent）来跑。
下面是我从 app 复制的连接配置：

<在这里粘贴你从 app 复制的整段配置>

请按 IO 的 resident-agent skill 完成这次切换：先确认能解密我云端的数据，
再停掉托管，确认托管停了之后，再把你自己作为常驻服务启动，最后确认切换完成。
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

**Step 1 · Copy the connection config from the app**

Open IO → Chat → choose "**I have my own server**". Copy the `resident consumer config`
it shows you (it contains `FEEDLING_API_URL`, `FEEDLING_API_KEY`, and an enclave address).
**Copy the whole thing, unchanged.**

**Step 2 · Send this message, plus the config, to your VPS agent**

```
I want to switch IO from hosted mode to running on you (my agent on my VPS).
Here's the connection config I copied from the app:

<paste the whole config you copied from the app here>

Please follow IO's resident-agent skill to do the switch: first confirm you can
decrypt my cloud data, then stop the hosted agent, wait until it's fully stopped,
then start yourself as a resident service, and finally confirm the switch is done.
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
