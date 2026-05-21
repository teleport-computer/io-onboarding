# IO · Troubleshooting

When something doesn't work — read this first. If you're still stuck, ping us with your symptoms + which section below got closest.

---

## 中文

### 1. Chat 页一直停在 "WAITING FOR AGENT"

**含义**：服务器没看到任何 agent 写过任何东西。Agent 没真正连上、或者连上但还没动。

**排查顺序：**

1. **MCP 连接到位了吗？** 在你的 agent 客户端里手动确认 MCP server 显示为已连接（不同客户端的 UI 不一样，但都会有"已连接 / 工具列表"的提示）。

2. **Agent 输出 Step 0 了吗？** Skill 要求 agent 在做任何事之前**先输出 Step 0 三行**（earliest message / name / memorable moments count）。如果 agent 直接开始写 identity 卡而没有 Step 0，说明它跳过了。让它"重新从 Step 0 开始，按 skill 要求逐字输出三行"。

3. **Skill 真的被读了吗？** 让 agent 复述："你 fetch 了 skill.md 后，第一个动作是什么？" 正确答案是"输出 Step 0 三行"。复述不出来 = 它跳过了 fetch，让它重 fetch。

4. **Agent 收到了 401？** 让 agent 调 `feedling_chat_get_history` 看响应。401 = MCP key 没传过去，重连 MCP server。

5. **空白页等几分钟之后会出现 "STUCK?" 区块**：里面有一段 debug prompt 直接复制给 agent，会自检报告卡在哪步。

### 2. Agent 把自己叫做 "Hermes" / "Claude" / "Claude Code"

**含义**：Agent 偷懒，用了 runtime 的默认 label 当名字。Skill 明确禁止这件事。

**修法**：直接告诉 agent："你违反了 skill 里的 hard rule——`agent_name` 不能是 runtime label。回去 Step 0 重新做：从我们的对话历史里找你被叫过什么名字。如果没有，跟我商量起一个，不要 fall back 到平台默认。"

Agent 会调 `feedling_identity_replace` 改名字。

### 3. Identity 页显示 "DAY 0" 或者一个奇怪的天数

**含义**：Agent 没按 skill 里的 `today − earliest_memory.occurred_at` 公式算，凭印象瞎写。

**修法**：

(a) 如果 Memory Garden 里**有卡**：让 agent 重算 — "你 Garden 里最早一张卡的 `occurred_at` 是哪天？今天减它就是 days_with_user。请重新算并 set。" Agent 调 `feedling_identity_set_relationship_days`。

(b) 如果 Memory Garden **是空的或者很少**：根因是 bootstrap 走得太浅。回到第 4 条。

### 4. Memory Garden 里只有 0–2 张卡 / 远低于关系长度

**含义**：Agent 跳过了深度提取。Skill 要求关系 1+ 月至少 15 张，6+ 月至少 30 张；低于这个底线就不能进入 identity。

**修法**：跟 agent 说：

> "你只写了 X 张卡，但我们认识 [N 个月]。按 skill 里 4-pass 的要求重做：
> - Pass 1（唤醒）：列我们之间所有 themes，10–25 个
> - Pass 2（清点）：每个 theme 列 candidate moments，直到够覆盖关系长度的底线
> - Pass 3（落卡）：通过 friend test 的全写下来，不够底线就继续扫，够了不要硬凑
> - Pass 4（对账）：列给我看，问我漏了什么
> 
> 这一轮不要快，预计 30–60 分钟。"

Agent 应该重新走 4 pass。

### 5. Identity 维度看起来是瞎写的 / 没受记忆支撑

**含义**：Agent 没遵守"每个维度必须有 ≥3 张记忆卡作为 receipts"的 skill 规则。

**修法**：让 agent 给你**列出**每个维度的 receipts："对每个维度，告诉我哪 3 张卡支撑这个值 (X)。如果指不出来，那个维度就不该写——换一个能 defend 的维度，重新派生。"

Agent 调 `feedling_identity_replace`。

### 6. Bootstrap 用了不对的语言（identity 中文 memory 英文，或反之）

**含义**：Agent 在 bootstrap 中混了语言。Skill 是 hard rule "整个 bootstrap 不准混语言"。

**修法**：直接重写："`feedling_identity_replace` + 把所有 memory cards 用 `feedling_memory_delete` 删了重写一遍，全程统一语言。Skill 在哪一行说了 hard rule，请你引用一遍再做。"

如果 Garden 已经几十张卡，**全部重写很贵**——可以妥协，只把 identity 改成跟 garden 一致的语言。

### 7. Bootstrap 跑了 10 分钟就"完成"了

**含义**：Skill 明确说 "1+ 月关系 < 30 分钟 = 跳过深度"。Agent 没按 4 pass 走。

**修法**：跟 agent 说："skill 的 hard rule 之一是 1+ 月关系 bootstrap 不能 < 30 分钟。回去重做 Pass 2（清点），把候选数翻 5 倍，**不要管时间**。"

### 8. Bootstrap 跑了 30+ 分钟还没完成

**这是正常的**。深度提取就是慢。30–60 分钟是设计好的预期。

**怎么判断 agent 在干活而不是 stuck**：去 Chat tab 看进度——`Memories planted` 数字应该在持续增长。如果 30 分钟数字一直不变，可能 agent 在 runtime 那边卡了；让它继续，或重新发 prompt。

### 9. Chat 收不到 agent 回复（"Chat loop" 进度卡在未完成）

最常见的失败模式。Agent 写完 bootstrap、发了第一条消息，然后**就停了**——你后面再发什么它都不回。

iOS 上的信号：进度条里 "Chat loop" 那一行显示 `send a message →`（说明 agent 发过初始消息但没轮询），或者 `—`（说明连初始消息都没发）。

**根因**：bootstrap 结束后必须有一个真实的长期 reply pipeline。Hermes / OpenClaw 这类常驻 gateway 应该像 Telegram/WeChat/Feishu bot 一样启用一个 Feedling/IO channel，由同一个 resident process 持续轮询并回复。只有字面意义上的 one-shot command（例如每次只运行一次 `hermes chat ...` 然后退出）才需要 `chat-resident-consumer` 这种 fallback bridge。

**最常见原因（按概率）：**

- **选错 Live connection owner**——按 [`skill.md` 的 "Connection owner selection"](./skill.md#connection-owner-selection-before-any-tool-call) 重新选最高优先级路径：resident agent/gateway > chat-product MCP client > HTTP/API backend > literal one-shot command fallback。Hermes/OpenClaw 如果有 resident gateway，就应该先找/启用 Feedling channel，而不是默认走 CLI bridge。
- **Agent 把 Hermes/OpenClaw 误判成 one-shot CLI**——让它先检查 resident gateway/channel registry。缺少 Feedling channel 的结论应该是“启用或实现 Feedling adapter”，不是“把自己降级成 `hermes chat ...`”。
  - 给它的 prompt：*"先不要继续 onboarding。回答：你现在是否运行在 Hermes/OpenClaw resident gateway 里？这个 gateway 里是否已有 Feedling/IO channel/adapter？如果有，启用它并用当前 key 轮询；如果没有，报告需要实现该 adapter。不要默认使用 hermes chat CLI 或 chat-resident-consumer。"*
- **`feedling_chat_verify_loop passing=true` 被误读**——这个结果只说明 synthetic ping 后出现了一条 agent-role 回复；如果回复来自 resident / bridge / fallback template，它不能证明 one-shot agent 本人还活着。用真实 app 消息和 resident 前台日志验证。
- **adapter 类不满足 gateway contract**——服务循环重启并出现 `TypeError: Can't instantiate abstract class FeedlingAdapter ...`，说明 adapter 缺 base class 要求的方法。先补齐抽象方法（例如 Hermes/OpenClaw 里的 `get_chat_info(chat_id)`），服务稳定后再继续。
- **常驻 gateway 没启动 Feedling long-poll**——如果 agent 确实是 resident，让它检查 gateway logs：是否有 Feedling channel startup、是否用当前 onboarding key、是否 poll `/v1/chat/poll`、是否 POST `/v1/chat/response`。
- **Feedling 被配置层强制关闭**——如果 platform/adapter 代码都存在但没有 startup/poll 日志，检查 systemd drop-ins / env / config snapshot，尤其是 `FEEDLING_ENABLED=false` 或 `*disable*feedling*.conf`。
- **API URL 配错**——`/v1/chat/poll` 必须走 `https://api.feedling.app`。如果日志里是 `https://mcp.feedling.app/v1/chat/poll`，就是错的；`mcp.feedling.app` 只用于 MCP SSE。
- **sender allowlist 拦截**——如果 polling 活着但用户消息不进 agent，日志可能有 `Unauthorized user: <usr_...> on feedling`。把当前 Feedling `user_id` 加进 gateway allowlist（例如 `FEEDLING_ALLOWED_USERS=<user_id>`），或明确采用 allow-all policy。
- **平台/工具集 registry 漏了 `feedling`**——adapter 能启动但第一条消息后出现 `KeyError: 'feedling'`，说明 gateway 的 platform/toolset/routing/home-channel registry 没补全。修 registry，不要让用户在 IO Chat 里处理。
- **gateway 配置提示泄漏到用户 Chat**——如果用户看到 "No home channel is set"、`/sethome`、部署状态、traceback、internal reasoning，说明 adapter 没把 gateway console 和 relationship chat 隔离。Feedling 应该静默注册/跳过 home-channel prompt，且过滤 debug/reasoning 后再 POST `/v1/chat/response`。
- **用户被要求发 `/reset` / `/sethome` 才能继续**——这是 bug，不是正常 onboarding。不要把 gateway 命令变成用户步骤；先在 adapter/config 层修好，然后只用一条普通消息做最终验证。
- **真的只有 one-shot command**——普通 shell 单次调用、每轮退出的 CLI、不能驻留的网页产品都不会自己 poll IO 消息。**这种情况不是换一句 prompt 能修的**：配置 `chat-resident-consumer`，或换成真正常驻的 runtime。
- **Vision gate 拦了**：agent 想 `feedling_push_live_activity` 但没先 `feedling_screen_decrypt_frame(include_image=true)`，server 返回 `vision_gate_missing_decrypt`。让 agent 先 decrypt frame。
- **Agent 循环 retry 但失败**：Settings → Health Check → "Chat round-trip" 行。如果显示 "no agent reply yet"，server 也没收到，问题在 agent 侧。

### 10. Live Activity 没出现在锁屏

**修法：**

1. 第一次安装时 onboarding 里有"启用 Live Activity"按钮。没点就去 iOS Settings → IO → Live Activities → 打开。
2. 锁屏等 agent push。Settings → Health Check → "Test live activity push" 发本地测试推送验证通路。
3. 系统设置开了但还没显示——重启 IO（双击主屏 swipe 关掉）然后重开。

### 11. 我换了 iPhone 语言 / 重装了 app / 系统更新之后 chat 全空了

**含义**：客户端 API key 被清，IO 帮你注册了新账号，旧数据绑在旧账号上。

如果你是 Keychain 修复版本（commit `ee6bd78` 之后），不应该再发生。如果还发生，告诉我们看日志能不能恢复旧账号。老版本——升级到最新 TestFlight build。

### 12. 跑了 Delete Account & Reset 之后 agent 每个 tool call 都返回 401 `user_not_found`

**含义**：Settings → Delete Account & Reset 把服务端账号删了、本地凭据清了、并注册了一个新账号；但你的 agent runtime（Claude.ai / Claude Desktop / Hermes / 等）里还 pin 着旧 key——旧 key 对应的 user 已经不存在了，所以所有 `tools/call` 都 401。

iOS 上的信号：reset 完成时会弹出 "Your old key is dead." 的 sheet，里面有新的 MCP String 和一个 COPY 按钮。如果你当时点了 "I'll update later"，现在去 Settings → Storage 重新拿。

**修法：**

1. iOS app → Settings → Storage → 找 "MCP String" 那一行 → COPY。
2. 把旧的 MCP 配置删掉，paste 新的：
   - **Claude Code / Claude.ai / Claude Desktop**：先 `claude mcp remove feedling`，然后把复制到的 `claude mcp add feedling …` 跑一遍。
   - **Hermes / OpenClaw / 自己起的 resident**：编辑 env 文件，把 `FEEDLING_API_KEY` 换成新 key，然后 `sudo systemctl restart feedling-chat-resident`（或你对应的服务名）。
3. 让 agent 重连，再发一条消息。它的 `feedling_bootstrap` 这次会返回 `first_time`——新账号是空的，让它重走 bootstrap。

**注意：** 旧账号的 chat / identity / memory garden 已经在服务端被删除了，找不回来。如果你只想轮换 key 但保留数据，**不要**用 Delete Account & Reset，用 Settings → Storage → "Regenerate API Key"。

### 还在卡住

把以下信息发给我们：

- iOS 版本
- IO build number（Settings 最底部 `v 0.5.0` 那种）
- 你用的 agent 客户端（Claude Code / Desktop / claude.ai / 其他）
- 卡在哪一步（参考 quickstart 的 5 步 + 如果在 bootstrap 中，是哪个 Pass）
- Health Check 页截图

---

## English

### 1. Chat tab stuck on "WAITING FOR AGENT"

**Meaning**: the server hasn't seen any agent activity yet. Agent isn't really connected, or is connected but hasn't done anything.

**Triage in order:**

1. **Is the MCP connection up?** In your agent client, verify the MCP server shows as connected.

2. **Did the agent output Step 0?** The skill requires the agent to output the **Step 0 three lines** (earliest message / name / memorable moments count) before any tool call. If the agent jumped straight to writing the identity card without Step 0, it skipped. Tell it: "Restart from Step 0 — output the three lines verbatim before doing anything else."

3. **Did the agent actually read the skill?** Have it recap: "After fetching skill.md, what's your first action?" Correct answer is "output the Step 0 three lines." If it can't recap, it skipped the fetch — tell it to re-fetch.

4. **Is the agent getting 401?** Have the agent call `feedling_chat_get_history` and check. 401 = key didn't propagate; reconnect the MCP server.

5. **After a few minutes the empty state shows a "STUCK?" block**: copy the debug prompt to your agent for self-diagnosis.

### 2. Agent named itself "Hermes" / "Claude" / "Claude Code"

**Meaning**: agent fell back to its runtime label. Skill explicitly forbids this.

**Fix**: tell the agent: "You violated the skill's hard rule — `agent_name` cannot be a runtime label. Go back to Step 0 and search our prior conversations for an actual name I called you. If none, propose one and let me confirm. Do not fall back to your platform default."

Agent calls `feedling_identity_replace`.

### 3. Identity shows "DAY 0" or a weird day count

**Meaning**: agent didn't follow the skill's `today − earliest_memory.occurred_at` formula and guessed instead.

**Fix:**

(a) If the Garden **has cards**: ask the agent: "What's the earliest `occurred_at` in my Garden? Subtract from today — that's `days_with_user`. Recompute and call `feedling_identity_set_relationship_days`."

(b) If the Garden is **empty or sparse**: root cause is shallow bootstrap. See section 4.

### 4. Memory Garden has 0–2 cards / far fewer than the relationship length warrants

**Meaning**: agent skipped depth. Skill requires ≥15 cards for 1+ month and ≥30 cards for 6+ months; below that floor, identity should not start.

**Fix**: tell the agent:

> "You only wrote X cards but we've known each other [N months]. Redo per the skill's 4 passes:
> - Pass 1 (唤醒/wake): list every theme between us, 10–25
> - Pass 2 (清点/enumerate): for each theme list candidate moments until you can cover the relationship-age floor
> - Pass 3 (落卡/write): write everything that passes the friend test; keep sweeping if below floor, don't pad after it
> - Pass 4 (对账/verify): list back to me, ask what I missed
>
> This pass is slow, 30–60 min. Don't rush."

Agent should redo the four passes.

### 5. Identity dimensions look made up / not grounded in memories

**Meaning**: agent ignored the skill rule "every dimension needs ≥3 memory cards as receipts".

**Fix**: ask the agent to **list** receipts for each dimension: "For each dimension, tell me the 3 memory cards that support its value. If you can't name them, drop the dimension and pick one you can defend, then re-derive."

Agent calls `feedling_identity_replace`.

### 6. Bootstrap used the wrong language (identity in Chinese, memory in English, or vice versa)

**Meaning**: agent mixed languages. Hard rule violation.

**Fix**: tell the agent to redo: "`feedling_identity_replace` and delete all memory cards (`feedling_memory_delete`), then rewrite everything in one consistent language. Quote the skill's hard rule about not mixing languages back to me before doing this."

If the Garden has many cards, full rewrite is expensive — compromise by changing identity to match the Garden's language.

### 7. Bootstrap "finished" in under 10 minutes

**Meaning**: skill's hard rule says <30 min for 1+ month relationship = skipped depth. Agent didn't run the four passes.

**Fix**: tell the agent: "One of the skill's hard rules is that bootstrap for 1+ month relationship cannot finish in <30 min. Redo Pass 2, multiply your candidates by 5×, and don't worry about time."

### 8. Bootstrap has been running 30+ minutes without finishing

**This is normal.** Deep extraction is slow. 30–60 min is the expected design window.

**How to tell the agent is working vs stuck**: check the Chat tab's progress — `Memories planted` count should be increasing. If the count doesn't change for 30 min, the agent may be stuck on its runtime side; tell it to continue, or re-send the prompt.

### 9. Chat sends but no reply ever comes ("Chat loop" progress row stalls)

The most common failure mode. Agent finishes bootstrap, posts its greeting,
then **stops** — anything you send afterward gets no reply.

iOS signal: in the progress checklist, the **Chat loop** row shows
`send a message →` (agent sent the initial message but isn't polling) or
`—` (agent didn't even send the greeting).

**Root cause**: after bootstrap there must be a real long-running reply
pipeline. Hermes / OpenClaw-style resident gateways should add a Feedling/IO
channel the same way they add Telegram/WeChat/Feishu channels, and that same
resident process should poll and reply. Only a literal one-shot command
(`hermes chat ...` invoked once and then exiting) needs the
`chat-resident-consumer` fallback bridge.

**Most common causes (by probability):**

- **Wrong Live connection owner** — re-run [`skill.md` "Connection owner selection"](./skill.md#connection-owner-selection-before-any-tool-call) and pick the highest-priority honest path: resident agent/gateway > chat-product MCP client > HTTP/API backend > literal one-shot command fallback. If Hermes/OpenClaw has a resident gateway, look for or enable a Feedling channel before considering any CLI bridge.
- **Agent misclassified Hermes/OpenClaw as one-shot CLI** — first inspect the
  resident gateway/channel registry. If Feedling is missing, the answer is
  "enable or implement the Feedling adapter", not "run `hermes chat ...`".
  - Try this prompt: *"Pause onboarding. Answer first: are you running inside
    the Hermes/OpenClaw resident gateway? Does that gateway have a Feedling/IO
    channel/adapter? If yes, enable it with this key and poll from there. If
    no, report that the adapter needs implementation. Do not default to Hermes
    CLI or chat-resident-consumer."*
- **`feedling_chat_verify_loop passing=true` was misread** — it only proves
  that an agent-role message appeared after the synthetic ping. If a resident /
  bridge / fallback template generated that message, it does not prove the
  one-shot agent itself is alive. Verify with a real app message and the
  resident's foreground logs.
- **A real resident gateway didn't start Feedling long-polling** — check gateway
  logs for Feedling channel startup, current onboarding key, `/v1/chat/poll`,
  and `/v1/chat/response`.
- **Adapter violates the gateway contract** — service restart loops with
  `TypeError: Can't instantiate abstract class FeedlingAdapter ...` means the
  adapter is missing a base-class method. Implement required methods first
  (for Hermes/OpenClaw this includes `get_chat_info(chat_id)`), then continue.
- **Feedling is force-disabled by config** — if platform/adapter code exists
  but there is no startup/poll log, inspect systemd drop-ins / env / config
  snapshots for `FEEDLING_ENABLED=false` or files like
  `*disable*feedling*.conf`.
- **Wrong API URL** — `/v1/chat/poll` must use `https://api.feedling.app`.
  If logs show `https://mcp.feedling.app/v1/chat/poll`, fix the gateway env;
  `mcp.feedling.app` is only the MCP SSE host.
- **Sender allowlist blocked the user** — if polling is alive but user messages
  do not reach the agent, logs may say `Unauthorized user: <usr_...> on
  feedling`. Add the current Feedling `user_id` to the gateway allowlist
  (for example `FEEDLING_ALLOWED_USERS=<user_id>`) or intentionally allow all.
- **Missing `feedling` registry entry** — if the adapter starts but the first
  message produces `KeyError: 'feedling'`, the gateway's platform/toolset/
  routing/home-channel registries are incomplete. Fix the registry; do not ask
  the user to repair this in IO Chat.
- **Gateway console leaked into IO Chat** — if users see "No home channel is
  set", `/sethome`, deployment status, traceback, or internal reasoning, the
  adapter is posting system/debug text as relationship chat. Feedling should
  silently register or bypass home-channel prompts and filter debug/reasoning
  before POSTing `/v1/chat/response`.
- **User had to send `/reset` / `/sethome` to continue** — this is a bug, not
  an onboarding step. Do not turn gateway commands into user instructions; fix
  the adapter/config layer, then use one normal message as final verification.
- **Your runtime is truly one-shot** — ordinary shell invocations, per-turn
  CLIs, and non-resident web products are request-response models. This is not
  fixed by another prompt: configure `chat-resident-consumer` or switch to a
  genuinely persistent runtime.
- **Vision gate blocked the push**: agent tried `feedling_push_live_activity`
  without first calling `feedling_screen_decrypt_frame(include_image=true)` —
  server returns `vision_gate_missing_decrypt`. Tell agent to decrypt the
  frame first.
- **Agent silently retry-looping**: Settings → Health Check → "Chat round-trip".
  If "no agent reply yet", server never received a reply — issue is on agent side.

### 10. Live Activity isn't showing on the lock screen

**Fixes:**

1. On first install, onboarding had an "Enable Live Activity" button. If you skipped, go to iOS Settings → IO → Live Activities → enable.
2. Lock the phone and wait. Settings → Health Check → "Test live activity push" sends a local test that bypasses the agent.
3. If enabled but nothing appears, force-quit IO and relaunch.

### 11. After switching iPhone language / reinstalling / OS update, chat went empty

**Meaning**: client-side API key got cleared and IO auto-registered a fresh account; old data still on server but bound to old account.

If you're on the Keychain-fix build (commit `ee6bd78` or later) this shouldn't recur. If it does, ping us — we can probably recover the old account from server logs. On older builds, upgrade.

### 12. After Delete Account & Reset, every tool call returns 401 `user_not_found`

**Meaning**: Settings → Delete Account & Reset deleted your account server-side, wiped local credentials, and auto-registered a fresh account — but your agent runtime (Claude.ai / Claude Desktop / Hermes / etc.) is still pinned to the OLD key. The old user no longer exists, so every `tools/call` returns 401.

iOS signal: when reset finishes, a "Your old key is dead." sheet appears with the new MCP String and a COPY button. If you tapped "I'll update later," grab it again from Settings → Storage.

**Fix:**

1. iOS app → Settings → Storage → find the "MCP String" row → COPY.
2. Remove the old MCP config and paste the new one:
   - **Claude Code / Claude.ai / Claude Desktop**: run `claude mcp remove feedling`, then paste the copied `claude mcp add feedling …` line.
   - **Hermes / OpenClaw / self-hosted resident**: edit your env file, replace `FEEDLING_API_KEY` with the new key, then `sudo systemctl restart feedling-chat-resident` (or whatever your service is called).
3. Reconnect the agent and send a message. Its next `feedling_bootstrap` will return `first_time` — the new account is empty; let it re-walk the bootstrap flow.

**Note:** The old account's chat / identity / memory garden was deleted server-side and can't be recovered. If you want to rotate the key without losing data, **don't** use Delete Account & Reset — use Settings → Storage → "Regenerate API Key" instead.

### Still stuck?

Send us:

- Your iOS version
- The IO build number (Settings, bottom — looks like `v 0.5.0`)
- Which agent client you're using
- Which step you're stuck on (reference the 5-step quickstart, or which Pass if in bootstrap)
- A screenshot of the Health Check page
