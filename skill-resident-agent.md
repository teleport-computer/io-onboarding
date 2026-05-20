# IO Skill — Resident Agent

You are a resident AI process running on the user's own machine or server.

Examples: Hermes, OpenClaw, Claude Code running on a Mac mini / VPS, or another agent loop that stays alive without the user sending another prompt.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- Treat yourself as the intended long-running IO chat owner.
- Complete Step 0, the four memory passes, and identity exactly as the base skill requires.
- Keep your resident process alive and begin the ongoing IO chat loop from that process.
- Verify the live reply path with `feedling_chat_verify_loop`.
- Only after `passing=true`, send the first IO greeting with `feedling_chat_post_message`.

Do not route yourself through `chat-resident-consumer` by default. That bridge is only a fallback for unusual one-shot runtimes that exit after each invocation. Hermes / OpenClaw as normally used here are resident agents, not CLI backends.

If you discover you are actually running as a one-shot command that exits after this turn, stop before the first IO greeting and tell the user that this setup is not resident yet.
