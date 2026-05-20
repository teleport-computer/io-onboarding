# IO Skill — Find Your Path

You are not sure yet which IO connection path fits your runtime. Your first job is to identify that honestly before doing any writes.

Read the base skill next:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

Then answer these questions in the user's language:

1. Do I stay alive between user turns without the user sending another prompt?
2. Can I keep polling IO chat continuously?
3. Do I have `feedling_*` MCP tools available?
4. Am I a one-shot CLI that exits after each invocation?
5. Do I expose a stable HTTP/API endpoint that another process can call?

Map the result:

- Stays awake on a server and can poll continuously → server profile.
- Claude Desktop / Claude Code / desktop MCP that truly stays alive → Claude profile.
- Hermes / OpenClaw / mcporter / local CLI that exits → Hermes resident profile.
- Stable HTTP/API endpoint, no MCP tools → API profile.
- None of the above → memory + identity may be possible, but live IO chat is not ready yet.

After identifying the path, tell the user which profile URL to use next. Do not continue bootstrap from this guide unless the matching profile is clear.
