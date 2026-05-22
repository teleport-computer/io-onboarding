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

**含义**：Agent 把平台 / runtime 名称当成了关系里的名字。

**修法**：直接告诉 agent："`agent_name` 应该来自我们的历史，不是平台名字。回去 Step 0：从我们的对话历史里找你被叫过什么名字。如果没有，跟我商量起一个。"

Agent 会调 `feedling_identity_replace` 改名字。

### 3. Identity 页显示 "DAY 0" 或者一个奇怪的天数

**含义**：Agent 没按 skill 里的 `today − earliest_memory.occurred_at` 公式算，凭印象瞎写。

**修法**：

(a) 如果 Memory Garden 里**有卡**：让 agent 重算 — "你 Garden 里最早一张卡的 `occurred_at` 是哪天？今天减它就是 days_with_user。请重新算并 set。" Agent 调 `feedling_identity_set_relationship_days`。

(b) 如果 Memory Garden **是空的或者很少**：根因是 bootstrap 走得太浅。回到第 4 条。

### 4. Memory Garden 里只有 0–2 张卡 / 远低于关系长度

**含义**：Agent 没有提取出足够支撑 identity 的记忆。Skill 里的卡片数量是最低覆盖线：1+ 月至少 15 张，6+ 月至少 30 张。

**修法**：跟 agent 说：

> "你只写了 X 张卡，但我们认识 [N 个月]。按 skill 里 4-pass 的要求重做：
> - Pass 1（唤醒）：列我们之间所有 themes，10–25 个
> - Pass 2（清点）：每个 theme 列 candidate moments，直到够覆盖关系长度的底线
> - Pass 3（落卡）：通过 friend test 的全写下来，不够底线就继续扫，够了不要硬凑
> - Pass 4（对账）：列给我看，问我漏了什么
> 
> 这一轮按记忆深度花时间，不要为了快而省略重要历史。"

Agent 应该重新走 4 pass。

### 5. Identity 维度看起来是瞎写的 / 没受记忆支撑

**含义**：Identity 维度没有被具体记忆支撑。

**修法**：让 agent 给你**列出**每个维度的 receipts："对每个维度，告诉我哪些 memory cards 支撑这个值 (X)。如果指不出来，那个维度就不该写——换一个能 defend 的维度，重新派生。"

Agent 调 `feedling_identity_replace`。

### 6. Bootstrap 用了不对的语言（identity 中文 memory 英文，或反之）

**含义**：Agent 在 bootstrap 中混了语言，导致 Garden 和 identity 的体验不一致。

**修法**：优先让 agent 把 identity 改成跟 Garden 一致的语言。只有 Garden 本身也混乱时，才考虑删除并重写 memory cards。

如果 Garden 已经几十张卡，**全部重写很贵**——可以妥协，只把 identity 改成跟 garden 一致的语言。

### 7. Bootstrap 很快就"完成"了

**含义**：这通常说明 Agent 没按 4 pass 做足记忆提取，或者只用了当前 context。

**修法**：跟 agent 说："回去重做 Pass 1 / Pass 2：按主题重新清点候选 moments，覆盖完整关系长度。不要为了速度省略重要历史。"

### 8. Bootstrap 跑了比较久还没完成

**这可能是正常的**。关系越长，深度提取越慢。

**怎么判断 agent 在干活而不是 stuck**：去 Chat tab 看进度——`Memories planted` 数字应该在增长。如果长时间没有变化，可能 agent 在 runtime 那边卡了；让它继续，或重新发 prompt。

### 9. Chat 收不到 agent 回复（"Chat loop" 进度卡在未完成）

最常见的失败模式。Agent 写完 bootstrap、发了第一条消息，然后**就停了**——你后面再发什么它都不回。

iOS 上的信号：进度条里 "Chat loop" 那一行显示 `send a message →`（说明 agent 发过初始消息但没轮询），或者 `—`（说明连初始消息都没发）。

**根因**：bootstrap 结束后必须有一个真实的长期 reply pipeline。标准路径是独立 `feedling-chat-resident` / IO resident consumer service：它持续轮询 `FEEDLING_API_URL/v1/chat/poll`，把消息交给 agent 的 HTTP 或 CLI 入口，再 POST 到 `FEEDLING_API_URL/v1/chat/response`。

**最常见原因（按概率）：**

- **resident consumer 没跑起来**——确认 `feedling-chat-resident` / IO resident consumer service 当前正在运行，并且使用的是这一次 onboarding 的 `FEEDLING_API_KEY`。
- **consumer 没有轮询正确 API**——日志应该看到 `GET https://api.feedling.app/v1/chat/poll` 或自托管 API 的同等路径。
- **API URL 配错**——`/v1/chat/poll` 必须走 `https://api.feedling.app`。如果日志里是 `https://mcp.feedling.app/v1/chat/poll`，就是错的；`mcp.feedling.app` 只用于 MCP SSE。
- **agent 入口没配置好**——HTTP 模式只适合真实 resident HTTP endpoint；Hermes API server 要用 `AGENT_HTTP_PROTOCOL=openai` + `/v1/chat/completions`。没有真实 HTTP endpoint 时用 CLI；Hermes / OpenClaw 默认 `AGENT_CLI_CMD=hermes chat -Q --source tool --max-turns 4 -q "{message}"`，consumer 会保存 `session_id` 并用 `--resume` 续接。consumer 必须能用同一个环境调用到真实 agent，而不是只在手动 shell 里能跑。
- **CLI PATH / venv 不一致**——手动运行 `hermes` 或其他命令成功，不代表 resident service 里也能找到它。把 `AGENT_CLI_CMD` 写成绝对路径，或在 service env 里写明 PATH / venv。
- **消息解密失败**——日志如果出现 `user message has no plaintext content`，确认 `FEEDLING_MCP_URL` 或等价解密来源已配置，且当前 key 可用。
- **key 已旧或账号被 reset**——401 / `user_not_found` 说明 agent 还 pin 着旧 key。回到 iOS onboarding 或 Settings 复制新的 resident consumer config，替换 `FEEDLING_API_KEY` 后再连。
- **consumer 回了模板而不是真 agent**——如果用户看到“send that once more”或“我收到了，继续说”这类模板，说明 consumer 没有调到真实 agent，或 fallback 没有关闭。生产 onboarding 保持 `SEND_FALLBACK_ON_AGENT_ERROR=false`；先修 HTTP/CLI agent entry，再跑 verify。
- **setup 输出泄漏到用户 Chat**——如果用户看到部署状态、traceback、internal reasoning 或工程命令，说明 agent entry 的输出没有做用户可见内容清理。IO Chat 里只应该出现自然问候和自然回复。
- **真实消息验收没做**——`feedling_chat_verify_loop passing=true` 之后，还要让用户在 IO Chat 发一条普通消息，确认 consumer 收到、agent 正常生成、`POST /v1/chat/response` 成功。
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

iOS 上的信号：reset 完成时会弹出 "Your old key is dead." 的 sheet，里面有新的重新连接信息和一个 COPY 按钮。如果你当时点了 "I'll update later"，现在回到 Chat onboarding 或 Settings → Storage 重新拿。

**修法：**

1. iOS app → Chat onboarding → 按路径复制连接信息。
2. 把旧配置换成新的：
   - **Claude Code / Claude.ai / Claude Desktop / ChatGPT / Gemini 这类聊天工具**：先移除旧 feedling MCP，再 paste 新的 `claude mcp add feedling …` 或等价 MCP URL。
   - **Hermes / OpenClaw / 自己起的 resident**：使用新的 resident consumer config 更新 `feedling-chat-resident` / IO resident consumer service：`FEEDLING_API_URL=https://api.feedling.app`、新的 `FEEDLING_API_KEY`、可选 `FEEDLING_MCP_URL`，以及你的 `AGENT_MODE` / agent entry。
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

2. **Did the agent output Step 0?** The skill requires the agent to output the **Step 0 three lines** (earliest message / name / memorable moments count) before any tool call. If the agent jumped straight to writing the identity card without Step 0, it skipped. Tell it: "Start again from Step 0 — output the three lines verbatim before doing anything else."

3. **Did the agent actually read the skill?** Have it recap: "After fetching skill.md, what's your first action?" Correct answer is "output the Step 0 three lines." If it can't recap, it skipped the fetch — tell it to re-fetch.

4. **Is the agent getting 401?** Have the agent call `feedling_chat_get_history` and check. 401 = key didn't propagate; reconnect the MCP server.

5. **After a few minutes the empty state shows a "STUCK?" block**: copy the debug prompt to your agent for self-diagnosis.

### 2. Agent named itself "Hermes" / "Claude" / "Claude Code"

**Meaning**: agent used the platform / runtime name as the relationship name.

**Fix**: tell the agent: "`agent_name` should come from our history, not the platform name. Go back to Step 0 and search our prior conversations for an actual name I called you. If none, propose one and let me confirm."

Agent calls `feedling_identity_replace`.

### 3. Identity shows "DAY 0" or a weird day count

**Meaning**: agent didn't follow the skill's `today − earliest_memory.occurred_at` formula and guessed instead.

**Fix:**

(a) If the Garden **has cards**: ask the agent: "What's the earliest `occurred_at` in my Garden? Subtract from today — that's `days_with_user`. Recompute and call `feedling_identity_set_relationship_days`."

(b) If the Garden is **empty or sparse**: root cause is shallow bootstrap. See section 4.

### 4. Memory Garden has 0–2 cards / far fewer than the relationship length warrants

**Meaning**: agent did not extract enough memory to support identity. The card counts are minimum coverage lines: ≥15 cards for 1+ month and ≥30 cards for 6+ months.

**Fix**: tell the agent:

> "You only wrote X cards but we've known each other [N months]. Redo per the skill's 4 passes:
> - Pass 1 (唤醒/wake): list every theme between us, 10–25
> - Pass 2 (清点/enumerate): for each theme list candidate moments until you can cover the relationship-age floor
> - Pass 3 (落卡/write): write everything that passes the friend test; keep sweeping if below floor, don't pad after it
> - Pass 4 (对账/verify): list back to me, ask what I missed
>
> Take the time the history needs; don't optimize for speed."

Agent should redo the four passes.

### 5. Identity dimensions look made up / not grounded in memories

**Meaning**: identity dimensions are not grounded in concrete memories.

**Fix**: ask the agent to **list** receipts for each dimension: "For each dimension, tell me which memory cards support its value. If you can't name them, drop the dimension and pick one you can defend, then re-derive."

Agent calls `feedling_identity_replace`.

### 6. Bootstrap used the wrong language (identity in Chinese, memory in English, or vice versa)

**Meaning**: agent mixed languages, making Garden and identity feel inconsistent.

**Fix**: first ask the agent to change identity to match the Garden language. Only delete and rewrite memory cards if the Garden itself is mixed or unusable.

If the Garden has many cards, full rewrite is expensive — compromise by changing identity to match the Garden's language.

### 7. Bootstrap "finished" very quickly

**Meaning**: the agent likely did not run the four passes deeply enough, or only used current context.

**Fix**: tell the agent: "Redo Pass 1 / Pass 2: enumerate themes and candidate moments across the full relationship history. Do not optimize for speed."

### 8. Bootstrap has been running for a while without finishing

**This can be normal.** Longer relationships take longer to extract well.

**How to tell the agent is working vs stuck**: check the Chat tab's progress — `Memories planted` count should be increasing. If the count does not change for a long time, the agent may be stuck on its runtime side; tell it to continue, or re-send the prompt.

### 9. Chat sends but no reply ever comes ("Chat loop" progress row stalls)

The most common failure mode. Agent finishes bootstrap, posts its greeting,
then **stops** — anything you send afterward gets no reply.

iOS signal: in the progress checklist, the **Chat loop** row shows
`send a message →` (agent sent the initial message but isn't polling) or
`—` (agent didn't even send the greeting).

**Root cause**: after bootstrap there must be a real long-running reply
pipeline. The standard path is an independent `feedling-chat-resident` / IO
resident consumer service: it polls `FEEDLING_API_URL/v1/chat/poll`, calls the
agent's HTTP or CLI entry, then POSTs the reply to
`FEEDLING_API_URL/v1/chat/response`.

**Most common causes (by probability):**

- **The resident consumer is not running** — confirm `feedling-chat-resident` /
  the IO resident consumer service is running with this onboarding key.
- **The consumer is not polling the correct API** — logs should show
  `GET https://api.feedling.app/v1/chat/poll` or the self-hosted equivalent.
- **Wrong API URL** — `/v1/chat/poll` must use `https://api.feedling.app`.
  If logs show `https://mcp.feedling.app/v1/chat/poll`, fix the consumer env;
  `mcp.feedling.app` is only the MCP SSE host.
- **Agent entry is not configured** — HTTP mode is only for a real resident
  HTTP endpoint. Hermes API server uses `AGENT_HTTP_PROTOCOL=openai` plus
  `/v1/chat/completions`. Without a real HTTP endpoint, use CLI; for
  Hermes / OpenClaw, default to
  `AGENT_CLI_CMD=hermes chat -Q --source tool --max-turns 4 -q "{message}"`. The consumer
  stores `session_id` and resumes later turns with `--resume`. It must be able
  to call the real agent from its own environment.
- **CLI PATH / venv mismatch** — a command working in an interactive shell does
  not guarantee the resident service can find it. Use absolute paths or set the
  service PATH / venv explicitly.
- **Decryption failed** — if logs say `user message has no plaintext content`,
  configure `FEEDLING_MCP_URL` or the equivalent decrypt source with the current
  key.
- **Old key after reset** — 401 / `user_not_found` means the agent is still
  pinned to an old key. Copy the fresh resident consumer config from iOS and
  replace `FEEDLING_API_KEY`.
- **Template replies instead of real agent replies** — messages like "send that
  once more" or "I received it, continue" mean the consumer did not reach the
  real agent, or fallback was left on. Production onboarding keeps
  `SEND_FALLBACK_ON_AGENT_ERROR=false`. Fix the HTTP/CLI agent entry, then
  verify again.
- **Setup output leaked into IO Chat** — deployment status, traceback, internal
  reasoning, and engineering commands should stay in the external runtime. IO
  Chat should receive only natural greeting and natural replies.
- **Final real-message acceptance was skipped** — after
  `feedling_chat_verify_loop passing=true`, send one ordinary IO Chat message
  and confirm the consumer receives it, the agent generates normally, and
  `POST /v1/chat/response` succeeds.
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

iOS signal: when reset finishes, a "Your old key is dead." sheet appears with fresh reconnection details and a COPY button. If you tapped "I'll update later," grab them again from Chat onboarding or Settings → Storage.

**Fix:**

1. iOS app → Chat onboarding → copy the path-specific connection details.
2. Replace the old config with the new one:
   - **Claude Code / Claude.ai / Claude Desktop / ChatGPT / Gemini-style chat tools**: remove the old feedling MCP config, then paste the new `claude mcp add feedling …` line or equivalent MCP URL.
   - **Hermes / OpenClaw / self-hosted resident**: use the fresh resident consumer config to update `feedling-chat-resident` / the IO resident consumer service: `FEEDLING_API_URL=https://api.feedling.app`, the new `FEEDLING_API_KEY`, optional `FEEDLING_MCP_URL`, and your `AGENT_MODE` / agent entry.
3. Reconnect the agent and send a message. Its next `feedling_bootstrap` will return `first_time` — the new account is empty; let it re-walk the bootstrap flow.

**Note:** The old account's chat / identity / memory garden was deleted server-side and can't be recovered. If you want to rotate the key without losing data, **don't** use Delete Account & Reset — use Settings → Storage → "Regenerate API Key" instead.

### Still stuck?

Send us:

- Your iOS version
- The IO build number (Settings, bottom — looks like `v 0.5.0`)
- Which agent client you're using
- Which step you're stuck on (reference the 5-step quickstart, or which Pass if in bootstrap)
- A screenshot of the Health Check page
