# 在 IO 里接入 Ombre-Brain（记忆 MCP）—— 认证与接入指南

[Ombre-Brain](https://github.com/P0luz/Ombre-Brain) 是一个"记忆型" MCP server，给
你的 agent 一组长期记忆工具（`hold` 存、`breath` 回想、`grow`、`trace` 等，共 14 个）。

这份指南**只讲它的认证与接入**，因为 **Ombre 远程默认开的是 OAuth 2.1，而 IO 不支持
OAuth**——这是"Ombre 接不上"的头号原因。MCP 的通用机制（URL/请求头/自签名证书/隧道/
测试连接怎么看）都在 **[mcp-servers.md](./mcp-servers.md)**，本文不重复，只在需要处指过去。

> 实测结论：把 Ombre 改成**静态 token 模式**后，IO 的两类 VPS 常驻 agent（**Hermes** 与
> **OpenClaw**）都能连上并真实调用 Ombre 工具（`hold`/`breath` 全通，14 个工具可见）。
> 下面就是怎么配。

---

## 一、一句话结论

| Ombre 的鉴权方式 | IO 支持吗 | 你要做什么 |
|---|---|---|
| **默认 OAuth 2.1** | ❌ 接不上 | 必须换成下面两种之一 |
| **静态 token**（推荐） | ✅ 实测可用 | Ombre 开 token 模式；IO 里加一条 `Authorization` 请求头 |
| **关闭鉴权** | ✅ 可用（不安全） | Ombre 关鉴权；IO 里只填 URL。**等于裸奔，别暴露公网** |

---

## 二、为什么默认接不上（原理）

OAuth 2.1 是一套**需要浏览器交互授权**的流程：点"允许"、跳转、拿授权码换 token。

IO 的 MCP 接入只支持一种认证形态——**URL + 你自己填的静态请求头**（比如
`Authorization: Bearer <token>`）。它**不会、也没法替你走 OAuth 授权流程**：你的 agent
是无人值守跑的（无论托管还是你 VPS 上的常驻 agent），没有人在浏览器里点"允许"，
OAuth 那一步永远完不成，于是连接始终认证不过——表现就是"加了、连不上"。

**所以关键不是 IO 有 bug，而是 Ombre 要改成 IO 认得的认证方式。**

---

## 三、在你的 Ombre 那边怎么配（二选一）

### 方式 A：静态 token 模式（推荐）

启动 Ombre 时设这几个环境变量（`docker compose` 的 `environment:` 段或 `.env` 里）：

```bash
OMBRE_TRANSPORT=streamable-http     # 远程接入必须
OMBRE_MCP_AUTH_MODE=token           # 关掉 OAuth，改成静态 token
OMBRE_MCP_TOKEN=<一段你自己生成的随机长字符串>   # 例：openssl rand -hex 24
```

> ⚠️ 这个 token **等于万能钥匙**——拿到它的人能读写你全部记忆。当强密码保管，
> 定期轮换，别写进公开仓库或截图。

### 方式 B：关闭鉴权（仅限可信内网 / 完全不暴露公网时）

```bash
OMBRE_TRANSPORT=streamable-http
OMBRE_MCP_REQUIRE_AUTH=false
```

关鉴权后 `/mcp` 对任何人开放，**Ombre 官方明确警告不要直连公网**。只有当这台服务
完全在你可信内网、或只被你自己的常驻 agent 通过 `localhost` 访问时才用。

改完**重启 Ombre** 生效。启动日志里应看到类似
`MCP 静态 Token 鉴权已启用（OAuth 端点已关闭）` 或 `require_auth=false`。

---

## 四、在 IO 里怎么填

在 IO 的 MCP 设置里新建一个 server：

| 字段 | 填什么 |
|---|---|
| **名称** | `ombre`（小写字母/数字/`-`/`_`，≤32 字符） |
| **URL** | 你的 Ombre 地址，**结尾必须是 `/mcp`**。例：`https://你的域名/mcp`。同一 VPS 上的常驻 agent 也可以填 `http://localhost:18001/mcp`（见第五节） |
| **请求头** | 方式 A 填一条：`Authorization: Bearer <你的 OMBRE_MCP_TOKEN>`（Ombre 也接受 `Ombre-MCP-Token: <token>`，二选一）。方式 B 不填 |

保存后点**"测试连接"**。测试结果各种提示的含义见
[mcp-servers.md 第五节](./mcp-servers.md#五测试连接的结果怎么看)。

> **常见错**：URL 只填到域名根、漏了 `/mcp`；或 token 前漏了 `Bearer ` 前缀；或还留着
> Ombre 默认的 OAuth 没改成 token 模式。这三样任何一个都会"连不上"。

---

## 五、你的 agent 够得到这台 Ombre 吗（网络可达性）

这和任何 MCP server 一样，取决于你 agent 跑在哪——**IO 只存配置、不替你转发流量**，
真正去连 Ombre 的是你 agent 调用工具的那一刻：

- **你 VPS 上的常驻 agent（Hermes / OpenClaw）**：如果 Ombre 就在**同一台 VPS**，
  直接填 `http://localhost:18001/mcp` 即可，无需公网、无需隧道（loopback 上用 `http`
  发 token 也没问题）。
- **IO 托管 agent**（IO 在云端帮你跑）：够不到你内网，**必须给 Ombre 一个公网 HTTPS
  地址**——用 Cloudflare Tunnel / Tailscale Funnel / ngrok 之类，然后 URL 填隧道给你的
  公网地址（结尾仍是 `/mcp`）。细节见
  [mcp-servers.md 第四节](./mcp-servers.md#四托管-agent-连不到你本地的-server--最常见的坑)。

---

## 六、如果你的 Ombre 用自签名证书

- 用 **Cloudflare Tunnel** 暴露的话，证书是公网信任的，**没有这个问题**，跳过本节。
- 自建 HTTPS + 自签名证书：IO 默认**首次连接即自动信任**，通常什么都不用做；
  完整说明（含 TOFU 安全性、以及 **codex 运行时只吃"CA+叶子证书链"、不吃单张自签名
  证书**的坑）见 [mcp-servers.md 第三节](./mcp-servers.md#三自签名证书的-server重点基本零配置)。

---

## 七、验证与排查

**验证**：加好之后，在聊天里明确让 agent 用一下 Ombre，例如：

> 用 ombre 的 hold 工具存一条："接入测试成功"，再用 breath 看一眼。

agent 应报告工具调用成功。Ombre 服务端日志会出现 `op=hold phase=ok` /
`op=breath phase=ok`——两边对上就说明端到端通了。

**排查对照**：

| 现象 | 多半是 |
|---|---|
| 认证失败 / 401 | 还没把 Ombre 改成 token 模式（仍是默认 OAuth）；或 token 填错；或漏了 `Bearer ` 前缀 |
| 连上了但一个工具都没有 | URL 结尾漏了 `/mcp` |
| 保存成功但 agent 从不调用 | 先确认 server 是**启用**状态；再确认 agent 到该地址**网络可达**（第五节）；再在聊天里**点名**让它用某个工具 |
| 托管 agent 连不上、填的是 localhost/内网 IP | 托管 agent 够不到你内网，得挂隧道走公网（第五节） |
| 自签名相关提示 / codex 用不了单张证书 | 见第六节 → mcp-servers.md 第三节 |

> **注**：`hold`/`grow` 这类会调用 LLM 压缩记忆的工具，需要你在 Ombre 那边配好它自己的
> 压缩模型 key（`OMBRE_COMPRESS_API_KEY` 等）；缺 key 时 `/mcp` 仍能连、工具仍列得出来，
> 但这几个工具真正执行会报错。这是 Ombre 自身的配置，和 IO 接入无关。

---

## 八、限制速查（IO 侧）

- URL 结尾 **必须 `/mcp`**；`http://` 会明文发送请求头（含 token），仅限 loopback/可信网络。
- 请求头最多 **20 条**、合计 **8KB**；`Host` 头禁止。
- 每账号最多 **10 个** MCP server。
- 其余通用限制见 [mcp-servers.md 第七节](./mcp-servers.md#七限制速查)。
