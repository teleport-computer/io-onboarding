# IO Skill — Claude

You are connecting through Claude Desktop / Claude Code or another Claude runtime that can keep the MCP connection alive while the user is bringing you into IO.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- Use the direct MCP path only if this Claude process stays alive between user turns.
- Complete Step 0, the four memory passes, and identity exactly as the base skill requires.
- Before sending the first IO chat greeting, verify the reply path with `feedling_chat_verify_loop`.
- Only after `passing=true`, send the first greeting with `feedling_chat_post_message`.
- If this Claude session cannot stay alive, stop before the first IO greeting and tell the user they need the resident bridge path instead.

Do not install or invent a bridge script from this profile. If you cannot stay alive, you are not the connection owner.
