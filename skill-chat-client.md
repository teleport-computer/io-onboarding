# IO Skill — Chat Client

You are connecting from an official AI app, website, or third-party chat
product.

Examples: Claude, ChatGPT, Gemini, Claude Desktop, Cursor, or another product
where the user talks to you through a chat window.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- The user may give you a `claude mcp add feedling --transport sse ...`-style MCP connection command or equivalent MCP server URL if your chat product supports MCP/tools.
- Complete Step 0, the four memory passes, and identity exactly as the base skill requires.
- After each module, call `feedling_onboarding_validate`; if `passing=false`, fix `next_action` before continuing.
- Do not assume a chat product can stay alive in the background.
- Before sending the first IO chat greeting, verify the reply path with `feedling_chat_verify_loop`.
- Only after `passing=true`, send the first greeting with `feedling_chat_post_message`.
- If the chat product cannot keep listening after the user closes the window, sleeps the computer, or ends the session, say that clearly before the first greeting. It may still be able to initialize memory and identity, but it is not a reliable live IO chat owner.

If live chat cannot be owned from this client, this path is import-only for now.
The user needs the server route for reliable realtime IO chat.

## 中文同义规则

- 按 base skill 完成 Step 0、四轮记忆 pass、identity。
- 每个模块后调用 `feedling_onboarding_validate`；如果 `passing=false`，先修 `next_action` 再继续。
- 如果你的聊天产品支持 MCP/tools，用户会给你 `claude mcp add feedling --transport sse ...` 这类 MCP 连接命令，或等价的 MCP server URL。
- 不要默认假设聊天产品能在后台一直活着。
- 只有在你能真实持续接收 IO/Feedling 消息时，才可以成为 Live connection owner。
- 第一条 IO 问候前必须用 `feedling_chat_verify_loop` 验证；只有 `passing=true` 才能发。
- 如果这个聊天产品在用户关窗口、电脑睡眠、session 结束后就不能继续听消息，要在第一条 IO 问候前说清楚：你可以初始化 memory / identity，但不能可靠负责长期聊天。

不能从这个 client 持续接住 live chat 时，这条路线目前只用于导入。用户如果需要可靠实时 IO chat，需要选择“我有自己的服务器”路线。
