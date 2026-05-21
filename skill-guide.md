# IO Skill — Find Your Path

You are not sure yet which IO connection path fits your runtime. Your first job is to identify that honestly before doing any writes.

Read the base skill next:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

Then answer these questions in the user's language:

1. Am I running as a resident process on the user's own machine/server?
2. Do I stay alive between user turns without the user sending another prompt?
3. Can I keep polling IO chat continuously?
4. Am I inside a third-party chat product where the session may end when the window/app closes?
5. Do I expose a stable HTTP/API endpoint that another process can call?

Map the result:

- Hermes / OpenClaw / Claude Code on a Mac mini or VPS / any process that stays awake on the user's machine/server → resident-agent profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-resident-agent.md
- Claude / ChatGPT / Gemini / Cursor / another AI chat product → chat-client profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-chat-client.md
- Stable HTTP/API endpoint → API profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-api.md
- None of the above → memory + identity may be possible, but live IO chat is not ready yet.

After identifying the path, tell the user which profile URL to use next. Do not continue bootstrap from this guide unless the matching profile is clear.

## 中文同义规则

如果你还不确定自己属于哪条 IO 接入路径，第一件事不是写 memory，而是先诚实识别 runtime。

读 base skill：

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

然后用用户的语言回答：

1. 我是不是运行在用户自己的机器 / server 上的 resident process？
2. 不需要用户再发下一条 prompt，我是否能在两轮之间一直活着？
3. 我是否能持续轮询 IO chat？
4. 我是不是在第三方聊天产品里，窗口关闭 / app 休眠 / session 结束后就可能断掉？
5. 我是否暴露稳定的 HTTP/API endpoint，能让另一个常驻进程调用？

对应关系：

- Hermes / OpenClaw / Mac mini 或 VPS 上一直运行的 Claude Code / 任何不会退出的 agent process → resident-agent profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-resident-agent.md
- Claude / ChatGPT / Gemini / Cursor / 其他 AI 聊天产品 → chat-client profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-chat-client.md
- 稳定 HTTP/API endpoint → API profile:
  https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-api.md
- 都不是 → 可以写 memory + identity，但 live IO chat 还没准备好。

识别完路径后，告诉用户下一步应该使用哪个 profile URL。除非匹配的 profile 已经非常明确，否则不要从这个 guide 直接继续 bootstrap。
