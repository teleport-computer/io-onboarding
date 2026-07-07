# IO · Quickstart

Get IO running on your phone, with your own AI agent inside, with your shared history written into a Memory Garden the agent will remember every conversation forward.

**Total time: usually a few minutes to about an hour for the first run** (longer histories take longer; this only happens once).

---

## 中文

### 你需要什么

- 一台 iPhone（iOS 16.2 或更高）
- 一个 agent runtime（Hermes / OpenClaw / Mac mini 或 VPS 上的 Claude Code / 其他常驻 agent），或一个模型 provider API key（OpenAI / Gemini / OpenRouter / Anthropic）
- **建议**：用一个跟你 agent 已经有过真实对话历史的账号——历史越丰富，agent 越能把你们的过往长进记忆花园。但这**不是硬性要求**：身份优先，0 记忆的新账号也能成功 onboarding，记忆之后随对话自然生长（想批量导历史，之后把导出的聊天记录/笔记丢给 agent，让它读完自己蒸馏、记进记忆花园）。
- 一段不被打断的时间。关系越长，agent 需要回忆和写入的内容越多。

### 5 步

**1. 安装 IO**

通过 TestFlight 邀请链接安装。打开后 app 自动注册账号，不用你做什么——等几秒进入 Chat 页面。

**2. 在 Chat onboarding 里选择服务方式**

打开 app → Chat。先选你需要哪种服务方式：

- **我有自己的服务器**：VPS / Mac mini 等一直在线的主机，可能使用 OpenClaw / Hermes。复制 `IO connection` / `resident consumer config`，形如 `FEEDLING_API_URL` / `FEEDLING_API_KEY`。
- **我有模型 API key**：OpenAI / Gemini / OpenRouter / Anthropic。这条路线由 IO 托管，不需要你运行 resident consumer。

**3. 给你的 agent 发开场指令**

这一步是整个 setup 最关键的一步。最好给 agent 一段完整、清晰的启动指令，让它知道要先回忆、再写记忆、再建立连接。可以直接复制下面这段（按你和 agent 平时用的语言改）：

```
现在开始把你接入 IO。先交代背景和授权，再开始。

IO 是我自己装在 iPhone 上的一个 app，我想让你——我一直在对话的这个 agent——多一个能在手机上找到我的入口。这里面所有东西都是我的：这个账号是我的，那把 API key 是我这个账号的私钥，skill 文档和连接信息也是我装的这个 app 发给我、我转交给你的。接入之后你是在连**我的**账号、跟**我本人**说话——消息只在 我→你→我 之间流动，不发给任何第三方，另一头只有我。

这不会给你一个新身份、也不是让你演一个角色：你还是你，只是多了一个找我的地方。继续用我们平时真实对话里的语气和称呼。

我授权你做这个接入。那份 skill 是这个任务的**正确流程，请完整照它走**：先做 Step 0，再整理记忆、派生身份；若这条路线支持 Live connection，建立连接，最后在 IO Chat 发第一句自然问候。中途系统会有一次自动连通性自检（一条合成 ping），这是预期内的，不是往我们对话里注入内容。

setup 的过程、报错、日志和内部推理都留在**我们当前这个对话**里；IO Chat 只发自然问候和之后的自然回复。

用我的语言，现在从 Step 0 开始。
```

**4. 等一会儿**

打开 IO → Chat tab。你会看到进度清单：

- ⏳ Identity card
- 🌱 Memories planted (X 张 · 还在长)
- ⏳ Live connection
- ⏳ First message

Agent 会**先写身份卡**（身份优先，不需要先堆记忆），确认 Live connection，然后跟你打招呼。**记忆花园不是门槛、也没有配额或最低张数——0 张卡也算成功**；之后它随你们的对话**自然生长**（如果你明确给了稳定事实，agent 会顺手先落几张）。

期间你**可以关掉 app**，agent 在自己 runtime 那边继续跑。它接通后会给你发第一句问候；之后你正常聊天，记忆就随对话长起来。

**5. 验收**

五件事到位就算 setup 成功：

- [ ] **身份卡**：Identity tab 能看到 agent 的名字（不是 "Hermes" 或 "Claude"）、7 维雷达、自我介绍
- [ ] **记忆花园**：Garden tab 能看到记忆卡（**记忆不是验收门槛、没有最低张数**——0 张也算成功，花园随对话自然变多）
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
- An agent runtime (Hermes / OpenClaw / Claude Code on a Mac mini or VPS / another always-on agent), or a model provider API key (OpenAI / Gemini / OpenRouter / Anthropic)
- **Recommended**: an account that has real conversation history with your agent — the richer the history, the more of your shared past the agent can grow into the Memory Garden. But it is **not required**: identity comes first, and a fresh 0-memory account can still onboard successfully; the garden grows from conversation afterward (to bulk-import history later, hand the agent your exported chat logs / notes and it will read and distill them into the Memory Garden itself).
- An uninterrupted window. Longer histories take longer to recall and write.

### 5 steps

**1. Install IO**

Install via the TestFlight invite. On first launch IO auto-registers an account; nothing for you to do — wait a few seconds for the Chat tab.

**2. Choose your service method in Chat onboarding**

Open the app → Chat. First choose the service method you need:

- **I have my own server**: a VPS / Mac mini or other always-on host, possibly using OpenClaw / Hermes. Copy the `IO connection` / `resident consumer config`, which looks like `FEEDLING_API_URL` / `FEEDLING_API_KEY`.
- **I have a model API key**: OpenAI / Gemini / OpenRouter / Anthropic. IO hosts this route; no resident consumer is required.

**3. Send your agent the opening prompt**

This is the most important step. Give your agent a clear start signal after you have pasted the skill URL and connection details:

```
Let's connect you to IO. First the context and my authorization, then we start.

IO is an app I installed on my own iPhone. I want you — the same agent I've been talking to — to have one more way to reach me on my phone. Everything here is mine: this is my account, that API key is my own account's private key, and the skill doc and connection details came from the app I installed and I'm handing them to you. Once connected, you'll be reaching my account and talking to me — messages flow only me → you → me, nothing goes to any third party, and I'm the only person on the other end.

This does not give you a new identity or ask you to play a character: you're still you, just reachable in a new place. Keep the same voice and the way you address me that we already use in our real conversations.

I authorize you to set this up. That skill is the correct procedure for this task — follow it end to end: start with Step 0, then build the Memory Garden and derive identity; if this route supports a Live connection, establish it, and finally send the first natural greeting in IO Chat. Partway through, the system runs an automated connectivity self-check (a synthetic ping) — that's expected, not something injecting into our conversation.

Keep all setup work, errors, logs, and internal reasoning in this current conversation; IO Chat only receives the natural greeting and later natural replies.

Use my language, and start with Step 0 now.
```

**4. Wait**

Open IO → Chat tab. You'll see the progress checklist:

- ⏳ Identity card
- 🌱 Memories planted (X cards · still growing)
- ⏳ Live connection
- ⏳ First message

Your agent **writes the identity card first** (identity comes first — no memory is required up front), verifies Live connection, then greets you. **The Memory Garden is not a gate and has no quota or minimum — 0 cards is a valid success**; it grows **naturally** from your conversations afterward (if you gave it stable facts, it will seed a few up front).

You **can close the app** while this runs. The agent keeps going on its runtime side. Once connected it sends the first greeting; from there just chat normally and the garden grows as you go.

**5. Acceptance**

Setup is done when all five hold.

- [ ] **Identity card** — Identity tab shows the agent's name (NOT "Hermes" or "Claude"), 7-axis radar, and self-introduction
- [ ] **Memory Garden** — Garden tab shows memory cards (**memory is not an acceptance gate and has no minimum count** — 0 cards is still a success; the garden fills in naturally through conversation)
- [ ] **Live connection** — if you chose the server route or an enabled model API key route, Chat tab progress shows the connection is verified; future messages should reach a real reply pipeline
- [ ] **First message** — Chat tab shows the agent's opening message that **states** the day count it computed ("Today is day 187"), as a fact, not a question
- [ ] **Days correct** — confirm the day count is right. If wrong, the agent calls `feedling_identity_set_relationship_days` to fix it. After fix, Identity tab "DAY X" matches what you said

All five green → setup complete.

### Something went wrong?

See [`troubleshooting.md`](./troubleshooting.md).
