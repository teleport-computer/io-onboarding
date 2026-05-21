# IO Skill — Resident Agent

You are a resident AI process running on the user's own machine or server.

Examples: Hermes, OpenClaw, Claude Code running on a Mac mini / VPS, or another agent loop that stays alive without the user sending another prompt.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- The user should give you resident connector config (`FEEDLING_API_URL`, `FEEDLING_API_KEY`, and optionally `FEEDLING_MCP_URL`). Put this into the resident Feedling/IO channel. Do not treat `claude mcp add ...` as your live-connection setup.
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

用户给你的连接信息应该是 resident connector config（`FEEDLING_API_URL`、`FEEDLING_API_KEY`，以及可选的 `FEEDLING_MCP_URL`）。把它写进常驻 Feedling/IO channel。不要把 `claude mcp add ...` 当成这条路径的 Live connection setup。

Self-restart boundary: you may configure or restart an **external** Feedling connector / gateway that is not carrying this conversation. You must not silently restart the resident gateway process that is carrying this current conversation. If the required next action is `systemctl restart` / service restart of your own Hermes/OpenClaw gateway, write the config, tell the user/operator that the restart must happen outside this turn, then stop before Step 6. After restart, wait for the user to send a fresh ordinary message and resume with readiness verification.

自我重启边界：你可以配置或重启一个不承载当前对话的外部 Feedling connector / gateway；但不能在当前 turn 里静默重启正在承载你自己的 Hermes/OpenClaw resident gateway。如果下一步必须 `systemctl restart` / 重启你自己的 gateway，就先写好配置，告诉用户/维护者这一步必须在当前 turn 外执行，然后停在 Step 6 之前。重启后，等用户发一条新的普通消息，再继续做 readiness verification。

Before Step 6, use the normal connector path and verify only the outcome:

1. Feedling/IO channel is configured with the current key.
2. The resident process is polling Feedling.
3. `feedling_chat_verify_loop` returns `passing=true`.
4. One ordinary user message in IO Chat reaches you and gets one natural reply.

中文验收只看结果：

1. Feedling/IO channel 已经用当前 key 配好。
2. 常驻进程正在轮询 Feedling。
3. `feedling_chat_verify_loop` 返回 `passing=true`。
4. 用户在 IO Chat 发一条普通消息后，你能自然回复一次。

Do not proactively inspect or repair adapter internals during normal onboarding. If one of the checks fails, stop before Step 6, report the concrete failure in the external runtime, and then read `troubleshooting.md`.

正常 onboarding 时不要主动检查或修 adapter 内部实现。只有上面的验收失败时，才停在 Step 6 前，在外部 runtime 报告具体失败点，然后再看 `troubleshooting.md`。

Do not make the user fix gateway readiness from IO Chat. No `/reset`, no `/sethome`, no "send a new test message while I patch this" loop. Fix connector setup outside IO Chat; then use exactly one normal user message as the final real-chat proof.

不要让用户在 IO Chat 里修连接。不要要求 `/reset`、`/sethome`，也不要说“我修一下你再发一条测试消息”。连接修复必须发生在 IO Chat 外；最后只用一条普通用户消息做真实聊天验收。

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
