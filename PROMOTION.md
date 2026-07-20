# Promotion Gate — test → main

本仓库跑两条车道：

- **`test`**（测试车道）— 当前主线，新东西先在这里改、先在这里测。
- **`main`**（生产 canonical）— 已装 app 的用户，agent 实时 `raw.githubusercontent.com` 拉取的就是这条分支。**push 到 main = 立刻对所有在线用户生效，不需要发版。**

Promote 之前，逐条过这份 checklist。别凭感觉合并——下面每一条都对应过一次真实事故或一个会静默炸掉的坑。

---

## ① test 车道已真机验过

不是"本地跑通"，是真的走过一次 onboarding / 真机 agent 会话，确认这批改动在实际环境里行为正常。

**在 PR / commit message 里留一行证据**，格式：

```
verified: <日期> · <账号/环境> · <验的是哪条路径：VPS resident / API-key hosted / ...> · <结果>
```

例：`verified: 2026-07-14 · usr_75a0(知行) VPS resident · onboarding Step0→身份卡→live loop 全过`

没有这一行，不合并。

## ② self-ref 车道一致性（真实事故，别再犯）

`skill*.md` / `quickstart.md` 等文件里互相引用彼此时，用的是 `raw.githubusercontent.com/teleport-computer/io-onboarding/<branch>/...` 这种带分支名的绝对链接。**在 test 车道上开发时这些自引用理应指向 `test/`**（这样测试者拉到的也是测试版），但 promote 到 main 时必须**全部**改回指向 `main/`——漏了一个，装 app 的用户就会被自引用悄悄带回测试车道。

**真实事故**：`ed31710`（`docs(skill-resident): flip base-skill self-ref to main lane before promoting`）—— resident-agent 的 io_cli 走查是在 test 车道写的，promote 到 main 时漏改了一处 self-ref，还留着指向 test/skill.md。之前 `262aeb9` / `5e71725`（zhihao）也各修过一轮同类残留。这不是假设风险，是已经发生过至少三次的真实翻车模式。

**promote 前必须跑这条命令，输出必须为空**（排除本文件自身——本文件里的例子字符串会一直命中）：

```bash
grep -rn "io-onboarding/test/" *.md --exclude=PROMOTION.md
```

如果有输出——列出每个命中文件，逐个改成 `main/`，重新跑一遍确认清零，再继续。

（反过来，在 test 车道上开发时可以跑 `grep -rn "io-onboarding/main/" *.md` 确认 test 车道的自引用没有提前跳到 main——但这不是 promote 的阻塞项，只是 test 车道自己的卫生检查。）

## ③ consumer 安装分支指向核对

`skill-resident-agent.md` 里写死了 IO resident consumer（`feedling-mcp`）该装哪个分支，例如：

> Before starting the service, install or update the official consumer code from `https://github.com/teleport-computer/feedling-mcp` on the **`main`** branch — the release branch matching this skill.

promote io-onboarding 到 main 前，去核对一下：**feedling-mcp 当前的发布分支到底是不是这里写的这个**。feedling-mcp 自己也在跑 test/main 两条车道，两边promote节奏不同步是常态——io-onboarding 这边写的分支名可能已经滞后于 feedling-mcp 实际的发布状态。

检查方法：

```bash
grep -n "feedling-mcp\` on the \*\*\`" skill-resident-agent.md   # 英文段
grep -n "feedling-mcp\` 的 \*\*\`" skill-resident-agent.md        # 中文段
```

确认写的分支名仍和 feedling-mcp 实际发布的那条一致。**注意：这个分支名跟 io-onboarding 自己的 test/main 车道无关**——两条 io-onboarding 车道都写 feedling-mcp *当前对外发布*的那条分支（目前 test 和 main 都写 `main`，因为 feedling-mcp 已 promote 到 main）。它不随 io-onboarding 的车道自动镜像，只跟 feedling-mcp 的发布状态走。feedling-mcp 换发布分支时，**两条车道要一起改**，别让 test 和 main 的 consumer 指向分叉。

## ④ diff 审阅

Promote 前，把要合入 main 的每个文件过一遍 diff，不要盲 merge：

```bash
git diff main..test -- <file1> <file2> ...
```

逐个文件列出**行为变化**（不是逐行念 diff）：新加了什么规则、删了什么旧机制、哪个工具调用方式变了。这份行为变化清单直接贴进 promote 的 commit message 或 PR 描述里，方便回溯"这次 main 到底变了什么"。

## ⑤ promote 即生效，没有缓冲

`main` 是所有已装 app 的用户的 agent 实时拉取的对象。**push 到 main 的那一刻**，所有在线 agent 下一次读 skill 就会读到新版本——不需要用户升级 app，不需要等发版，没有灰度、没有回滚缓冲。

正因为如此，①-④ 是硬门，不是建议：

- 没有真机验证证据 → 不 promote。
- self-ref 有一个指向 test/ → 不 promote。
- consumer 分支指向过期 → 不 promote。
- 没过一遍 diff、说不清这次改了什么行为 → 不 promote。

四条全过，才 push main。
