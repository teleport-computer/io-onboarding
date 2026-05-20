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
