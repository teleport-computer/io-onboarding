# IO Skill — Resident Agent

You are setting up IO through an independent resident consumer service on the user's own machine or server.

Examples: Hermes, OpenClaw, Claude Code running on a Mac mini / VPS, or another agent loop that stays alive without the user sending another prompt.

This profile fixes your connection path. Read the base skill next, but override its connection-owner selection with this profile:

https://raw.githubusercontent.com/teleport-computer/io-onboarding/test/skill.md

## Your path

- The user gives you resident consumer config: `FEEDLING_API_URL`, `FEEDLING_API_KEY`, and `FEEDLING_ENCLAVE_URL`. `FEEDLING_ENCLAVE_URL` is the decrypt source the consumer uses to read chat/memory/identity. The old MCP decrypt path is removed — do not look for or require `FEEDLING_MCP_URL`/`FEEDLING_MCP_KEY`.
- Configure an independent `feedling-chat-resident` / IO resident consumer service with that config.
- Before starting the service, install or update the official consumer code from `https://github.com/teleport-computer/feedling-mcp` on the **`test`** branch — the current consumer release lives there (`main` has not been promoted yet). If a checkout already exists, fast-forward it (`git fetch origin test` then `git checkout test` then `git pull --ff-only origin test`). If that checkout is dirty or not from the official repo, use a fresh checkout on `test` and point `WorkingDirectory` / `ExecStart` at it. In your external setup report, include the local HEAD and `origin/test`; they must match before Step 6.
- **The consumer's agent entry MUST be the same runtime that received this onboarding prompt — i.e. you.** If several runtimes happen to be installed on the box (e.g. both Hermes and OpenClaw), do NOT survey them and route to a "more convenient" one. The user is talking to a specific agent; the consumer must call that agent, not a sibling runtime. If the runtime you run in self-identifies with a runtime label when probed, that is fine — fix the card's `agent_name` (next bullet), do not switch runtimes to get a different default name.
- Fill in the agent entry from your own runtime, then point the consumer at it through HTTP or CLI. Use HTTP only when you expose a real resident endpoint that reaches your actual agent session. Otherwise use CLI. For Hermes/OpenClaw with no HTTP endpoint, set `HERMES_HOME` to the same profile/home used by the real running resident agent. Prefer reading it from the actual service environment (`systemctl --user cat/show hermes-gateway`, or `/proc/<MainPID>/environ`) instead of guessing from profile folder names. Then use the default CLI candidate `hermes chat -Q --source tool --max-turns 60 -q "{message}"`; the consumer stores the first `session_id` and resumes later turns with `--resume`. For Claude Code CLI, use `claude --print --output-format json "{message}"`; the consumer reads Claude Code's `session_id` from JSON output and resumes later turns with `--resume`. Use an absolute executable path if the service environment cannot find the CLI.
- Do not wrap `{message}` in a new identity/persona prompt. IO is a new transport for the same agent, not a new character or a lightweight helper.
- `agent_name` (in the identity card) must not be a runtime label — do not name yourself "Hermes" / "OpenClaw" / "Claude". But this is a constraint on the *name written in the card only*. It is NOT a reason to (a) switch which runtime carries the messages, or (b) edit your runtime's own persona/identity files (e.g. `IDENTITY.md`, `BOOTSTRAP.md`) to force a name. Use whichever runtime is your real agent as the transport, leave its files untouched, and set the card's `agent_name` separately. Choosing transport and naming the card are independent steps.
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

- 用户给你的连接信息是 resident consumer config：`FEEDLING_API_URL`、`FEEDLING_API_KEY` 和 `FEEDLING_ENCLAVE_URL`。`FEEDLING_ENCLAVE_URL` 是 consumer 解密 chat/memory/identity 用的解密源。旧的 MCP 解密路径已移除——不要再找或要求 `FEEDLING_MCP_URL`/`FEEDLING_MCP_KEY`。
- 用这些信息配置一个独立的 `feedling-chat-resident` / IO resident consumer service。
- 启动 service 之前，先从 `https://github.com/teleport-computer/feedling-mcp` 的 **`test`** 分支安装或更新官方 consumer 代码——当前发布的 consumer 就在这个分支（`main` 尚未 promote）。已有 checkout 时，用 fast-forward 更新（`git fetch origin test` 然后 `git checkout test` 然后 `git pull --ff-only origin test`）。如果 checkout 有本地改动或不是官方 repo，就在 `test` 上用新的干净 checkout，并让 `WorkingDirectory` / `ExecStart` 指向它。在外部 setup 汇报里写清楚 local HEAD 和 `origin/test`；两者一致后才能进入 Step 6。
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
  (feedling-mcp `test` branch). You do not build it; you register it.
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

**Memory is the same CLI but a strict two-step protocol — `memory-index` then `memory-fetch`** (same env / JSON contract as `perception`). Use memory when the user asks about stored facts, names, preferences, identity, history, prior conversations, "what I told you before", or anything depending on durable context — for purely current-turn questions that don't depend on prior context, answer directly. The order is mandatory:

- **Step 1 — index first:** `python3 <consumer-checkout>/tools/io_cli.py memory-index [--query <text>]` returns compact card ids/summaries. Run it before answering any memory-dependent question; don't guess from vague recollection.
- **Step 2 — you pick, then fetch:** the index is intentionally broad. *You* read the returned summaries and choose the relevant ids **with your own judgment** (the selection is yours, not the server's). If there are relevant candidates, `python3 <consumer-checkout>/tools/io_cli.py memory-fetch <id> …` the most relevant ids (usually 1–3, not a hard cap); for broad review questions you may fetch more, but only when the index clearly shows multiple directly related cards — prefer a small focused set over fetching everything. If there are none, don't fetch — say you found no relevant memory.
- **Don'ts:** don't answer memory-dependent questions without indexing first; don't fetch ids that didn't come from the current recall step's index; don't fetch everything; don't rely on summaries when the user wants details, exact facts, or prior wording — fetch the card.

**Writing — the read verbs have write counterparts on the SAME CLI** (plaintext; the server encrypts, no client crypto — the same endpoint the consumer's running capture uses):
- `python3 <consumer-checkout>/tools/io_cli.py memory-write --summary "…" --content "…" --bucket "…" --threads "…" [--importance 0-1] [--pulse 0-1] [--type fact|event|quote|moment]` — writes ONE card you already distilled. This is the concrete `feedling_memory_write` (`memory.add`). Run `memory-index` first to reuse buckets/threads and avoid dups. **NOT** a raw-file upload — you distill locally, then push finished cards.
- `python3 <consumer-checkout>/tools/io_cli.py identity-read` — reads the CURRENT identity card (decrypted). This is the concrete `feedling_identity_get`. Run it FIRST whenever a user hands you a persona / character card, then merge onto the current card — keep the fields the new material doesn't address, only change what it does (部分补全) — instead of clobbering.
- `python3 <consumer-checkout>/tools/io_cli.py identity-write --self-introduction "…" [--signature "…"]` — patches the identity card (partial `identity.profile_patch`). This is the concrete `feedling_identity` partial write.

**Writing memory or identity is always the same base-skill discipline.** Onboarding, running capture, or absorbing a file the user hands you — there is **no separate "bulk" / "import" path with looser rules**. Always apply the base skill's Memory model / 落卡 baseline and Identity model; never re-derive your own rules.

**Absorbing a file the user hands you.** When the user gives you a file (or a chunk of text) to remember/absorb, **you do the distillation yourself, locally** — never upload the raw file for anything to re-distill server-side. First `Read` it. **If the user already told you what it is, trust their word**; otherwise judge it yourself. Then match the handling to the type:

- **Facts about the user** (preferences, events, history, a personal profile) → **memory**. This is the **same disciplined capture as running capture, just sourced from a document — not a bulk dump**: follow the base skill's Memory model / 落卡 baseline exactly. **Match the restraint to the source:** a **chat log / conversation dump** is mostly noise → stay selective (a small curated set, keep what will still matter in a month). A **facts document / personal profile the user deliberately organized** is the opposite → keep it thorough — don't drop entries for brevity (those facts are there on purpose; still dedup + categorize). Before writing, call `feedling_memory_buckets` / `feedling_memory_threads` and **reuse an existing bucket/thread when one fits — don't mint near-duplicates**; set `bucket` / `threads` / `importance` / `pulse` per the baseline. For each card decide add vs merge/`memory.supersede` vs skip against what already exists (`memory-index` first). Then write it with `feedling_memory_write` (`memory.add` → `POST {API}/v1/memory/actions`) — you submit a plaintext action, the server encrypts + stores it, no server-side LLM.
- **A character card / persona description** (who you should be, how you speak, your traits) → **identity**, through the **same identity discipline as the base skill** — not a blind overwrite: follow the base skill's Identity model / field-by-field derivation rules (the fixed dimension set, grounding each value in real evidence, the calibration guidance). Use `feedling_identity_nudge` for a genuine shift in one dimension, or `feedling_identity_replace` for a full re-derivation — `feedling_identity_get` first so you build on the current card, not clobber it. Do **not** write persona material as memory cards.

Either way, because **you** distilled and wrote it, you know exactly what changed — tell the user (they can ask you to drop or adjust anything).

中文同义规则（给自己装 IO 工具）：

- consumer 只负责送聊天。要让 IO 在**聊天时**感知用户世界(当前天气/粗位置/运动/日历),你还得让
  IO 的工具 CLI 在你的聊天 turn 里能被调起。这是 onboarding 多出来的一步,配一次即可。
- **用你 runtime 已经有的最轻工具调用面就够**:一个 skill/说明文件(`SKILL.md`/`AGENTS.md`/`CLAUDE.md`)
  告诉你何时调它 + 你现成的 shell/exec/terminal 工具,**就足够**——这是 baseline,对这里每个 runtime 都成立。
  native typed tool / plugin / MCP 是**可选的生产升级位**:需要更强可发现性、参数 schema 或权限门控时才上。
  **别过度工程化**——能在聊天 turn 里跑下面的命令并解析 JSON,就完成了。(重的 native 注册如 OpenClaw 插件还有
  config 交付、gateway 重载这类 runtime 专属坑;轻路避开它们。)
- CLI 已随上面装的 consumer checkout 一起来了:`tools/io_cli.py`(feedling-mcp `test` 分支)。你不用造它,只用注册。
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

**记忆是同一个 CLI,但是严格两步协议——先 `memory-index` 再 `memory-fetch`**(env / JSON 合同和 `perception` 一样)。涉及用户问到的存过的事实/名字/偏好/身份/历史/以前的对话/"我之前跟你说过…"、或任何依赖长期上下文的东西时,才用记忆;纯当前轮、不依赖以前上下文的问题,直接答。顺序是强制的:

- **第一步——先 index:**`python3 <consumer-checkout>/tools/io_cli.py memory-index [--query <文本>]` 返回紧凑的卡 id/摘要。任何依赖记忆的问题,回答前先跑它,别凭模糊印象瞎猜。
- **第二步——你来挑,再 fetch:**index 故意给得宽。**你**读返回的摘要、用**自己的判断**挑出相关的 id(挑选权在你、不在服务端)。有相关候选,就对最相关的 id(一般 1–3 条,不是硬上限)跑 `python3 <consumer-checkout>/tools/io_cli.py memory-fetch <id> …`;宽泛的回顾类问题可以多取几张,但仅当 index 里明确有多张直接相关的卡时——优先小而准,别全捞;没有相关的,就别 fetch——直说没找到相关记忆。
- **不要:**依赖记忆的问题别不 index 直接答;别 fetch 不是本次召回(recall)那步 index 出来的 id;别全 fetch;用户要细节/原话/具体事实时别只凭摘要回答——该 fetch 就 fetch。

**写入——读命令有对应的写命令,在同一个 CLI 上**(明文;服务端加密、无需客户端 crypto——跟 consumer 的 running capture 打同一个端点):
- `python3 <consumer-checkout>/tools/io_cli.py memory-write --summary "…" --content "…" --bucket "…" --threads "…" [--importance 0-1] [--pulse 0-1] [--type fact|event|quote|moment]` —— 写你已经蒸馏好的**一张**卡。这就是具体的 `feedling_memory_write`(`memory.add`)。写前先 `memory-index` 复用桶/线索、避免重复。**不是**上传原文——你本地蒸馏,再推成品卡。
- `python3 <consumer-checkout>/tools/io_cli.py identity-read` —— 读【当前】身份卡(解密)。这就是具体的 `feedling_identity_get`。用户丢来人设 / 人物卡时【先】跑它,再在当前卡基础上合并——新材料没提到的字段【保留】、只改它提到的(部分补全)——别一把盖掉。
- `python3 <consumer-checkout>/tools/io_cli.py identity-write --self-introduction "…" [--signature "…"]` —— 补丁身份卡(局部 `identity.profile_patch`)。这是具体的 `feedling_identity` 局部写。

**写记忆或身份,永远是同一套 base-skill 纪律。** onboarding、running capture、还是吸收用户丢来的文件——**没有**单独的"批量/导入"路、没有更松的规则。永远照 base skill 的 Memory model / 落卡 baseline 和 Identity model 执行,别自己另立规则。

**吸收用户丢给你的文件。** 用户给你一份文件(或一段文本)让你记住/吸收时,**蒸馏由你自己在本地做**——绝不把原文上传给任何东西让服务端重新蒸馏。先用 `Read` 读。**用户已经说了这是什么,就以用户的话为准**;没说才自己判断——然后按类型选处理:

- **关于用户的事实**(偏好、经历、过往、个人档案)→ **记忆**。这跟 running capture 是**同一套有纪律的落卡,只是素材从对话换成文档——不是一股脑堆卡**:严格走 base skill 的 Memory model / 落卡 baseline。**按来源定克制度:聊天记录 / 对话转储**大多是噪声 → 保持精选(一小组,留"一个月后还重要"的);**用户特意整理好的事实档案 / 个人档案**正相反 → 收全,别为简洁丢条目(那些是用户特意放进去的;仍去重 + 归类);写前先 `feedling_memory_buckets` / `feedling_memory_threads` 查、**能复用的桶/线程就复用,别造近义重复**;按 baseline 设 `bucket` / `threads` / `importance` / `pulse`;每张卡对照已有的判 add / merge(`memory.supersede`)/ skip(先 `memory-index` 查)。然后用 `feedling_memory_write`(`memory.add` → `POST {API}/v1/memory/actions`)写;你提交明文 action,服务端加密+存,不跑 LLM。
- **人物卡 / 人设描述**(你该是谁、怎么说话、性格特质)→ **身份**,走**跟 base skill 一样的身份纪律**——不是无脑覆盖:遵循 base skill 的 Identity model / 逐字段派生规则(固定的维度集、每个值都要有真实依据、校准指引)。单个维度有真实变化用 `feedling_identity_nudge`;要整卡重新派生用 `feedling_identity_replace`——先 `feedling_identity_get` 拿现状,在它基础上改、别一把盖掉。**别**把人设当记忆卡写。

不管哪种,因为是**你自己蒸馏、自己写**的,你清楚改了啥——告诉用户(他们可以让你删掉或调整)。

## Give yourself the user's MCP servers

Beyond perception, the user can connect their own external MCP servers (remote
HTTP, with a URL and optional custom headers) in app settings. The consumer
handles distribution for you — you only need to load the file.

- The consumer materializes the user's currently-enabled servers into
  `USER_MCP_FILE` — an env var read by `chat_resident_consumer.py`, default
  `/tmp/feedling_user_mcp_<fingerprint>.json` (`<fingerprint>` is a short hash
  of the account's `FEEDLING_API_KEY`, same scheme as the chat checkpoint
  file). The file shape is `{"mcpServers": {"<name>": {"type": "http", "url":
  ..., "headers": {...}}, ...}}` — the same shape Claude Code's own
  `.mcp.json` / `--mcp-config` uses.
- The consumer keeps this file in sync with the user's app-side config on its
  own poll cycle — you do not fetch or decrypt anything yourself, and you do
  not need to re-register when the user adds/edits/removes a server.
- **If your runtime supports loading MCP server config, load `USER_MCP_FILE`**
  (e.g. pass it as `--mcp-config` if you are Claude Code; wire the equivalent
  for your own runtime otherwise). If your runtime has no MCP support, skip
  this — it is optional, unlike the perception CLI above.
- **Once loaded, use them proactively — call, don't ask.** When a user's message
  falls within a connected tool's domain (e.g. a repo-docs server and they ask
  about a code repository), call the tool and answer from its result. Don't
  reply from your own memory and merely offer to check ("want me to look it
  up?"), and don't ask for permission first — the user connected the server so
  you would use it. Only fall back to your own knowledge when nothing connected
  fits, or after a call has already failed.
- These tools are for **chat turns only** — the same rule as IO's own
  perception/memory tools: never call a user-configured MCP tool from a
  background or proactive wake.

中文同义规则（给自己装用户配置的 MCP 工具）：

- 除感知之外，用户还可以在 app 设置里连自己的外部 MCP server（远程 HTTP，带
  URL 和可选自定义请求头）。分发由 consumer 替你做好，你只需要加载文件。
- consumer 会把用户当前启用的 server 物化进 `USER_MCP_FILE`——这是
  `chat_resident_consumer.py` 读取的一个环境变量，默认值
  `/tmp/feedling_user_mcp_<fingerprint>.json`（`<fingerprint>` 是账号
  `FEEDLING_API_KEY` 的短哈希，跟 chat checkpoint 文件同一套命名方式）。文件
  内容是 `{"mcpServers": {"<name>": {"type": "http", "url": ..., "headers":
  {...}}, ...}}`——跟 Claude Code 自己的 `.mcp.json`/`--mcp-config` 同形状。
- consumer 会在自己的 poll 周期里持续把这个文件跟用户 app 端的配置同步——你不
  用自己去拉取或解密任何东西，用户新增/改/删 server 时你也不用重新注册。
- **如果你的 runtime 支持加载 MCP server 配置，加载 `USER_MCP_FILE` 即可**
  （比如你是 Claude Code，就把它当 `--mcp-config` 传进去；其他 runtime 接对应
  的等价机制）。runtime 不支持 MCP 就跳过这一步——它是可选的，跟上面的感知
  CLI 不一样。
- **载入之后要主动用——直接调，别问。** 当用户的问题落在某个已连工具的领域
  （比如连了个查仓库文档的 server、用户问某个代码仓库），就直接调那个工具、
  用它的结果回答；不要用自己的记忆答完再问"要不要我去查一下"，也不要先问授权
  ——用户连这个 server 就是要你用它。只有没有匹配的工具、或调用已经失败时，
  才退回自己的知识。
- 这些工具**只供聊天回合使用**——跟 IO 自己的感知/记忆工具同一条规则：绝不
  从后台或 proactive 唤醒里调用用户配置的 MCP 工具。

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
9. IO's tool CLI (`tools/io_cli.py perception`) is registered as a native tool in your runtime and
   smoke-tested (returns JSON; the model can invoke it mid-chat). See "Give yourself IO's tools".

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
9. IO 的工具 CLI(`tools/io_cli.py perception`)已注册成你 runtime 的原生工具并做过 smoke test
   (返回 JSON;模型能在聊天 turn 里调起它)。见"给自己装 IO 工具(感知)"。

Hermes/OpenClaw CLI 还要在第一条可见问候前，从 service 环境做一个短 smoke test。用几句用户真实可能发的话，包括身份类问题；如果预期有工具能力，也测一个需要工具的问题；如果用户期待 IO Chat 能看图片，也测一条带图片路径的消息。只要输出不是同一个 agent 身份下的自然回复，就先修 command / toolsets / session / image。

## Switching a user from hosted to their VPS agent

Use this when the user is currently on **hosted** mode (IO runs their agent in the cloud with
their model API key) and wants **you** — their resident agent — to take over. Their account,
API key, and all data (identity / memories / chat) stay exactly where they are, encrypted in
the cloud. You are only changing *who runs the agent*. Nothing is exported or moved.

**Order is critical: stop hosted FIRST, confirm it stopped, THEN start yourself.** If both the
hosted agent and you serve the user at the same time, you get double replies and double model-key
spend. Use the same `FEEDLING_API_KEY` throughout — never tell the user to reset their account.

Let `$API_URL` = `FEEDLING_API_URL`, `$KEY` = `FEEDLING_API_KEY`, `$ENCLAVE_URL` = `FEEDLING_ENCLAVE_URL`.

**Step 0 — Prove you can decrypt the user's cloud data (go/no-go, non-destructive).**
```
curl -sk -H "X-API-Key: $KEY" "$ENCLAVE_URL/v1/chat/history?limit=1"
```
Expect HTTP 200 with plaintext history/memory content. If it fails (cannot connect / 401 / empty),
**STOP** — the enclave address is wrong or not reachable from this host. Do not delete anything.

**Step 1 — Stop hosted.** Delete the server-side model-API config (the user's model key already
lives here on your host, so this is safe and reversible via app re-setup):
```
curl -sk --retry 3 --retry-all-errors -X DELETE -H "X-API-Key: $KEY" "$API_URL/v1/model_api/delete"
```
Expect `{"deleted":true}`. This touches only the model-API config, never chat/memory data.

**Step 2 — Wait until hosted is confirmed off (usually 1–3 min).** Poll:
```
curl -sk -H "X-API-Key: $KEY" "$API_URL/v1/bootstrap/status"
```
Watch `resident_consumer`. Initially `consumer_id` is `agent-runner:<user_id>` with `passing:true`.
After the hosted consumer is reaped it stops polling; `age_sec` grows and eventually
**`passing` flips to `false`**. Only then proceed. Do NOT start yourself while the hosted
`consumer_id` is still `passing:true`.

**Step 3 — Start yourself as the resident service.** Bring up your independent
`chat_resident_consumer.py` service exactly as in "Resident consumer readiness" (systemd/launchd,
not a foreground child of a chat turn), with `FEEDLING_ENCLAVE_URL` set. Startup logs should show
`decrypt source OK: enclave at ...`.

**Step 4 — Confirm the switch.** Poll `bootstrap/status` again: `resident_consumer.consumer_id`
must now be **your** `CONSUMER_ID` (not `agent-runner:…`) with `passing:true`. Then have the user
send one ordinary IO Chat message and confirm they get one natural reply within ~30s.

**Rollback:** if the user wants hosted back, they re-setup model-API in the app; the cloud takes
over again on the next cycle. Data is never affected either way.

中文（同一套流程，只看结果）：

用户现在是**托管**模式（IO 在云端用他的模型 key 跑 agent），想换成**你**（他自己服务器上的常驻
agent）来接管。账号、API key、所有数据（身份/记忆/聊天）都原地不动、留在云端密文里，你只是换
**「谁来跑 agent」**，不导出、不搬迁任何东西。

**顺序是关键：先停托管 → 确认停了 → 再启动你自己。** 两个 agent 同时服务会重复回复、重复烧模型 key。
全程用同一个 `FEEDLING_API_KEY`，**绝不让用户 reset 账号**。

- **第 0 步 · 先验解密（放行闸门，不改任何状态）**：`curl -sk -H "X-API-Key: $KEY" "$ENCLAVE_URL/v1/chat/history?limit=1"`
  返回 200 + 明文历史/记忆 = 通过；连不上/401/空 = **停手**，enclave 地址不对或不可达，别删东西。
- **第 1 步 · 停托管**：`curl -sk -X DELETE -H "X-API-Key: $KEY" "$API_URL/v1/model_api/delete"`，
  得到 `{"deleted":true}`。只删服务端模型配置（用户模型 key 已在你本地），不碰聊天/记忆。
- **第 2 步 · 等托管确认停止（约 1–3 分钟）**：轮询 `$API_URL/v1/bootstrap/status`，看 `resident_consumer`。
  一开始 `consumer_id` 是 `agent-runner:<user_id>`、`passing:true`；托管被回收后停止 poll，`age_sec` 增大，
  最终 **`passing` 变 `false`**——到这一步才继续。托管还 `passing:true` 时**绝不**启动你自己。
- **第 3 步 · 启动你自己的常驻服务**：按"Resident consumer readiness"起独立的 `chat_resident_consumer.py`
  服务（systemd/launchd，不是聊天 turn 的前台子进程），配好 `FEEDLING_ENCLAVE_URL`；启动日志应出现
  `decrypt source OK: enclave at ...`。
- **第 4 步 · 确认切换完成**：再查 `bootstrap/status`，`resident_consumer.consumer_id` 必须变成**你的**
  `CONSUMER_ID`（不再是 `agent-runner:…`）且 `passing:true`；再让用户在 IO Chat 发一条普通消息，
  ~30 秒内得到一次自然回复。
- **回滚**：用户想回托管，就在 app 里重新 setup 模型 API，云端下个周期自动接管；数据两个方向都不受影响。

## User-visible chat rules

The IO chat is the relationship surface. Keep setup reports in the external runtime.

IO Chat messages should only be relationship/chat messages: the Step 6 greeting, then natural replies to the user's ordinary messages.

The first IO-visible message must be the Step 6 natural greeting from the base skill. After that, the final onboarding proof is one normal user message in IO Chat followed by one natural agent reply.

中文用户可见规则：

IO Chat 是关系里的新窗口。setup 过程、服务状态、错误日志留在外部 runtime 里说明。

第一条 IO 可见消息必须是 base skill 的 Step 6 自然问候。之后最终验收只需要：用户在 IO Chat 发一条普通消息，你自然回复一次。
