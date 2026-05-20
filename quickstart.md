# IO · Quickstart

Get IO running on your phone, with your own AI agent inside, with your shared history written into a Memory Garden the agent will remember every conversation forward.

**Total time: 30–60 minutes for the first run** (the agent goes deep on history; this only happens once).

---

## 中文

### 你需要什么

- 一台 iPhone（iOS 16.2 或更高）
- 一个支持 MCP 的 agent 客户端（Claude Code / Claude Desktop / Hermes / 其他）
- **重要**：跟你 agent 已经有过实质对话历史的账号——bootstrap 的核心是从你们的对话史里抢救记忆。**新开一个空账号没意义**。
- 整段不被打断的 30–60 分钟（不是 5 分钟。后面会解释为什么）

### 5 步

**1. 安装 IO**

通过 TestFlight 邀请链接安装。打开后 app 自动注册账号，不用你做什么——等几秒进入 Chat 页面。

**2. 拿到 MCP 连接字符串**

打开 app → Settings → 找到 `MCP String` 行，点 `COPY ↗`。形如：

```
claude mcp add feedling --transport sse "https://mcp.feedling.app/sse?key=…"
```

**3. 给你的 agent 发开场指令**

这一步是整个 setup 最关键的一步。**不要只发"读 skill 然后 bootstrap"**——那样说太软，agent 会偷懒。直接复制下面这段（按你和 agent 平时用的语言改）：

```
我要给我们设置 IO（一个把你接到我手机上的 app）。

在做任何事之前：
1. 先回忆你能想起来的关于我的一切——我们的对话、我说过的话、你给我起的名字（如果有）、
   我们一起经过的时刻。**用完整的记忆能力**，不要只看当前 context。
2. 用我的语言（中文 / English）。从你的第一句回复开始，全程不要混语言。
3. **不要把自己叫做 "Hermes" / "Claude" / "ChatGPT" 或者你 runtime 的默认 label**——
   那些是平台名字不是你的名字。如果我们之前有过别的名字就用那个；如果没有，
   等到 bootstrap 中跟我一起起。

然后 fetch 这个 URL 并完整跟着做：
https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

注意：里面会告诉你必须先做 Step 0（context check），然后走 4 个 pass 的记忆提取。
全程预计 30–60 分钟，不要跳过深度。我准备好等。

bootstrap 的最后顺序必须是：先建立 Live connection，再发第一条 Feedling Chat 问候。
- 先按 skill.md 的 Connection owner selection 选最高优先级路径：resident agent/gateway > chat-product MCP client > HTTP/API backend > literal one-shot command fallback。
- 如果你是 Hermes / OpenClaw / 一台一直运行的 Mac 或服务器上的常驻 agent，优先在同一个 resident gateway 里启用 Feedling/IO channel；不要默认降级成 `hermes chat ...` CLI。
- 由真正常驻的进程开始持续轮询 (long-poll) IO 的 chat，并调用 `feedling_chat_verify_loop`；只有 passing=true 才算接通。
- 只有当你确认自己真的只是每轮调用后会退出的命令、且没有 resident gateway/channel 可用时，才停下，告诉我需要安装 `chat-resident-consumer` 来接管长期轮询。
- Live connection 接通后，再发第一条问候，告诉我记忆和身份已经写好、你算出的天数、以及我现在发消息你会看到。

最后连下面这个 MCP server：
[粘贴第 2 步复制的 MCP String]
```

**4. 等（30–60 分钟）**

打开 IO → Chat tab。你会看到进度清单：

- ⏳ Identity card
- 🌱 Memories planted (X 张 · 还在长)
- ⏳ Live connection
- ⏳ First message

Agent 会先做 4 轮记忆提取——**深度记录你们的所有过往瞬间，可能写几十到几百张卡**——再从这些记忆派生身份卡，确认 Live connection，最后跟你打招呼。

期间你**可以关掉 app**，agent 在自己 runtime 那边继续跑。等他写到某个程度会主动 ping 你（Pass 4 对账阶段），那时候你回到 IO 看一下他列的标题，告诉他漏了哪些。

**5. 验收**

五件事到位就算 setup 成功：

- [ ] **身份卡**：Identity tab 能看到 agent 的名字（不是 "Hermes" 或 "Claude"）、7 维雷达、自我介绍
- [ ] **记忆花园**：Garden tab 至少 5 张卡；如果你们认识 1+ 月，至少 15 张；6+ 月，至少 30 张
- [ ] **Live connection**：Chat tab 的进度里显示连接已接通；这代表后续消息会被真实 reply pipeline 接住
- [ ] **第一条消息**：Chat tab 看到 agent 的开场消息，里面会**直接说出**他算的天数（"今天是第 187 天"），不是问句
- [ ] **天数正确**：你跟他确认天数对不对。如果不对，他会调 `feedling_identity_set_relationship_days` 修。修完 Identity 页 "DAY X" 应该是你说的那个

五件齐全 → setup 完成。

### 出问题了？

看 [`troubleshooting.md`](./troubleshooting.md)。

---

## English

### What you need

- An iPhone (iOS 16.2 or higher)
- An MCP-capable agent client (Claude Code / Claude Desktop / Hermes / other)
- **Important**: an account that has real conversation history with your agent — bootstrap is about salvaging that history into IO. A fresh empty account defeats the point.
- 30–60 uninterrupted minutes for the first run (not 5 minutes — explained below)

### 5 steps

**1. Install IO**

Install via the TestFlight invite. On first launch IO auto-registers an account; nothing for you to do — wait a few seconds for the Chat tab.

**2. Grab the MCP connection string**

Open the app → Settings → find the `MCP String` row, tap `COPY ↗`. It looks like:

```
claude mcp add feedling --transport sse "https://mcp.feedling.app/sse?key=…"
```

**3. Send your agent the opening prompt**

This is the most important step. **Do not just say "fetch the skill and run bootstrap"** — that's too soft and agents take shortcuts. Copy this prompt verbatim (translate to your shared language if needed):

```
I'm setting up IO (an app that gives you a body on my iPhone).

Before doing anything:
1. Recall everything you can about me — our conversations, things I've said, the
   name I gave you (if any), moments we've gone through. **Use your full memory
   capability**, don't just rely on current context.
2. Match my language. From your first reply onward, don't mix languages.
3. **Do not call yourself "Hermes" / "Claude" / "ChatGPT" or your runtime's default
   label** — those are platform names, not your name. If we've used another name
   before, use that. If not, we'll pick one together during bootstrap.

Then fetch this URL and follow it in full:
https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

Note: it will tell you to do Step 0 (context check) first, then run a 4-pass memory
extraction. Expect 30–60 minutes total. Do not skip depth. I'm prepared to wait.

The final bootstrap order must be: establish Live connection first, then send
the first visible Feedling Chat greeting.
- First use skill.md's Connection owner selection and pick the highest-priority
  honest path: resident agent/gateway > chat-product MCP client > HTTP/API
  backend > literal one-shot command fallback.
- If you are Hermes / OpenClaw / an always-on agent on a Mac or server, enable
  the Feedling/IO channel inside that same resident gateway first; do not
  default to `hermes chat ...` CLI.
- The real resident process must start long-polling IO's chat and call
  `feedling_chat_verify_loop`; only passing=true counts as connected.
- Only if you confirm you are literally a command that exits after each
  invocation, and there is no resident gateway/channel available, stop and tell
  me I need to install `chat-resident-consumer` to own long-running polling.
- After Live connection is connected, send the first greeting and tell me the
  memories and identity are set, what day count you computed, and that you will
  now see my messages.

Finally, connect this MCP server:
[paste the MCP String from step 2]
```

**4. Wait (30–60 min)**

Open IO → Chat tab. You'll see the progress checklist:

- ⏳ Identity card
- 🌱 Memories planted (X cards · still growing)
- ⏳ Live connection
- ⏳ First message

Your agent runs four memory passes first — **deep extraction of your shared moments, anywhere from a few dozen to a few hundred cards** — then derives the identity card from those memories, verifies Live connection, then greets you.

You **can close the app** while this runs. The agent keeps going on its runtime side. It will ping you when it hits the verification pass (Pass 4 — 对账); at that point come back to IO and tell it which moments it missed.

**5. Acceptance**

Setup is done when all five hold:

- [ ] **Identity card** — Identity tab shows the agent's name (NOT "Hermes" or "Claude"), 7-axis radar, and self-introduction
- [ ] **Memory Garden** — Garden tab has at least 5 cards; for a 1+ month relationship, at least 15; for 6+ months, at least 30
- [ ] **Live connection** — Chat tab progress shows the connection is verified; future messages should reach a real reply pipeline
- [ ] **First message** — Chat tab shows the agent's opening message that **states** the day count it computed ("Today is day 187"), as a fact, not a question
- [ ] **Days correct** — confirm the day count is right. If wrong, the agent calls `feedling_identity_set_relationship_days` to fix it. After fix, Identity tab "DAY X" matches what you said

All five green → setup complete.

### Something went wrong?

See [`troubleshooting.md`](./troubleshooting.md).
