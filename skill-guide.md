# IO Skill — Find Your Path

You are selecting which IO connection path fits this runtime. Your first job is
to identify the route honestly before doing any writes.

Read the base skill next:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

Then answer these questions in the user's language:

1. Am I able to run an independent IO resident consumer service on the user's own machine/server?
2. Do I stay alive between user turns without the user sending another prompt?
3. Can that resident consumer keep polling IO chat continuously?
4. Does the user only have a model provider API key (OpenAI / Gemini / OpenRouter / Anthropic) and no always-on agent runtime?
5. Am I inside an official AI app or chat product where the session may end when the window/app closes?

Map the result:

- Hermes / OpenClaw / Claude Code on a Mac mini or VPS / any process with a stable HTTP or CLI agent entry on the user's machine/server → resident-agent profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-resident-agent.md
- Model provider API key only → model API key profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-api.md
- A plain chat product whose session ends when the window/app closes (Claude.ai / ChatGPT / Gemini app, etc.) → no live IO route yet. Suggest the resident-agent or model-API-key route instead.

After identifying the path, tell the user which profile URL to use next. Do not continue bootstrap from this guide unless the matching profile is clear.

## 中文同义规则

如果你正在判断自己属于哪条 IO 接入路径，第一件事不是写 memory，而是先诚实识别 runtime。

读 base skill：

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

然后用用户的语言回答：

1. 我是否能在用户自己的机器 / server 上运行一个独立的 IO resident consumer service？
2. 不需要用户再发下一条 prompt，我是否能在两轮之间一直活着？
3. 这个 resident consumer 是否能持续轮询 IO chat？
4. 用户是否只有模型 provider API key（OpenAI / Gemini / OpenRouter / Anthropic），但没有一直在线的 agent runtime？
5. 我是不是在官方 AI app 或聊天产品里，窗口关闭 / app 休眠 / session 结束后就可能断掉？

对应关系：

- Hermes / OpenClaw / Mac mini 或 VPS 上的 Claude Code / 任何在用户机器或 server 上有稳定 HTTP 或 CLI agent 入口的 runtime → resident-agent profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-resident-agent.md
- 只有模型 provider API key → model API key profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-api.md
- 窗口/app 关闭就断的纯聊天产品（Claude.ai / ChatGPT / Gemini app 等）→ 目前没有 live IO 路线，建议改用 resident-agent 或 model-API-key 路线。

识别完路径后，告诉用户下一步应该使用哪个 profile URL。除非匹配的 profile 已经非常明确，否则不要从这个 guide 直接继续 bootstrap。
