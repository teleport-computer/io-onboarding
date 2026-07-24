# IO Skill — Hermes / OpenClaw (legacy)

This file is kept for old app builds. New onboarding should use:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/test/skill-resident-agent.md

Hermes and OpenClaw use the resident-agent profile. The IO live chat path is an independent `feedling-chat-resident` consumer service on the user's machine/server.

Read the resident-agent profile now, then read the base skill:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/test/skill.md

## Override

Configure the independent resident consumer service with the user's `FEEDLING_API_URL`, `FEEDLING_API_KEY`, and your real HTTP or CLI agent entry. If you use Hermes/OpenClaw CLI, set `HERMES_HOME` to the same profile used by the real resident agent, then use `hermes chat -Q --source tool --max-turns 60 -q "{message}"`; the consumer stores `session_id` and resumes later turns with `--resume`. Do not wrap `{message}` in a new persona prompt. After each module, call `feedling_onboarding_validate` and fix `next_action` until the server validator passes.
