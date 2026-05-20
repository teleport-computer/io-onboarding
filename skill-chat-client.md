# IO Skill — Chat Client

You are connecting from a third-party AI chat product or desktop client.

Examples: Claude Desktop, Claude.ai, ChatGPT, Gemini, Cursor, or another product where the user talks to you through a chat window.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- Complete Step 0, the four memory passes, and identity exactly as the base skill requires.
- Do not assume a chat product can stay alive in the background.
- Before sending the first IO chat greeting, verify the reply path with `feedling_chat_verify_loop`.
- Only after `passing=true`, send the first greeting with `feedling_chat_post_message`.
- If the chat product cannot keep listening after the user closes the window, sleeps the computer, or ends the session, say that clearly before the first greeting. It may still be able to initialize memory and identity, but it is not a reliable live IO chat owner.

Do not invent a polling bridge. If live chat cannot be owned from this client, the user needs a resident agent running on their own machine/server.
