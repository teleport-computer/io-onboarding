# IO

Give your AI agent a body on your iPhone.

IO lets the AI you already use read your screen, push to your lock screen,
and keep an identity card + memory garden of what it knows about you.

There are two onboarding routes:

1. **I have my own server** — VPS / Mac mini / always-on host, possibly using
   OpenClaw or Hermes. Live chat is owned by an independent resident consumer.
2. **I have a model API key** — OpenAI / Gemini / OpenRouter / Anthropic.
   IO hosts the runtime; no resident service is required.

This repo is the public onboarding package for IO testers. **The iOS app and
the IO server live elsewhere.** Everything here is just docs.

---

## 中文

### 我应该看什么

| 文件 | 干什么用 | 谁读 |
|------|----------|------|
| **[quickstart.md](./quickstart.md)** | 5 步把 IO 装好、连上 agent | 你（测试者） |
| **[troubleshooting.md](./troubleshooting.md)** | 卡住的时候的排错指南 | 你（测试者） |
| **[switch-to-vps-agent.md](./switch-to-vps-agent.md)** | 已经在托管、想换成你 VPS 上的 agent（数据不丢） | 你（测试者） |
| **[mcp-servers.md](./mcp-servers.md)** | 给 agent 接 MCP 工具服务（含自签名证书） | 你（测试者） |
| **[mcp-ombre-brain.md](./mcp-ombre-brain.md)** | 接 Ombre-Brain 记忆 MCP：认证怎么配（默认 OAuth 接不上，要换 token） | 你（测试者） |
| **[notify-relay.md](./notify-relay.md)** | 自部署后端收不到推送？用推送中继代发（通知 / Live Activity / 灵动岛） | 你（测试者） |
| **[im-bridge-guide.md](./im-bridge-guide.md)** | 把 QQ / IM 接入 Feedling：单脑桥接原则、安装和排错 | 你（测试者） |
| **[astrbot-feedling-bridge/README.md](./astrbot-feedling-bridge/README.md)** | 官方 AstrBot ↔ Feedling 纯桥插件安装与配置 | QQ / AstrBot 测试者 |
| **[skill.md](./skill.md)** | 共同底座：记忆、身份、连接原则 | 你的 AI |
| **[skill-resident-agent.md](./skill-resident-agent.md)** | 我有自己的服务器：VPS / Mac mini / Hermes / OpenClaw | 你的 AI |
| **[skill-api.md](./skill-api.md)** | 我有模型 API key：OpenAI / Gemini / OpenRouter / Anthropic | IO / 你的 AI |
| **[skill-guide.md](./skill-guide.md)** | 内部诊断用：路线辨认 | 操作员 / 你的 AI |
| **[PROMOTION.md](./PROMOTION.md)** | 内部维护用：test→main promote checklist | 操作员 |

### 怎么开始

1. 拿到 TestFlight 邀请链接（操作员私下发给你）
2. 装 app
3. 跟着 [quickstart.md](./quickstart.md) 走 5 步
4. 卡住就翻 [troubleshooting.md](./troubleshooting.md)

### 反馈

- 直接开 GitHub issue
- 或者发给你的操作员

---

## English

### What to read

| File | Purpose | Audience |
|------|---------|----------|
| **[quickstart.md](./quickstart.md)** | 5-step setup — install + connect your agent | You (the tester) |
| **[troubleshooting.md](./troubleshooting.md)** | Common failure modes + fixes | You (the tester) |
| **[switch-to-vps-agent.md](./switch-to-vps-agent.md)** | Already hosted? Switch to your VPS agent (no data loss) | You (the tester) |
| **[mcp-servers.md](./mcp-servers.md)** | Connect MCP tool servers to your agent (incl. self-signed) | You (the tester) |
| **[mcp-ombre-brain.md](./mcp-ombre-brain.md)** | Connect the Ombre-Brain memory MCP: auth setup (its default OAuth won't connect — switch to static token) | You (the tester) |
| **[notify-relay.md](./notify-relay.md)** | Self-hosted backend can't push? Relay pushes through the official server (alerts / Live Activity / Dynamic Island) | You (the tester) |
| **[im-bridge-guide.md](./im-bridge-guide.md)** | Connect QQ / IM to Feedling: single-brain bridge principles, setup, and troubleshooting | You (the tester) |
| **[astrbot-feedling-bridge/README.md](./astrbot-feedling-bridge/README.md)** | Install and configure the official AstrBot ↔ Feedling transport-only plugin | QQ / AstrBot testers |
| **[skill.md](./skill.md)** | Shared base: memory, identity, connection principles | Your AI |
| **[skill-resident-agent.md](./skill-resident-agent.md)** | I have my own server: VPS / Mac mini / Hermes / OpenClaw | Your AI |
| **[skill-api.md](./skill-api.md)** | I have a model API key: OpenAI / Gemini / OpenRouter / Anthropic | IO / Your AI |
| **[skill-guide.md](./skill-guide.md)** | Internal diagnostic route selection | Operator / Your AI |
| **[PROMOTION.md](./PROMOTION.md)** | Internal maintenance: test→main promote checklist | Operator |

### Getting started

1. Get the TestFlight invite link (your operator sends this directly)
2. Install the app
3. Follow [quickstart.md](./quickstart.md)
4. If stuck, see [troubleshooting.md](./troubleshooting.md)

### Feedback

- Open a GitHub issue here
- Or message your operator
