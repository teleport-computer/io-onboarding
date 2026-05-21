# IO Skill — Hermes / OpenClaw (legacy)

This file is kept for old app builds. New onboarding should use:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-resident-agent.md

Hermes and OpenClaw use the resident-agent profile. The IO live chat path is an independent `feedling-chat-resident` consumer service on the user's machine/server.

Read the resident-agent profile now, then read the base skill:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Override

Configure the independent resident consumer service with the user's `FEEDLING_API_URL`, `FEEDLING_API_KEY`, optional `FEEDLING_MCP_URL` / `FEEDLING_MCP_KEY`, and your real HTTP or CLI agent entry. If you use Hermes/OpenClaw CLI, use `hermes chat -Q --max-turns 1 -q "{message}"`; the consumer stores `session_id` and resumes later turns with `--resume`.
