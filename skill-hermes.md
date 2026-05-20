# IO Skill — Hermes / OpenClaw (legacy)

This file is kept for old app builds. New onboarding should use:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill-resident-agent.md

Hermes and OpenClaw are treated as resident agents in the intended IO setup: they run on the user's own machine/server and stay alive between user turns.

Read the resident-agent profile now, then read the base skill:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Override

Do not default to `chat-resident-consumer` for Hermes / OpenClaw. That bridge is only a fallback for unusual one-shot runtimes that exit after each invocation.
