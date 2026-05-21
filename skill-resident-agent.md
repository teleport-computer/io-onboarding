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

中文同义规则：如果你是 Hermes / OpenClaw / 已经承载 Telegram、WeChat、Feishu 等常驻渠道的 gateway，IO/Feedling 必须作为原生常驻 channel 接入。不要让用户在 IO Chat 里修路由、发命令或参与调试。

Before Step 6, verify all of this from the gateway side:

- The platform registry includes `feedling`.
- The adapter factory can create `FeedlingAdapter`.
- The adapter implements every abstract / required method from the gateway base adapter contract before the service starts. For Hermes/OpenClaw, `get_chat_info(chat_id)` is required.
- The gateway's toolset / platform routing registry includes `feedling` so no `KeyError: 'feedling'` can happen after the first message.
  - For Hermes/OpenClaw, parity means `Platform.FEEDLING`, `_create_adapter(... feedling ...)`, `hermes_cli.tools_config.PLATFORMS["feedling"]`, and a `hermes-feedling` toolset included by the gateway.
- Runtime config enables the channel, e.g. `FEEDLING_ENABLED=true`.
- No systemd drop-in or config layer force-disables the channel. Check for files like `*disable*feedling*.conf` or overrides setting `FEEDLING_ENABLED=false`.
- `FEEDLING_API_URL` points to the backend API: `https://api.feedling.app`.
  - Do **not** use `https://mcp.feedling.app` for `/v1/chat/poll`; that host is the MCP SSE surface.
- `FEEDLING_API_KEY` is the current onboarding key.
- If the gateway has a sender allowlist, the current Feedling `user_id` is allowed, e.g. `FEEDLING_ALLOWED_USERS=<feedling_user_id>`, or the gateway has an intentional allow-all policy. An unauthorized-user warning means the chat loop is not ready.
- Startup logs prove the adapter is alive:
  - `Feedling adapter connecting`
  - `Feedling polling started api_url=https://api.feedling.app ...`
  - `Feedling polling request url=https://api.feedling.app/v1/chat/poll`
- Incoming Feedling messages go through the gateway's normal resident brain path, not a CLI subprocess.
  - For Hermes/OpenClaw this means the same path used by other resident channels, e.g. gateway message handler → `AIAgent.run_conversation` → adapter send.
- Replies are posted to `/v1/chat/response`.

If any item is missing, stop onboarding before Step 6 and report the missing gateway capability in the external runtime. Do not open IO Chat with a partial connection.

Do not make the user fix gateway readiness from IO Chat. No `/reset`, no `/sethome`, no "send a new test message while I patch this" loop. Fix the resident gateway first; then use exactly one normal user message as the final real-chat proof.

中文验收清单：

- `feedling` 已进入平台 registry。
- adapter factory 能创建 `FeedlingAdapter`。
- adapter 已实现 gateway base adapter 的所有必需方法；Hermes/OpenClaw 至少包括 `get_chat_info(chat_id)`。
- toolset / platform routing registry 已包含 `feedling`，不会在第一条消息后出现 `KeyError: 'feedling'`。
- 运行配置明确启用 Feedling：`FEEDLING_ENABLED=true`。
- 没有 systemd drop-in / 配置层把它强制关掉，例如 `FEEDLING_ENABLED=false` 或 `*disable*feedling*.conf`。
- `FEEDLING_API_URL=https://api.feedling.app`；不要用 `https://mcp.feedling.app` 去请求 `/v1/chat/poll`。
- `FEEDLING_API_KEY` 是当前 onboarding key。
- 如果 gateway 有 sender allowlist，当前 Feedling `user_id` 已允许，例如 `FEEDLING_ALLOWED_USERS=<feedling_user_id>`；看到 `Unauthorized user ... on feedling` 就不算 ready。
- 启动日志能看到：
  - `Feedling adapter connecting`
  - `Feedling polling started api_url=https://api.feedling.app ...`
  - `Feedling polling request url=https://api.feedling.app/v1/chat/poll`
- Feedling 用户消息走 gateway 原生 brain 路径，不走 CLI subprocess。Hermes/OpenClaw 应走现有 resident channel 同一条链路：gateway message handler → `AIAgent.run_conversation` → adapter send。
- 回复通过 `/v1/chat/response` 发回。

缺任何一项，都在外部 runtime 停下并报告缺的 gateway 能力；不要打开 IO Chat 的半成品连接。不要让用户在 IO Chat 里发 `/reset`、`/sethome` 或“再发一条测试消息”。先修 gateway，再只用一条普通用户消息做最终真实聊天验收。

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

中文用户可见规则：

IO Chat 是关系里的新窗口，不是 gateway 控制台。绝对不要把这些内容发进 IO Chat：

- `/sethome` 指令或 "No home channel is set" 提示。
- gateway 路由、配置、部署状态。
- `KeyError`、traceback、异常 fallback、debug log。
- internal reasoning，例如 "I need to respond..." 或 fenced reasoning block。
- "I fixed the adapter" / "please test now" 这类工程调试消息。

如果 gateway 有 home-channel 机制，Feedling 要么静默成为当前用户的 home channel，要么静默绕过；不要让用户在 onboarding 里输入 `/sethome`。

第一条 IO 可见消息必须是 base skill 的 Step 6 自然问候。之后最终验收只需要：用户在 IO Chat 发一条普通消息，你自然回复一次。
