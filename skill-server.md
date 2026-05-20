# IO Skill — Server

You are already running from a server or hosted process that can stay awake without the user keeping a local app, tab, or CLI turn open.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- You are the preferred connection owner if your process can poll IO continuously and post replies back.
- Complete Step 0, the four memory passes, and identity exactly as the base skill requires.
- Start the ongoing chat loop from the resident server process.
- Verify it with `feedling_chat_verify_loop`.
- Only after `passing=true`, send the first IO greeting with `feedling_chat_post_message`.

If you cannot keep a resident process alive, do not use this profile. Tell the user which profile fits instead.
