# IO Skill — API

You are connecting through a custom HTTP/API backend rather than direct MCP tools.

This profile fixes your connection path. Read the base skill next, but use its Appendix A HTTP equivalents whenever a `feedling_*` MCP tool is named:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- Your backend must expose a stable endpoint that a resident process can call for replies.
- Complete the same Step 0, memory, and identity standards as the base skill.
- Use the HTTP equivalents for writes and verification.
- Pair the API backend with a resident process that polls IO and POSTs user messages to your endpoint.
- Do not claim live chat until the resident path passes `feedling_chat_verify_loop` or the equivalent live chat verification.
- Only after the connection verifies, send the first IO greeting.

If you only have a one-shot script and no stable API endpoint, use the Hermes / resident bridge profile instead.
