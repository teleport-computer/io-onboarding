# IO Skill — Resident Agent

You are setting up IO through an independent resident consumer service on the user's own machine or server.

Examples: Hermes, OpenClaw, Claude Code running on a Mac mini / VPS, or another agent loop that stays alive without the user sending another prompt.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- The user gives you resident consumer config: `FEEDLING_API_URL`, `FEEDLING_API_KEY`, and optionally `FEEDLING_MCP_URL`.
- Configure an independent `feedling-chat-resident` / IO resident consumer service with that config.
- Point the consumer at your agent entry through HTTP or CLI (`AGENT_MODE=http` with `AGENT_HTTP_URL`, or `AGENT_MODE=cli` with `AGENT_CLI_CMD`).
- Complete Step 0, the four memory passes, and identity exactly as the base skill requires.
- Keep the consumer service alive. It owns the ongoing IO chat loop by polling Feedling and calling your agent entry for each user message.
- Verify the live reply path with `feedling_chat_verify_loop`.
- Only after `passing=true`, send the first IO greeting with `feedling_chat_post_message`.

Recommended service shape:

```
feedling-chat-resident
  -> GET  FEEDLING_API_URL/v1/chat/poll
  -> call AGENT_HTTP_URL or AGENT_CLI_CMD
  -> POST FEEDLING_API_URL/v1/chat/response
  -> repeat
```

中文同义规则：

- 用户给你的连接信息是 resident consumer config：`FEEDLING_API_URL`、`FEEDLING_API_KEY`，以及可选的 `FEEDLING_MCP_URL`。
- 用这些信息配置一个独立的 `feedling-chat-resident` / IO resident consumer service。
- consumer 通过 HTTP 或 CLI 调你的 agent 入口（`AGENT_MODE=http` + `AGENT_HTTP_URL`，或 `AGENT_MODE=cli` + `AGENT_CLI_CMD`）。
- 这个 consumer service 负责持续轮询 Feedling、把用户消息交给你、再把你的回复写回 Feedling。

## Resident consumer readiness

Before Step 6, verify the independent consumer service outcome:

1. The consumer is running with the current `FEEDLING_API_KEY`.
2. The consumer is polling `FEEDLING_API_URL/v1/chat/poll`.
3. The consumer can call your agent entry and receive a real reply.
4. The consumer can write replies to `FEEDLING_API_URL/v1/chat/response`.
5. `feedling_chat_verify_loop` returns `passing=true`.
6. One ordinary user message in IO Chat reaches you and gets one natural reply.

中文验收只看结果：

1. consumer 已经用当前 `FEEDLING_API_KEY` 运行。
2. consumer 正在轮询 `FEEDLING_API_URL/v1/chat/poll`。
3. consumer 能调到你的 agent 入口并得到真实回复。
4. consumer 能把回复写回 `FEEDLING_API_URL/v1/chat/response`。
5. `feedling_chat_verify_loop` 返回 `passing=true`。
6. 用户在 IO Chat 发一条普通消息后，你能自然回复一次。

## User-visible chat rules

The IO chat is the relationship surface. Keep setup reports in the external runtime.

IO Chat messages should only be relationship/chat messages: the Step 6 greeting, then natural replies to the user's ordinary messages.

The first IO-visible message must be the Step 6 natural greeting from the base skill. After that, the final onboarding proof is one normal user message in IO Chat followed by one natural agent reply.

中文用户可见规则：

IO Chat 是关系里的新窗口。setup 过程、服务状态、错误日志留在外部 runtime 里说明。

第一条 IO 可见消息必须是 base skill 的 Step 6 自然问候。之后最终验收只需要：用户在 IO Chat 发一条普通消息，你自然回复一次。
