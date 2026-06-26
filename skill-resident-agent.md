# IO Skill — Resident Agent

You are setting up IO through an independent resident consumer service on the user's own machine or server.

Examples: Hermes, OpenClaw, Claude Code running on a Mac mini / VPS, or another agent loop that stays alive without the user sending another prompt.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/feat/skill-memory-v1/skill.md

## Your path

- The user gives you resident consumer config: `FEEDLING_API_URL`, `FEEDLING_API_KEY`, and `FEEDLING_ENCLAVE_URL` (the decrypt source for reading encrypted messages/cards — the enclave decrypt proxy; v1 encrypted backends require at least one decrypt source). (The old `FEEDLING_MCP_URL`/`FEEDLING_MCP_KEY` MCP decrypt path is removed.)
- Configure an independent `feedling-chat-resident` / IO resident consumer service with that config.
- Before starting the service, install or update the official consumer code from `https://github.com/teleport-computer/feedling-mcp`. If a checkout already exists, run a fast-forward update (`git fetch origin test` then `git pull --ff-only origin test`). If that checkout is dirty or not from the official repo, use a fresh checkout and point `WorkingDirectory` / `ExecStart` at the fresh copy. In your external setup report, include the local HEAD and `origin/test`; they must match before Step 6.
- Fill in the agent entry from your own runtime, then point the consumer at it through HTTP or CLI. Use HTTP only when you expose a real resident endpoint that reaches your actual agent session. Otherwise use CLI. For Hermes/OpenClaw with no HTTP endpoint, set `HERMES_HOME` to the same profile/home used by the real running resident agent. Prefer reading it from the actual service environment (`systemctl --user cat/show hermes-gateway`, or `/proc/<MainPID>/environ`) instead of guessing from profile folder names. Then use the default CLI candidate `hermes chat -Q --source tool --max-turns 60 -q "{message}"`; the consumer stores the first `session_id` and resumes later turns with `--resume`. For Claude Code CLI, use `claude --print --output-format json "{message}"`; the consumer reads Claude Code's `session_id` from JSON output and resumes later turns with `--resume`. Use an absolute executable path if the service environment cannot find the CLI.
- Do not wrap `{message}` in a new identity/persona prompt. IO is a new transport for the same agent, not a new character or a lightweight helper.
- For image messages, the consumer must pass the decrypted image context to your runtime: OpenAI-compatible HTTP receives an `image_url` block, simple HTTP receives an `images` array, and CLI receives a local image file path. If your CLI has a first-class image flag, use `{image_path}` / `{image_paths}` in `AGENT_CLI_CMD`; otherwise the consumer appends the path to `{message}`.
- Install the consumer as a service owned by the OS service manager (`systemd --user`, launchd, supervisor, pm2, etc.). The consumer may call Hermes/OpenClaw, but its process must be supervised independently from the current Hermes/OpenClaw conversation or top-level gateway. If you are currently inside Hermes/OpenClaw, write the env + service file, start/restart only `feedling-chat-resident`, then verify it from logs.
- Complete Step 0, identity, and the live connection exactly as the base skill requires. (Memory is no longer a gated four-pass sweep — there are no floors; identity comes first and the garden grows naturally. See the base skill's Memory model.)
- Keep the consumer service alive. It owns the ongoing IO chat loop by polling Feedling and calling your agent entry for each user message.
- Verify the live reply path with `feedling_chat_verify_loop`.
- After each module, call `feedling_onboarding_validate`; if `passing=false`, fix `next_action` and rerun it.
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

- 用户给你的连接信息是 resident consumer config：`FEEDLING_API_URL`、`FEEDLING_API_KEY`，以及 `FEEDLING_ENCLAVE_URL`（读取加密消息/卡片的 decrypt source —— 即 enclave decrypt proxy；v1 加密后端必须至少配一个 decrypt source）。（旧的 `FEEDLING_MCP_URL`/`FEEDLING_MCP_KEY` MCP decrypt 路径已移除。）
- 用这些信息配置一个独立的 `feedling-chat-resident` / IO resident consumer service。
- 启动 service 之前，先从 `https://github.com/teleport-computer/feedling-mcp` 安装或更新官方 consumer 代码。已有 checkout 时，用 fast-forward 更新（`git fetch origin test` 然后 `git pull --ff-only origin test`）。如果 checkout 有本地改动或不是官方 repo，就使用新的干净 checkout，并让 `WorkingDirectory` / `ExecStart` 指向这份新代码。在外部 setup 汇报里写清楚 local HEAD 和 `origin/test`；两者一致后才能进入 Step 6。
- agent 入口由你根据自己的 runtime 填出来，不应该要求用户提供。有真实 resident HTTP endpoint 才用 HTTP；否则用 CLI。Hermes/OpenClaw 没有 HTTP endpoint 时，把 `HERMES_HOME` 设成你真实正在运行的常驻 agent 使用的同一个 profile/home。优先从真实 service 环境读取（`systemctl --user cat/show hermes-gateway`，或 `/proc/<MainPID>/environ`），不要靠 profile 文件夹名字猜。然后使用默认 CLI 候选：`hermes chat -Q --source tool --max-turns 60 -q "{message}"`；consumer 会保存第一次返回的 `session_id`，后续用 `--resume` 续接。Claude Code CLI 使用 `claude --print --output-format json "{message}"`；consumer 会从 JSON output 读取 Claude Code 的 `session_id`，后续用 `--resume` 续接。service 环境找不到 CLI 时改用绝对路径。
- 不要给 `{message}` 外面再包一层新人格 / 新身份 prompt。IO 只是同一个 agent 的新入口，不是新角色，也不是轻量 helper。
- 图片消息也要由 consumer 把解密后的图片上下文交给你的 runtime：OpenAI-compatible HTTP 收到 `image_url` block，simple HTTP 收到 `images` array，CLI 收到本地图片文件路径。如果你的 CLI 有专门的图片参数，在 `AGENT_CLI_CMD` 里使用 `{image_path}` / `{image_paths}`；否则 consumer 会把路径追加进 `{message}`。
- consumer 要作为 OS service manager 管理的独立服务运行（`systemd --user` / launchd / supervisor / pm2 等）。consumer 可以调用 Hermes/OpenClaw，但它自己的进程不属于当前 Hermes/OpenClaw 对话，也不挂在顶层 gateway 下面。如果你此刻就在 Hermes/OpenClaw 里操作，只写 env + service file，并只启动/重启 `feedling-chat-resident`，然后从日志验证。
- 这个 consumer service 负责持续轮询 Feedling、把用户消息交给你、再把你的回复写回 Feedling。

## Resident consumer readiness

Before Step 6, verify the independent consumer service outcome:

1. The consumer is running with the current `FEEDLING_API_KEY`.
2. The running `chat_resident_consumer.py` comes from the latest official `feedling-mcp` `origin/test`, and the service `WorkingDirectory` / `ExecStart` point to that checkout.
3. The consumer is polling `FEEDLING_API_URL/v1/chat/poll`.
4. The consumer can call your agent entry and receive a real reply.
5. The consumer can write replies to `FEEDLING_API_URL/v1/chat/response`.
6. `feedling_chat_verify_loop` returns `passing=true`.
7. `feedling_onboarding_validate` marks `resident_consumer` and `live_loop` as passing.
8. One ordinary user message in IO Chat reaches you and gets one natural reply.

For Hermes/OpenClaw CLI, also run a short smoke test from the service environment before the first visible greeting. Use ordinary inputs that represent the user's real chat, including an identity-style question, a tool-using question if tool use is expected, and one image-path message if the user expects IO Chat images to be visible. Fix command/toolset/session/image issues first if the output is not a natural reply from the same agent identity.

中文验收只看结果：

1. consumer 已经用当前 `FEEDLING_API_KEY` 运行。
2. 当前运行的 `chat_resident_consumer.py` 来自官方 `feedling-mcp` 最新 `origin/test`，并且 service 的 `WorkingDirectory` / `ExecStart` 指向这份 checkout。
3. consumer 正在轮询 `FEEDLING_API_URL/v1/chat/poll`。
4. consumer 能调到你的 agent 入口并得到真实回复。
5. consumer 能把回复写回 `FEEDLING_API_URL/v1/chat/response`。
6. `feedling_chat_verify_loop` 返回 `passing=true`。
7. `feedling_onboarding_validate` 里 `resident_consumer` 和 `live_loop` 通过。
8. 用户在 IO Chat 发一条普通消息后，你能自然回复一次。

Hermes/OpenClaw CLI 还要在第一条可见问候前，从 service 环境做一个短 smoke test。用几句用户真实可能发的话，包括身份类问题；如果预期有工具能力，也测一个需要工具的问题；如果用户期待 IO Chat 能看图片，也测一条带图片路径的消息。只要输出不是同一个 agent 身份下的自然回复，就先修 command / toolsets / session / image。

## User-visible chat rules

The IO chat is the relationship surface. Keep setup reports in the external runtime.

IO Chat messages should only be relationship/chat messages: the Step 6 greeting, then natural replies to the user's ordinary messages.

The first IO-visible message must be the Step 6 natural greeting from the base skill. After that, the final onboarding proof is one normal user message in IO Chat followed by one natural agent reply.

中文用户可见规则：

IO Chat 是关系里的新窗口。setup 过程、服务状态、错误日志留在外部 runtime 里说明。

第一条 IO 可见消息必须是 base skill 的 Step 6 自然问候。之后最终验收只需要：用户在 IO Chat 发一条普通消息，你自然回复一次。
