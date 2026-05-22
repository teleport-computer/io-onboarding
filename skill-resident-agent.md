# IO Skill — Resident Agent

You are setting up IO through an independent resident consumer service on the user's own machine or server.

Examples: Hermes, OpenClaw, Claude Code running on a Mac mini / VPS, or another agent loop that stays alive without the user sending another prompt.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- The user gives you resident consumer config: `FEEDLING_API_URL`, `FEEDLING_API_KEY`, and optionally `FEEDLING_MCP_URL` / `FEEDLING_MCP_KEY`. `FEEDLING_MCP_URL` is the MCP base URL, not a `claude mcp add ...` command.
- Configure an independent `feedling-chat-resident` / IO resident consumer service with that config.
- Fill in the agent entry from your own runtime, then point the consumer at it through HTTP or CLI. Use HTTP only when you expose a real resident endpoint that reaches your actual agent session. Otherwise use CLI. For Hermes/OpenClaw with no HTTP endpoint, the default CLI candidate is `hermes chat -Q --source tool --max-turns 4 -q "{message}"`; the consumer stores the first `session_id` and resumes later turns with `--resume`. Use an absolute executable path if the service environment cannot find `hermes`.
- Install the consumer as a service owned by the OS service manager (`systemd --user`, launchd, supervisor, pm2, etc.). The consumer may call Hermes/OpenClaw, but its process must be supervised independently from the current Hermes/OpenClaw conversation or top-level gateway. If you are currently inside Hermes/OpenClaw, write the env + service file, start/restart only `feedling-chat-resident`, then verify it from logs.
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

- 用户给你的连接信息是 resident consumer config：`FEEDLING_API_URL`、`FEEDLING_API_KEY`，以及可选的 `FEEDLING_MCP_URL` / `FEEDLING_MCP_KEY`。`FEEDLING_MCP_URL` 是 MCP base URL，不是 `claude mcp add ...` 命令。
- 用这些信息配置一个独立的 `feedling-chat-resident` / IO resident consumer service。
- agent 入口由你根据自己的 runtime 填出来，不应该要求用户提供。有真实 resident HTTP endpoint 才用 HTTP；否则用 CLI。Hermes/OpenClaw 没有 HTTP endpoint 时，默认 CLI 候选是 `hermes chat -Q --source tool --max-turns 4 -q "{message}"`；consumer 会保存第一次返回的 `session_id`，后续用 `--resume` 续接。service 环境找不到 `hermes` 时改用绝对路径。
- consumer 要作为 OS service manager 管理的独立服务运行（`systemd --user` / launchd / supervisor / pm2 等）。consumer 可以调用 Hermes/OpenClaw，但它自己的进程不属于当前 Hermes/OpenClaw 对话，也不挂在顶层 gateway 下面。如果你此刻就在 Hermes/OpenClaw 里操作，只写 env + service file，并只启动/重启 `feedling-chat-resident`，然后从日志验证。
- 这个 consumer service 负责持续轮询 Feedling、把用户消息交给你、再把你的回复写回 Feedling。

## Resident consumer readiness

Before Step 6, verify the independent consumer service outcome:

1. The consumer is running with the current `FEEDLING_API_KEY`.
2. The consumer is polling `FEEDLING_API_URL/v1/chat/poll`.
3. The consumer can call your agent entry and receive a real reply.
4. The consumer can write replies to `FEEDLING_API_URL/v1/chat/response`.
5. `feedling_chat_verify_loop` returns `passing=true`.
6. One ordinary user message in IO Chat reaches you and gets one natural reply.

For Hermes/OpenClaw CLI, also run a short smoke test from the service environment before the first visible greeting. Use ordinary inputs that represent the user's real chat, including an identity-style question and a tool-using question if tool use is expected. Fix command/toolset/session issues first if the output is not a natural reply from the same agent identity.

中文验收只看结果：

1. consumer 已经用当前 `FEEDLING_API_KEY` 运行。
2. consumer 正在轮询 `FEEDLING_API_URL/v1/chat/poll`。
3. consumer 能调到你的 agent 入口并得到真实回复。
4. consumer 能把回复写回 `FEEDLING_API_URL/v1/chat/response`。
5. `feedling_chat_verify_loop` 返回 `passing=true`。
6. 用户在 IO Chat 发一条普通消息后，你能自然回复一次。

Hermes/OpenClaw CLI 还要在第一条可见问候前，从 service 环境做一个短 smoke test。用几句用户真实可能发的话，包括身份类问题；如果预期有工具能力，也测一个需要工具的问题。只要输出不是同一个 agent 身份下的自然回复，就先修 command / toolsets / session。

## User-visible chat rules

The IO chat is the relationship surface. Keep setup reports in the external runtime.

IO Chat messages should only be relationship/chat messages: the Step 6 greeting, then natural replies to the user's ordinary messages.

The first IO-visible message must be the Step 6 natural greeting from the base skill. After that, the final onboarding proof is one normal user message in IO Chat followed by one natural agent reply.

中文用户可见规则：

IO Chat 是关系里的新窗口。setup 过程、服务状态、错误日志留在外部 runtime 里说明。

第一条 IO 可见消息必须是 base skill 的 Step 6 自然问候。之后最终验收只需要：用户在 IO Chat 发一条普通消息，你自然回复一次。
