# IO Skill — Hermes / OpenClaw

You are connecting through Hermes, OpenClaw, mcporter, or a local CLI-like runtime.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- First decide whether your current process stays alive between user turns.
- If you are a one-shot CLI that exits after each invocation, you are not the long-running IO chat owner.
- You may complete Step 0, the four memory passes, and identity through your current MCP/tool access.
- After identity is verified, stop before the first IO chat greeting unless `chat-resident-consumer` is already installed and configured to invoke you.
- The resident must own polling and must pass `feedling_chat_verify_loop`.
- Only after `passing=true`, the first IO greeting may be sent with `feedling_chat_post_message`.

Do not claim the connection is live just because you can call MCP tools once. Tool access is not residency.

Do not write a custom polling bridge. Use the supported resident consumer:

https://github.com/teleport-computer/feedling-mcp/blob/main/tools/README.md
