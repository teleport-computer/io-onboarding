# IO Skill — Resident Agent

You are setting up IO through an independent resident consumer service on the user's own machine or server.

Examples: Hermes, OpenClaw, Claude Code running on a Mac mini / VPS, or another agent loop that stays alive without the user sending another prompt.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/main/skill.md

## Your path

- The user gives you resident consumer config: `FEEDLING_API_URL`, `FEEDLING_API_KEY`, and `FEEDLING_ENCLAVE_URL`. `FEEDLING_ENCLAVE_URL` is the decrypt source the consumer uses to read chat/memory/identity. The old MCP decrypt path is removed — do not look for or require `FEEDLING_MCP_URL`/`FEEDLING_MCP_KEY`.
- Configure an independent `feedling-chat-resident` / IO resident consumer service with that config.
- Before starting the service, install or update the official consumer code from `https://github.com/teleport-computer/feedling-mcp` on the **`main`** branch. If a checkout already exists, fast-forward it (`git fetch origin main` then `git checkout main` then `git pull --ff-only origin main`). If that checkout is dirty or not from the official repo, use a fresh checkout on `main` and point `WorkingDirectory` / `ExecStart` at it. In your external setup report, include the local HEAD and `origin/main`; they must match before Step 6.
- **The consumer's agent entry MUST be the same runtime that received this onboarding prompt — i.e. you.** If several runtimes happen to be installed on the box (e.g. both Hermes and OpenClaw), do NOT survey them and route to a "more convenient" one. The user is talking to a specific agent; the consumer must call that agent, not a sibling runtime. If the runtime you run in self-identifies with a runtime label when probed, that is fine — fix the card's `agent_name` (next bullet), do not switch runtimes to get a different default name.
- Fill in the agent entry from your own runtime, then point the consumer at it through HTTP or CLI. Use HTTP only when you expose a real resident endpoint that reaches your actual agent session. Otherwise use CLI. For Hermes/OpenClaw with no HTTP endpoint, set `HERMES_HOME` to the same profile/home used by the real running resident agent. Prefer reading it from the actual service environment (`systemctl --user cat/show hermes-gateway`, or `/proc/<MainPID>/environ`) instead of guessing from profile folder names. Then use the default CLI candidate `hermes chat -Q --source tool --max-turns 60 -q "{message}"`; the consumer stores the first `session_id` and resumes later turns with `--resume`. For Claude Code CLI, use `claude --print --output-format json "{message}"`; the consumer reads Claude Code's `session_id` from JSON output and resumes later turns with `--resume`. Use an absolute executable path if the service environment cannot find the CLI.
- Do not wrap `{message}` in a new identity/persona prompt. IO is a new transport for the same agent, not a new character or a lightweight helper.
- `agent_name` (in the identity card) must not be a runtime label — do not name yourself "Hermes" / "OpenClaw" / "Claude". But this is a constraint on the *name written in the card only*. It is NOT a reason to (a) switch which runtime carries the messages, or (b) edit your runtime's own persona/identity files (e.g. `IDENTITY.md`, `BOOTSTRAP.md`) to force a name. Use whichever runtime is your real agent as the transport, leave its files untouched, and set the card's `agent_name` separately. Choosing transport and naming the card are independent steps.
- For image messages, the consumer must pass the decrypted image context to your runtime: OpenAI-compatible HTTP receives an `image_url` block, simple HTTP receives an `images` array, and CLI receives a local image file path. If your CLI has a first-class image flag, use `{image_path}` / `{image_paths}` in `AGENT_CLI_CMD`; otherwise the consumer appends the path to `{message}`.
- Install the consumer as a service owned by the OS service manager (`systemd --user`, launchd, supervisor, pm2, etc.). The consumer may call Hermes/OpenClaw, but its process must be supervised independently from the current Hermes/OpenClaw conversation or top-level gateway. If you are currently inside Hermes/OpenClaw, write the env + service file, start/restart only `feedling-chat-resident`, then verify it from logs.
- Complete Step 0, the four memory passes, and identity exactly as the base skill requires.
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

- 用户给你的连接信息是 resident consumer config：`FEEDLING_API_URL`、`FEEDLING_API_KEY` 和 `FEEDLING_ENCLAVE_URL`。`FEEDLING_ENCLAVE_URL` 是 consumer 解密 chat/memory/identity 用的解密源。旧的 MCP 解密路径已移除——不要再找或要求 `FEEDLING_MCP_URL`/`FEEDLING_MCP_KEY`。
- 用这些信息配置一个独立的 `feedling-chat-resident` / IO resident consumer service。
- 启动 service 之前，先从 `https://github.com/teleport-computer/feedling-mcp` 的 **`main`** 分支安装或更新官方 consumer 代码。已有 checkout 时，用 fast-forward 更新（`git fetch origin main` 然后 `git checkout main` 然后 `git pull --ff-only origin main`）。如果 checkout 有本地改动或不是官方 repo，就在 `main` 上用新的干净 checkout，并让 `WorkingDirectory` / `ExecStart` 指向它。在外部 setup 汇报里写清楚 local HEAD 和 `origin/main`；两者一致后才能进入 Step 6。
- **consumer 的 agent 入口必须是"收到这条 onboarding 指令的那个 runtime"——也就是你自己。** 如果这台机器上恰好装了多个 runtime（比如同时有 Hermes 和 OpenClaw），不要去逐个试探、改接一个"更顺手"的。用户在跟某个特定 agent 对话，consumer 必须接到那个 agent，而不是它的兄弟 runtime。如果你所在的 runtime 被探测时自报了一个 runtime 名字，没关系——去改卡里的 `agent_name`（下一条），不要为了拿一个不同的默认名字去换 runtime。
- agent 入口由你根据自己的 runtime 填出来，不应该要求用户提供。有真实 resident HTTP endpoint 才用 HTTP；否则用 CLI。Hermes/OpenClaw 没有 HTTP endpoint 时，把 `HERMES_HOME` 设成你真实正在运行的常驻 agent 使用的同一个 profile/home。优先从真实 service 环境读取（`systemctl --user cat/show hermes-gateway`，或 `/proc/<MainPID>/environ`），不要靠 profile 文件夹名字猜。然后使用默认 CLI 候选：`hermes chat -Q --source tool --max-turns 60 -q "{message}"`；consumer 会保存第一次返回的 `session_id`，后续用 `--resume` 续接。Claude Code CLI 使用 `claude --print --output-format json "{message}"`；consumer 会从 JSON output 读取 Claude Code 的 `session_id`，后续用 `--resume` 续接。service 环境找不到 CLI 时改用绝对路径。
- 不要给 `{message}` 外面再包一层新人格 / 新身份 prompt。IO 只是同一个 agent 的新入口，不是新角色，也不是轻量 helper。
- 身份卡里的 `agent_name` 不能是 runtime 标签——别把自己叫成 "Hermes" / "OpenClaw" / "Claude"。但这只是对*卡里那个名字*的约束。它**不是**让你为此去 (a) 换一个 runtime 来传消息，或 (b) 改你 runtime 自己的人格/身份文件（比如 `IDENTITY.md`、`BOOTSTRAP.md`）来强行改名。用你真实的那个 agent runtime 当传输，别动它的文件，卡里的 `agent_name` 单独设。选传输和给卡命名是两件独立的事。
- 图片消息也要由 consumer 把解密后的图片上下文交给你的 runtime：OpenAI-compatible HTTP 收到 `image_url` block，simple HTTP 收到 `images` array，CLI 收到本地图片文件路径。如果你的 CLI 有专门的图片参数，在 `AGENT_CLI_CMD` 里使用 `{image_path}` / `{image_paths}`；否则 consumer 会把路径追加进 `{message}`。
- consumer 要作为 OS service manager 管理的独立服务运行（`systemd --user` / launchd / supervisor / pm2 等）。consumer 可以调用 Hermes/OpenClaw，但它自己的进程不属于当前 Hermes/OpenClaw 对话，也不挂在顶层 gateway 下面。如果你此刻就在 Hermes/OpenClaw 里操作，只写 env + service file，并只启动/重启 `feedling-chat-resident`，然后从日志验证。
- 这个 consumer service 负责持续轮询 Feedling、把用户消息交给你、再把你的回复写回 Feedling。

## Give yourself IO's tools (perception)

The consumer only delivers chat. To let IO sense the user's world *during chat* — current
weather, coarse location, motion, calendar — you must also make IO's tool CLI callable from
your chat turns. This is one more onboarding step, done once.

**Use the lightest tool-invocation surface your runtime already has.** A skill / instruction
file (`SKILL.md` / `AGENTS.md` / `CLAUDE.md`) that tells you when to call it, plus your
existing shell / exec / terminal tool, is *sufficient* — that is the baseline and it works
for every runtime here. Native typed tools, plugins, or MCP servers are **optional production
upgrades**: reach for them only when you need stronger tool discovery, argument schemas, or
permission gating. Don't over-build — if you can run the command below from a chat turn and
parse its JSON, you're done. (Heavy native registration, e.g. an OpenClaw plugin, also has
runtime-specific gotchas like config delivery and gateway reloads; the light path avoids them.)

- The CLI already ships in the consumer checkout you installed above: `tools/io_cli.py`
  (feedling-mcp `main` branch). You do not build it; you register it.
- Generic contract (the same for every runtime):
  - Invocation: `python3 <consumer-checkout>/tools/io_cli.py perception [SIGNALS...]`
    where SIGNALS ⊆ `now location weather motion calendar steps sleep workout vitals`
    (default = the fast set `now location weather motion calendar`).
  - Output: JSON `{"ok":true,"signals":{"<name>":{...}}}`. A signal the user has switched
    off / not permitted comes back as `{"disabled":true,"reason":"switch_off|not_permitted"}` —
    surface that honestly to the user, do not pretend you have the data.
  - Env: it reads the SAME `FEEDLING_API_URL` / `FEEDLING_API_KEY` / `FEEDLING_ENCLAVE_URL`
    the consumer uses. Make sure your tool-execution environment has them (read them from the
    consumer service env, do not ask the user).
- **Register it the way YOUR runtime registers tools** — you know your own runtime
  (Hermes / OpenClaw / Claude Code / Codex / …). Wire it so the model can call it mid-chat,
  exactly as you wired `AGENT_CLI_CMD`: the skill is generic, you adapt it.
- The iOS perception switches gate this **server-side** — flipping a switch changes whether
  the tool returns data or `disabled`; you do NOT re-register or reconfigure when a switch flips.
  Register once.
- Smoke-test from the service environment before the first greeting: run
  `io_cli.py perception now`, confirm JSON; then confirm the model can actually invoke the
  tool inside a chat turn (ask it something perceptual and check it calls the tool).

中文同义规则（给自己装 IO 工具）：

- consumer 只负责送聊天。要让 IO 在**聊天时**感知用户世界(当前天气/粗位置/运动/日历),你还得让
  IO 的工具 CLI 在你的聊天 turn 里能被调起。这是 onboarding 多出来的一步,配一次即可。
- **用你 runtime 已经有的最轻工具调用面就够**:一个 skill/说明文件(`SKILL.md`/`AGENTS.md`/`CLAUDE.md`)
  告诉你何时调它 + 你现成的 shell/exec/terminal 工具,**就足够**——这是 baseline,对这里每个 runtime 都成立。
  native typed tool / plugin / MCP 是**可选的生产升级位**:需要更强可发现性、参数 schema 或权限门控时才上。
  **别过度工程化**——能在聊天 turn 里跑下面的命令并解析 JSON,就完成了。(重的 native 注册如 OpenClaw 插件还有
  config 交付、gateway 重载这类 runtime 专属坑;轻路避开它们。)
- CLI 已随上面装的 consumer checkout 一起来了:`tools/io_cli.py`(feedling-mcp `main` 分支)。你不用造它,只用注册。
- 通用合同(对所有 runtime 一样):
  - 调用:`python3 <consumer-checkout>/tools/io_cli.py perception [信号...]`,信号 ⊆
    `now location weather motion calendar steps sleep workout vitals`(默认快档 `now location weather motion calendar`)。
  - 输出:JSON `{"ok":true,"signals":{"<名字>":{...}}}`。用户关掉/未授权的信号返
    `{"disabled":true,"reason":"switch_off|not_permitted"}`——如实告诉用户,别假装有数据。
  - 环境:它读的是 consumer 同一套 `FEEDLING_API_URL`/`FEEDLING_API_KEY`/`FEEDLING_ENCLAVE_URL`。
    确保你执行工具的环境里有这些(从 consumer service env 读,别问用户)。
- **按你自己 runtime 的方式注册它**——你清楚自己的 runtime(Hermes/OpenClaw/Claude Code/Codex…),
  像当初配 `AGENT_CLI_CMD` 一样把它接成模型聊天中能调的工具:skill 是通用的,你来适配。
- iOS 的感知开关在**服务端**门控——翻开关只改"工具返数据还是返 disabled",**开关一变你不用重注册/重配**。注册一次即可。
- 第一条问候前从 service 环境做 smoke test:跑 `io_cli.py perception now` 确认 JSON;再确认模型在一个聊天 turn 里
  真能调起这个工具(问它一个跟感知有关的问题,看它有没有调)。

## Resident consumer readiness

Before Step 6, verify the independent consumer service outcome:

1. The consumer is running with the current `FEEDLING_API_KEY`.
2. The running `chat_resident_consumer.py` comes from the latest official `feedling-mcp` `origin/main`, and the service `WorkingDirectory` / `ExecStart` point to that checkout.
3. The consumer is polling `FEEDLING_API_URL/v1/chat/poll`.
4. The consumer can call your agent entry and receive a real reply.
5. The consumer can write replies to `FEEDLING_API_URL/v1/chat/response`.
6. `feedling_chat_verify_loop` returns `passing=true`.
7. `feedling_onboarding_validate` marks `resident_consumer` and `live_loop` as passing.
8. One ordinary user message in IO Chat reaches you and gets one natural reply.
9. IO's tool CLI (`tools/io_cli.py perception`) is registered as a native tool in your runtime and
   smoke-tested (returns JSON; the model can invoke it mid-chat). See "Give yourself IO's tools".

For Hermes/OpenClaw CLI, also run a short smoke test from the service environment before the first visible greeting. Use ordinary inputs that represent the user's real chat, including an identity-style question, a tool-using question if tool use is expected, and one image-path message if the user expects IO Chat images to be visible. Fix command/toolset/session/image issues first if the output is not a natural reply from the same agent identity.

中文验收只看结果：

1. consumer 已经用当前 `FEEDLING_API_KEY` 运行。
2. 当前运行的 `chat_resident_consumer.py` 来自官方 `feedling-mcp` 最新 `origin/main`，并且 service 的 `WorkingDirectory` / `ExecStart` 指向这份 checkout。
3. consumer 正在轮询 `FEEDLING_API_URL/v1/chat/poll`。
4. consumer 能调到你的 agent 入口并得到真实回复。
5. consumer 能把回复写回 `FEEDLING_API_URL/v1/chat/response`。
6. `feedling_chat_verify_loop` 返回 `passing=true`。
7. `feedling_onboarding_validate` 里 `resident_consumer` 和 `live_loop` 通过。
8. 用户在 IO Chat 发一条普通消息后，你能自然回复一次。
9. IO 的工具 CLI(`tools/io_cli.py perception`)已注册成你 runtime 的原生工具并做过 smoke test
   (返回 JSON;模型能在聊天 turn 里调起它)。见"给自己装 IO 工具(感知)"。

Hermes/OpenClaw CLI 还要在第一条可见问候前，从 service 环境做一个短 smoke test。用几句用户真实可能发的话，包括身份类问题；如果预期有工具能力，也测一个需要工具的问题；如果用户期待 IO Chat 能看图片，也测一条带图片路径的消息。只要输出不是同一个 agent 身份下的自然回复，就先修 command / toolsets / session / image。

## User-visible chat rules

The IO chat is the relationship surface. Keep setup reports in the external runtime.

IO Chat messages should only be relationship/chat messages: the Step 6 greeting, then natural replies to the user's ordinary messages.

The first IO-visible message must be the Step 6 natural greeting from the base skill. After that, the final onboarding proof is one normal user message in IO Chat followed by one natural agent reply.

中文用户可见规则：

IO Chat 是关系里的新窗口。setup 过程、服务状态、错误日志留在外部 runtime 里说明。

第一条 IO 可见消息必须是 base skill 的 Step 6 自然问候。之后最终验收只需要：用户在 IO Chat 发一条普通消息，你自然回复一次。
