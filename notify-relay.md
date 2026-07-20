# IO · 自部署推送中继（Push Relay）

让你的自部署后端也能给 IO app 发推送——一般通知、Live Activity、灵动岛。

---

## 这是什么，为什么需要它

推送到 Apple 设备必须用 Apple 签发的推送密钥（`.p8`），这把密钥属于 app 开发者、**不会外发**。所以你自己部署的后端**没法直接给 IO app 发推送**。

「推送中继」解决这个问题：你在 app 里申请一个**中继 Token**（`nrt_…`），之后你的后端带着这个 Token 调官方接口，由持有密钥的官方服务器**代你把推送投递到你的设备**。

支持的推送类型：

| 类型 | 说明 |
|---|---|
| `1` | 一般通知（顶部横幅 / 锁屏那种） |
| `2` | Live Activity 更新（灵动岛就是它的一种展示形态） |
| `3` | Live Activity 启动（push-to-start） |
| `4` | Live Activity 结束 |

> 前提：你的 IO app 已更新到**支持推送中继**的版本，且已在系统里**允许通知权限**。

---

## 第一步：在 app 里申请中继 Token

1. 打开 IO app（**自部署模式**下）→ 设置 → **系统配置** → **推送中继**。
   （这个入口**只在自部署模式下出现**；云模式的推送由官方直发，用不到它。）
2. 点「申请中继 Token」。app 会把本机的推送 token 注册到**官方**服务器，并显示一个 `nrt_` 开头的中继 Token。
3. 复制它，妥善保存。

关于这个 Token 的几点：

- 它**只在首次申请时显示一次**。app 会把它存在钥匙串里；如果你在别处也要用，就在这一步复制走。
- 重复申请同一台已注册的设备，服务器**不会再把 Token 显示出来**（设备的推送 token 不是秘密，不能凭它换回别人的中继 Token）。若你把 Token 弄丢了，需要重新申请。
- 换了设备 / 推送 token 轮换后，app 会带着你已有的 Token 自动重新绑定，Token 不变。

---

## 第二步：把 Token 配到你的后端

把中继 Token 放到你后端 / agent 跑推送的地方，例如写进环境变量：

```bash
echo 'NOTIFY_RELAY_URL=https://api.feedling.app'  >> ~/feedling-data/.env
echo 'NOTIFY_RELAY_AUTH_TOKEN=nrt_你的Token'      >> ~/feedling-data/.env
```

---

## 第三步：发推送

统一往官方接口 `POST https://api.feedling.app/v1/notify-relay/push` 发，用 `X-Relay-Token` 头带上你的 Token。

### 一般通知（类型 1）

不用带目标 token——默认发到你申请时注册的那台设备：

```bash
curl -s https://api.feedling.app/v1/notify-relay/push \
  -H "X-Relay-Token: $NOTIFY_RELAY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": 1, "content": {"title": "IO", "body": "你的 agent 回复了"}}'
```

`content` 可用字段：`title`、`body`、`subtitle`、`sound`（默认 `"default"`）、`badge`、`data`（自定义键，会并进推送顶层）。

### Live Activity / 灵动岛（类型 2 / 3 / 4）

这几种**必须带目标 token**，因为 Live Activity 的 token **每次活动都会轮换**。

这些 token 从哪来？你的 app 会把三类 token 上报到**你自己的后端**（`POST /v1/push/register-token`，存在你后端库里 `user_blobs` 的 `tokens` 记录）：

- `live_activity`：更新一个正在进行的活动用的 token
- `push_to_start`：远程**拉起**一个新活动用的 token（iOS 17.2+）

调中继时，从你后端取**最新**的那个 token 传进来。

```bash
# 3 · 用 push-to-start token 拉起一个 Live Activity（灵动岛随之出现）
curl -s https://api.feedling.app/v1/notify-relay/push \
  -H "X-Relay-Token: $NOTIFY_RELAY_AUTH_TOKEN" -H "Content-Type: application/json" \
  -d '{"type": 3, "token": "<push_to_start_token>",
       "content": {"name": "IO", "desc": "正在处理…", "alert_body": "已开始"}}'

# 2 · 用 live_activity token 更新它（灵动岛同步刷新）
curl -s https://api.feedling.app/v1/notify-relay/push \
  -H "X-Relay-Token: $NOTIFY_RELAY_AUTH_TOKEN" -H "Content-Type: application/json" \
  -d '{"type": 2, "token": "<live_activity_token>",
       "content": {"visualState": "reply", "name": "IO", "desc": "完成！",
                   "alert_title": "IO", "alert_body": "完成！"}}'

# 4 · 结束它
curl -s https://api.feedling.app/v1/notify-relay/push \
  -H "X-Relay-Token: $NOTIFY_RELAY_AUTH_TOKEN" -H "Content-Type: application/json" \
  -d '{"type": 4, "token": "<live_activity_token>", "content": {}}'
```

类型 2/3/4 的 `content` 常用字段：`visualState`（`default` / `sharing` / `reply`）、`name`、`desc`、`alert_title`、`alert_body`；类型 2 还可带 `stale_date`；类型 4 可带 `dismissal_date`（unix 秒，默认立即）。

---

## 怎么看返回结果

成功和失败都返回 **HTTP 200**，真正的结果在 body 的 `status` 里：

```json
{ "status": "delivered", "apns_env": "production", "log_id": 42 }
```

失败时：

```json
{ "status": "error", "apns_env": "production", "log_id": 43,
  "reason": "BadDeviceToken", "error_code": 400 }
```

- `status: "delivered"`：已投递给 Apple。
- `status: "error"` + `reason`：Apple 拒了。常见 `BadDeviceToken` / `Unregistered` 意味着那个 token 失效了——**在你这边刷新 token 后重试**（中继不替你管理透传 token 的生命周期）。

HTTP 状态码：

| 码 | 含义 |
|---|---|
| `401` | 中继 Token 缺失或错误 |
| `403` | 该 Token 已被停用 |
| `429` | 触发限流，**尊重 `Retry-After` 头**再重试 |
| `503` | 官方侧暂时无法签发推送，稍后重试 |

---

## 限流

- 申请 Token：每个 IP 每小时若干次（申请是低频动作）。
- 推送：**每个 Token 每分钟约 120 次**，单用户屏幕活动足够用。
- 超限返回 `429` 并带 `Retry-After`（秒），按它退避即可。

---

## 隐私说明

经中继的每次推送都会在**官方服务器留一条记录**用于排障：推送类型、目标 token、投递结果，以及 `content` 内容（**截断到 512 字符**）。

如果你不希望某些内容被留存，就别把它经中继推送，或让推送文案保持简短（比如只发一句笼统的「有新回复」）。

---

## 常见问题

**申请按钮是灰的 / 点了没反应。** 先在系统设置里给 IO **开启通知权限**，app 拿到推送 token 后按钮才可用。

**返回 `already_enrolled`、没有 Token。** 这台设备已经注册过了，出于安全服务器不会再显示 Token。如果你还留着之前那个 `nrt_`，继续用它；否则重置注册再重新申请。

**一直 `BadDeviceToken` / `Unregistered`。** 目标 token 失效了。一般通知（类型 1）说明设备推送 token 变了——让 app 重新申请一次即可；Live Activity（类型 2/3/4）说明你传的活动 token 过期了——从你后端取最新的再发。

**收到 `503`。** 官方侧此刻签不了推送，这是临时的，过一会儿重试。

**推送发出去了（`delivered`）但手机没响。** 检查系统通知权限、勿扰模式；Live Activity 还要确认活动确实处于进行中（先用类型 3 拉起，再用类型 2 更新）。
