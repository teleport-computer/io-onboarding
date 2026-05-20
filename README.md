# IO

Give your AI agent a body on your iPhone.

IO lets the AI you already use — Claude Code, Claude Desktop, Hermes, or another
MCP-capable client — read your screen, push to your lock screen, and keep an
identity card + memory garden of what it knows about you. If that client is a
one-shot CLI that exits after each turn, it needs a resident bridge for ongoing
chat after bootstrap; the skill's Runtime check makes that distinction.

This repo is the public onboarding package for IO testers. **The iOS app and
the IO server live elsewhere.** Everything here is just docs.

---

## 中文

### 我应该看什么

| 文件 | 干什么用 | 谁读 |
|------|----------|------|
| **[quickstart.md](./quickstart.md)** | 5 步把 IO 装好、连上 agent | 你（测试者） |
| **[troubleshooting.md](./troubleshooting.md)** | 卡住的时候的排错指南 | 你（测试者） |
| **[skill.md](./skill.md)** | Agent 读的指令书。你不直接看这个，你只是把 URL 给你 agent | 你的 AI agent |

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
| **[skill.md](./skill.md)** | Instruction manual the agent reads. You don't read this directly — you give the URL to your agent | Your AI agent |

### Getting started

1. Get the TestFlight invite link (your operator sends this directly)
2. Install the app
3. Follow [quickstart.md](./quickstart.md)
4. If stuck, see [troubleshooting.md](./troubleshooting.md)

### Feedback

- Open a GitHub issue here
- Or message your operator
