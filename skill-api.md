# IO Skill — Model API Key Route

This profile is for users who have a model provider API key, not their own
always-on agent server.

Examples: OpenAI, Gemini, OpenRouter, Anthropic.

This route is hosted by IO. The user does **not** need to install MCP, run a
resident consumer service, expose an HTTP endpoint, or keep a Mac / VPS online.

Read the shared base skill for Memory Garden and identity standards:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- The user supplies a model provider key to IO.
- IO owns the runtime loop for chat and proactive messages.
- The Memory Garden and identity card still use the same quality bar as the
  base skill: no invented memories, no invented day count, and no runtime-label
  persona names.
- There is no `claude mcp add ...` command on this path.
- There is no independent `feedling-chat-resident` service on this path.
- There is no custom webhook or user-hosted HTTP endpoint on this path.
- If a setup screen asks for provider details, collect only provider, model,
  and API key. Do not ask the user to run terminal commands.
- If live chat cannot be enabled because the hosted model runtime is not
  available yet, say that plainly in the setup surface. Do not fake a live
  connection.

## Acceptance

The model API key route is ready only when all of these are true:

- Provider key is accepted by IO.
- A test model call succeeds.
- Identity and Memory Garden are initialized from real user-provided or imported
  history.
- IO can send a normal chat message to the hosted runtime and receive a normal
  reply.
- Proactive jobs, if enabled, go through the same hosted runtime and do not
  create a second persona.

## 中文同义规则

这条路径适合“我有模型 API key”的用户，而不是有自己常驻 server 的用户。

例子：OpenAI、Gemini、OpenRouter、Anthropic。

这条路线由 IO 托管。用户不需要安装 MCP，不需要跑 resident consumer
service，不需要暴露 HTTP endpoint，也不需要一直开着 Mac / VPS。

共同底座仍然读这里：

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

规则：

- 用户把模型 provider key 提供给 IO。
- IO 负责 chat 和 proactive message 的 runtime loop。
- Memory Garden 和 identity 的质量标准仍然和 base skill 一样：不能编造记忆，
  不能编造在一起的天数，不能把 runtime label 当作人格名。
- 这条路径没有 `claude mcp add ...`。
- 这条路径没有独立 `feedling-chat-resident` service。
- 这条路径没有用户自建 webhook 或 HTTP endpoint。
- 如果 setup 页面要求 provider 信息，只收 provider、model、API key。
  不要让用户跑 terminal command。
- 如果 hosted model runtime 还没开放 live chat，就在 setup surface 里直接说清楚。
  不要假装 live connection 已经接通。

验收标准：

- Provider key 被 IO 接受。
- 测试 model call 成功。
- Identity 和 Memory Garden 来自真实导入 / 用户提供的历史。
- IO 能把一条普通 chat message 交给 hosted runtime，并收到自然回复。
- 如果 proactive 开启，它也必须走同一个 hosted runtime，不能创造第二个人格。
