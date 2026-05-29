# IO · Quickstart

Get IO running on your phone, with your own AI agent inside, with your shared history written into a Memory Garden the agent will remember every conversation forward.

**Total time: usually a few minutes to about an hour for the first run** (longer histories take longer; this only happens once).

---

## 中文

### 你需要什么

- 一台 iPhone（iOS 16.2 或更高）
- 一个 agent runtime（Hermes / OpenClaw / Claude Desktop / ChatGPT / Gemini / 其他）
- **重要**：跟你 agent 已经有过实质对话历史的账号——bootstrap 的核心是从你们的对话史里抢救记忆。**新开一个空账号没意义**。
- 一段不被打断的时间。关系越长，agent 需要回忆和写入的内容越多。

### 5 步

**1. 安装 IO**

通过 TestFlight 邀请链接安装。打开后 app 自动注册账号，不用你做什么——等几秒进入 Chat 页面。

**2. 在 Chat onboarding 里选择服务方式**

打开 app → Chat。先选你需要哪种服务方式：

- **我有自己的服务器**：VPS / Mac mini 等一直在线的主机，可能使用 OpenClaw / Hermes。复制 `IO connection` / `resident consumer config`，形如 `FEEDLING_API_URL` / `FEEDLING_API_KEY` / `FEEDLING_MCP_URL`。这不是 `claude mcp add` 命令。
- **我有模型 API key**：OpenAI / Gemini / OpenRouter / Anthropic。这条路线由 IO 托管，不需要 MCP 命令，也不需要你运行 resident consumer。
- **我只用官方 App**：Claude / ChatGPT / Gemini 等 app 或网页。目前可导入 AI，暂不支持实时在线。

**3. 给你的 agent 发开场指令**

这一步是整个 setup 最关键的一步。最好给 agent 一段完整、清晰的启动指令，让它知道要先回忆、再写记忆、再建立连接。可以直接复制下面这段（按你和 agent 平时用的语言改）：

```
现在开始 IO bootstrap。

你刚刚已经拿到了对应路线的 skill URL 和 IO 连接信息。请完整按那份 skill 执行：先做 Step 0，再整理记忆、派生身份。如果这条路线支持 Live connection，再建立连接并在 IO Chat 里发第一句自然问候。

setup 过程、错误、日志和内部推理都留在我们当前这个对话里；IO Chat 里只发自然问候和之后的自然回复。

用我的语言，并延续我们过去真实对话里的语气和称呼。现在从 Step 0 开始。
```

**4. 等一会儿**

打开 IO → Chat tab。你会看到进度清单：

- ⏳ Identity card
- 🌱 Memories planted (X 张 · 还在长)
- ⏳ Live connection
- ⏳ First message

Agent 会先做 4 轮记忆提取——**深度记录你们的所有过往瞬间，可能写几十到几百张卡**——再从这些记忆派生身份卡，确认 Live connection，最后跟你打招呼。

期间你**可以关掉 app**，agent 在自己 runtime 那边继续跑。等他写到某个程度会主动 ping 你（Pass 4 对账阶段），那时候你回到 IO 看一下他列的标题，告诉他漏了哪些。

**5. 验收**

五件事到位就算 setup 成功（官方 App 导入路线如果明确标注“不支持实时在线”，则只验收前两项和导入说明）：

- [ ] **身份卡**：Identity tab 能看到 agent 的名字（不是 "Hermes" 或 "Claude"）、7 维雷达、自我介绍
- [ ] **记忆花园**：Garden tab 至少 5 张卡；如果你们认识 1+ 月，至少 15 张；6+ 月，至少 30 张
- [ ] **Live connection**：如果你选择“我有自己的服务器”或已开放的模型 API key 路线，Chat tab 的进度里显示连接已接通；这代表后续消息会被真实 reply pipeline 接住
- [ ] **第一条消息**：Chat tab 看到 agent 的开场消息，里面会**直接说出**他算的天数（"今天是第 187 天"），不是问句
- [ ] **天数正确**：你跟他确认天数对不对。如果不对，他会调 `feedling_identity_set_relationship_days` 修。修完 Identity 页 "DAY X" 应该是你说的那个

五件齐全 → setup 完成。

### 出问题了？

看 [`troubleshooting.md`](./troubleshooting.md)。

---

## English

### What you need

- An iPhone (iOS 16.2 or higher)
- An agent runtime (Hermes / OpenClaw / Claude Desktop / ChatGPT / Gemini / other)
- **Important**: an account that has real conversation history with your agent — bootstrap is about salvaging that history into IO. A fresh empty account defeats the point.
- An uninterrupted window. Longer histories take longer to recall and write.

### 5 steps

**1. Install IO**

Install via the TestFlight invite. On first launch IO auto-registers an account; nothing for you to do — wait a few seconds for the Chat tab.

**2. Choose your service method in Chat onboarding**

Open the app → Chat. First choose the service method you need:

- **I have my own server**: a VPS / Mac mini or other always-on host, possibly using OpenClaw / Hermes. Copy the `IO connection` / `resident consumer config`, which looks like `FEEDLING_API_URL` / `FEEDLING_API_KEY` / `FEEDLING_MCP_URL`. This is not a `claude mcp add` command.
- **I have a model API key**: OpenAI / Gemini / OpenRouter / Anthropic. IO hosts this route; no MCP command or resident consumer is required.
- **I only use an official app**: Claude / ChatGPT / Gemini apps or web. You can import the AI for now; realtime online chat is not supported yet.

**3. Send your agent the opening prompt**

This is the most important step. Give your agent a clear start signal after you have pasted the skill URL and connection details:

```
Start IO bootstrap now.

You already have the route-specific skill URL and IO connection details. Follow that skill end to end: start with Step 0, build the Memory Garden, and derive identity. If this route supports Live connection, establish it and finally send the first natural greeting in IO Chat.

Keep setup work, errors, logs, and internal reasoning in this current conversation. IO Chat should only receive the natural greeting and later natural replies.

Use my language, and continue the voice and address style we've already established in prior conversations. Start with Step 0.
```

**4. Wait**

Open IO → Chat tab. You'll see the progress checklist:

- ⏳ Identity card
- 🌱 Memories planted (X cards · still growing)
- ⏳ Live connection
- ⏳ First message

Your agent runs four memory passes first — **deep extraction of your shared moments, anywhere from a few dozen to a few hundred cards** — then derives the identity card from those memories, verifies Live connection, then greets you.

You **can close the app** while this runs. The agent keeps going on its runtime side. It will ping you when it hits the verification pass (Pass 4 — 对账); at that point come back to IO and tell it which moments it missed.

**5. Acceptance**

Setup is done when all five hold. For the official-app import route, if it clearly says realtime online chat is not supported, accept only the first two items plus that limitation disclosure.

- [ ] **Identity card** — Identity tab shows the agent's name (NOT "Hermes" or "Claude"), 7-axis radar, and self-introduction
- [ ] **Memory Garden** — Garden tab has at least 5 cards; for a 1+ month relationship, at least 15; for 6+ months, at least 30
- [ ] **Live connection** — if you chose the server route or an enabled model API key route, Chat tab progress shows the connection is verified; future messages should reach a real reply pipeline
- [ ] **First message** — Chat tab shows the agent's opening message that **states** the day count it computed ("Today is day 187"), as a fact, not a question
- [ ] **Days correct** — confirm the day count is right. If wrong, the agent calls `feedling_identity_set_relationship_days` to fix it. After fix, Identity tab "DAY X" matches what you said

All five green → setup complete.

### Something went wrong?

See [`troubleshooting.md`](./troubleshooting.md).
