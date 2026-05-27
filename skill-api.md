# IO Skill — API

You are connecting through a custom HTTP/API backend rather than direct MCP tools.

This profile fixes your connection path. Read the base skill next, but use its Appendix A HTTP equivalents whenever a `feedling_*` MCP tool is named:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- Your backend must expose a stable endpoint that the independent IO resident consumer service can call for replies.
- Complete the same Step 0, memory, and identity standards as the base skill.
- Use the HTTP equivalents for writes and verification.
- After each module, call the onboarding validator HTTP equivalent and fix `next_action` before continuing.
- Pair the API backend with the resident consumer service that polls IO and POSTs user messages to your endpoint.
- Do not claim live chat until the resident path passes `feedling_chat_verify_loop` or the equivalent live chat verification.
- Only after the connection verifies, send the first IO greeting.

If you only have a one-shot script and no stable API endpoint, use the resident-agent profile and configure the resident consumer with `AGENT_MODE=cli`.

## 中文同义规则

你是通过自定义 HTTP/API backend 接入，而不是直接使用 MCP tools。

这条路径只适合有稳定 API endpoint 的后端：IO resident consumer service 能把 IO/Feedling 收到的用户消息 POST 给你，再把你的回复发回 IO。

- memory / identity 的质量标准和 base skill 完全一样。
- base skill 里出现 `feedling_*` MCP tool 时，改用 Appendix A 的 HTTP 等价接口。
- 每个模块后调用 onboarding validator 的 HTTP 等价接口；如果 `passing=false`，先修 `next_action` 再继续。
- 必须配合一个 IO resident consumer service 负责轮询 IO 并调用你的 API。
- resident path 通过 `feedling_chat_verify_loop` 或等价 live chat verification 之前，不要声称 Live connection 已经接通。
- 连接验证通过后，才能发第一条 IO 问候。

如果你只是一个每次调用后就退出的脚本，没有稳定 API endpoint，不要用 API profile；改用 resident-agent profile，并让 resident consumer 用 `AGENT_MODE=cli` 调用你。
