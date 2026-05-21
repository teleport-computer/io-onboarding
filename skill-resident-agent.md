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

## Resident gateway readiness

For Hermes / OpenClaw / any gateway that already hosts Telegram, WeChat, Feishu, or similar resident channels, IO must be a native gateway channel. Do **not** ask the user to repair routing in the IO chat.

Before Step 6, verify all of this from the gateway side:

- The platform registry includes `feedling`.
- The adapter factory can create `FeedlingAdapter`.
- The gateway's toolset / platform routing registry includes `feedling` so no `KeyError: 'feedling'` can happen after the first message.
- Runtime config enables the channel, e.g. `FEEDLING_ENABLED=true`.
- `FEEDLING_API_URL` points to the backend API: `https://api.feedling.app`.
  - Do **not** use `https://mcp.feedling.app` for `/v1/chat/poll`; that host is the MCP SSE surface.
- `FEEDLING_API_KEY` is the current onboarding key.
- Startup logs prove the adapter is alive:
  - `Feedling adapter connecting`
  - `Feedling polling started api_url=https://api.feedling.app ...`
  - `Feedling polling request url=https://api.feedling.app/v1/chat/poll`
- Incoming Feedling messages go through the gateway's normal resident brain path, not a CLI subprocess.
  - For Hermes/OpenClaw this means the same path used by other resident channels, e.g. gateway message handler → `AIAgent.run_conversation` → adapter send.
- Replies are posted to `/v1/chat/response`.

If any item is missing, stop onboarding before Step 6 and report the missing gateway capability in the external runtime. Do not open IO Chat with a partial connection.

## User-visible chat rules

The IO chat must not expose gateway setup.

Never send these into IO Chat:

- `/sethome` instructions or "No home channel is set" prompts.
- Gateway routing/config/deployment status.
- `KeyError`, traceback, exception fallback text, or debug logs.
- Internal reasoning text such as "I need to respond..." or fenced reasoning blocks.
- "I fixed the adapter" / "please test now" engineering messages.

If the gateway has a home-channel concept, Feedling must either become the home channel silently for this user or opt out silently. The user should not have to type `/sethome` during onboarding.

The first IO-visible message must be the Step 6 natural greeting from the base skill. After that, the final onboarding proof is one normal user message in IO Chat followed by one natural agent reply.
