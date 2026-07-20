# 在 IO 里连接 MCP server —— 使用指南

这份指南教你在 IO 里给你的 agent 接上一个 **MCP server**（一种给 agent 提供
"工具"的远程服务，比如搜索、查资料、连你自己的系统）。覆盖**普通用法**和
**自签名证书**两种情况，以及"加了却不生效"时怎么办。

---

## 一、MCP server 是什么（一句话）

MCP server 是一个跑在某个网址上的服务，向你的 agent 暴露一组"工具"。在 IO 里
登记它之后，你的 agent 聊天时就能调用这些工具。**IO 只保存这份配置、不替你转发
流量**——真正去访问那个网址的，是你的 agent 在调用工具的那一刻。

每个账号最多可以登记 **10 个** MCP server。

---

## 二、添加一个 MCP server（普通情况）

在 IO 的 MCP 设置里新建一个 server，填三样：

| 字段 | 填什么 |
|---|---|
| **名称** | 只能是小写字母、数字、`-`、`_`，最长 32 个字符（例：`search`、`my-tools`）。同名会覆盖旧配置。 |
| **URL** | server 的地址。优先用服务商给你的 **`https://…/mcp`**（现代 streamable HTTP）。如果对方只给 `…/sse`（老式 HTTP+SSE）也支持，直接填。传输方式 IO 会自动识别，你不用选。 |
| **请求头（可选）** | 需要鉴权时填，比如 `Authorization: Bearer sk-xxx`。最多 20 条、总大小 8KB。`Host` 这个头不允许填。 |

填好保存即可。想确认是否连得上，点**"测试连接"**。

> **小提示**：URL 尽量用 `https://`。如果填 `http://`，你所有的请求头（包括
> `Authorization` 里的密钥）都会**明文**发出去，只在你完全信任的网络里才这么用。

---

## 三、自签名证书的 server（重点：基本零配置）

如果你的 MCP server 用的是**自签名证书**（不是 Let's Encrypt 那种公网信任的证书，
常见于自建/内网服务），**你什么都不用额外做**：

- 直接像普通 server 一样填 URL、保存。
- 你的 agent 第一次连接时，会**自动获取并信任**这个 server 自己的证书，之后每次
  连接都照常校验。**加密校验全程开着**，不是"跳过验证"。

也就是说：**自签名 server 无需你手动贴任何证书**。IO 编辑器里"高级"折叠里有一个
贴 CA 证书的框，**绝大多数情况用不到**，留空即可。

> **一句安全说明（TOFU）**：这种"首次连接即信任"和你第一次 SSH 登录一台新机器时
> 那句"确认要信任这台主机吗"是一回事——只有在**你 agent 有史以来第一次**连它、且
> 那一次正好被中间人劫持时才有风险。日常自建服务基本不用担心；如果你对某台 server
> 安全性要求特别高，可以在"高级"里手动贴它的 CA 证书（你从别处拿到的、不经过这条
> 连接），作为更强的保证。

### 一个进阶注意：某些 agent 需要"证书链"而不是单张证书

极少数情况下，如果你的 agent 底层跑在 **OpenAI（codex）** 这类运行时上，它对自签名
证书更严格：**只接受"CA 证书 + 服务器证书"的证书链，不接受单张自签名证书。**
（Claude 等大多数 agent 两种都收，不受影响。）

如果你恰好是这种情况、且 server 连不上，把证书改成证书链即可。用 `openssl` 生成：

```bash
# 1) 自建一张 CA 证书
openssl req -x509 -newkey rsa:2048 -keyout ca.key -out ca.crt -days 397 -nodes -subj "/CN=my-mcp-ca"
# 2) 生成服务器证书并用这张 CA 签发（注意 CA:FALSE + 你的域名/IP）
openssl req -newkey rsa:2048 -keyout server.key -out server.csr -nodes -subj "/CN=my-mcp"
printf 'basicConstraints=CA:FALSE\nsubjectAltName=DNS:你的域名\n' > ext.cnf
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 397 -extfile ext.cnf
# 3) 让 server 呈上完整链（server.crt 后接 ca.crt），私钥用 server.key
cat server.crt ca.crt > fullchain.crt
```

在 IO 的"测试连接"里，如果你遇到提示说"这看起来是单张自签名证书，codex 用不了、
请改成证书链"，就是在说这件事。

---

## 四、托管 agent 连不到你本地的 server —— 最常见的坑

这一条是 **"我加了 MCP server 但没反应"最常见的原因**，请务必看：

- **如果你用的是 IO 托管的 agent**（IO 在云端帮你跑 agent）：它跑在云上，**够不到
  你家里 / 办公室内网的机器**——这跟任何云服务一样，是网络可达性问题，不是权限被卡。
  所以填 `http://localhost:...`、`192.168.x.x`、`127.0.0.1` 这类本地地址，**会保存成功
  但云端 agent 永远连不上**。
  - 解决：给你的本地 server 前面挂一个**隧道**（[Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)、
    [Tailscale Funnel](https://tailscale.com/kb/1223/funnel)、[ngrok](https://ngrok.com/)），
    然后在 IO 里填隧道给你的**公网 HTTPS 地址**。

- **如果你自己跑 agent（自托管）**：它能到你这台机器能到的一切，包括 `localhost`
  和局域网，无需隧道。

> IO 允许你填 `localhost`、内网 IP、裸 IP，是因为**保存时后端根本不去连它**——只有你
> 的 agent 调用工具时才连。所以"填了本地地址"本身不报错，是否连得上取决于你的 agent
> 跑在哪。

---

## 五、"测试连接"的结果怎么看

点测试后可能看到几种提示，含义如下（大多是**提醒、不是失败**——配置已经存好了）：

| 提示 | 意思 / 怎么办 |
|---|---|
| 连接成功 | 一切正常。 |
| 已保存，但 IO 验证不了该证书 | 多半是自签名 server。**你的 agent 仍能自己连上**——在聊天里让它调用一下该 server 确认即可（见第三节）。 |
| 已保存，但 IO 够不到该地址 | 该地址不是公网可达（本地/内网）。IO 后端只是探测不到，**不代表你的 agent 连不上**（自托管能连）。托管 agent 请看第四节挂隧道。 |
| 这看起来是单张自签名证书，codex 用不了 | 见第三节"进阶注意"，把证书改成 CA+叶子链。 |
| 证书无效 / 证书过大 | 你在"高级"里贴的 CA 证书有问题（格式不对，或超过 32KB）。检查粘贴内容，或留空走自动信任。 |
| 请求头不合法 / 含被禁的头 | 检查请求头格式；`Host` 不允许填。 |
| 已达上限 | 已经登记满 10 个 server，删掉不用的再加。 |

---

## 六、其它常见问题

- **加了 server，但 agent 聊天时不调用工具**：先确认 server 在列表里是**启用**状态；
  再确认你的 agent（托管/自托管）到那个地址**网络可达**（第四节）；然后在聊天里
  **明确让它用某个工具**试一次。
- **改了 server 配置多久生效**：保存后很快生效，你的 agent 下一轮会拿到新配置，
  一般不用重启。
- **同名覆盖**：用同一个"名称"再保存，会**替换**那个 server 的整份配置（URL、请求头、
  证书都以新的为准）。
- **暂时停用而不删除**：把该 server 关掉（disable）即可，不必重填 URL/请求头/证书；
  想彻底移除再删除。
- **列表里的徽标**：显示某个 server 是否存了 CA 证书（你手动贴过才会有；走自动信任的
  不显示，属正常）。

---

## 七、限制速查

- 每账号最多 **10 个** server。
- 请求头最多 **20 条**、名值合计 **8KB**；`Host` 头禁止。
- 手动贴的 CA 证书最大 **32KB**。
- URL 支持 `http://` 和 `https://`；`http://` 会明文发送请求头，谨慎使用。
- 自签名证书：默认零配置自动信任；OpenAI/codex 类运行时需 **CA+叶子证书链**。
