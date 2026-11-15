# AGENTS.md —— 给 AI 的入口（读完这页就能开工）

## 这是什么

**葫芦侠三楼每日自动签到**（上游开源项目的 Fork 版）—— 38 个版块精准签到、多账号支持、
每日定时执行，靠 GitHub Actions 跑，不占本机。

- 本仓库：`git@github.com:TKPORL/huluxia_thirdfloor_signin.git`
- 上游项目：`BoltLv4215/huluxia_thirdfloor_signin`

## 硬性规则（★必读）

- 项目根目录 = `D:\Tsinho文件夹\葫芦侠自动签到工具`（路径**没有空格**）
- **账号密码只存在 GitHub Secrets（`ACCOUNTS`），绝不写进代码、文档、回复**
- 使用前提（README 明确警告）：**葫芦侠账号需先解除 QQ 绑定**，否则会报"账号保护已开启，请使用 QQ 登录"
- 这是 Fork 项目：**改本地 ≠ 改线上**，线上生效必须推仓库
- 动手前先说清「改什么 / 为什么 / 影响 / 怎么验证 / 怎么回滚」，等用户点头；改完写变更记录（含「之前 → 现在」）

## 怎么跑

线上（主要方式）：GitHub Actions 定时触发（cron `0 16 * * *` 即北京时间 24 点），
或 `Actions → huluxia_signin → Run workflow` 手动触发

本地：

```bash
pip install -r requirements.txt
python main.py
```

## 断签防护（★这套是核心，别删）

签到中断过两次，原因不同，但都是「几个月后才发现」。现在的防护分三层：

| 层 | 机制 | 兜住什么 |
|---|---|---|
| 1 | `保活提交`（每天写 `.last_run` 并提交） | GitHub 在仓库 60 天无提交时自动停用 schedule |
| 2 | `失败告警`（`alert_failure.py`） | 任意步骤失败 → 立刻发邮件/企微，不必等 |
| 3 | `心跳上报`（healthchecks.io） | **任务压根没跑**（被停用 / cron 被跳过 / 额度用尽）也会在 26 小时后告警 |

**第三层是唯一能兜住「静默不跑」的手段**——GitHub 自身的失败邮件只在「跑了但失败」时才发，
「根本没跑」它一个字都不说，这正是 2026-11 那次白签 10 天的原因。

### 关键设计约束（改代码前必读）

- `alert_failure.py` **只能用标准库**（不得 import requests），且必须用 `/usr/bin/python3` 调用。
  因为它可能在 `setup-python` 崩掉之后执行，那时 pip 根本没跑。
- `失败告警` 步骤用 `if: failure()`，`心跳上报` 用 `if: always()`，两者顺序不能颠倒。
- 心跳根据 `steps.signin.outcome` 决定上报正常还是 `/fail`，**不要**改成按 job 整体状态判断，
  否则保活步骤的失败会污染签到结果。
- `main.py` 判定必须写成 `failed > 0`（有一个失败就失败），
  **不能**写成 `failed == len(accounts)`，否则部分账号断签不会变红，心跳还会报平安。

### 2026-11 事故复盘（务必记住）

- 现象：#106（11/04）成功，#107（11/05）起连续失败到 #116
- 根因：`actions/checkout@v3` + `actions/setup-python@v4` 所使用的 Node 运行时被 GitHub 强制下线，
  「初始化python环境」步骤 1 秒即崩，**签到代码一次都没跑到**
- 为什么没通知：通知代码在签到脚本里，脚本没跑 = 一条消息都发不出
- 修复：action 升级到 `@v7`，并加上面三层防护
- 教训：**GitHub 的 action 版本会过期**，每隔几个月应看一眼运行记录是否还绿

## 目录

| 文件 | 作用 |
|---|---|
| `main.py` | 入口（一个账号失败即整体失败，退出码 1） |
| `signin.py` | 签到逻辑（登录失败会抛出明确异常，不再静默跳过） |
| `notifier.py` | 消息推送（企业微信群机器人 / 邮箱 / 不推送） |
| `alert_failure.py` | **失败兜底告警**，纯标准库，由系统 python3 执行 |
| `logger.py` | 日志 |
| `cat_id.json` | 38 个版块的 ID 表 |
| `src/` | README 用的效果图（`wechat.jpg` / `email.png`） |
| `requirements.txt` | 依赖 |

推送方式通过环境变量 `NOTIFIER_TYPE` 选择：`wechat` / `email` / `none`

## 需要的 Secrets

| 名称 | 必需 | 作用 |
|---|---|---|
| `ACCOUNTS` | 是 | 账号密码，格式 `手机号,密码`，多账号一行一个 |
| `NOTIFIER_TYPE` | 是 | `email` / `wechat` / `none` |
| `EMAIL_CONFIG` | email 模式必需 | JSON，含 `username` / `auth_code_or_password` / `sender_email` / `recipient_email` |
| `WECHAT_ROBOT_URL` | wechat 模式必需 | 企业微信群机器人 Webhook |
| `HEALTHCHECK_URL` | **强烈建议** | healthchecks.io 的 ping 地址，缺了就没有「任务没跑」的告警 |

## 当前状态

- 最后更新：2026-11-15（修复 action 版本失效导致的连续断签，并加装三层防护）
- Git：是（Fork 自上游）
- workflow action 版本：`checkout@v7` / `setup-python@v7`（**已过期会直接失效，需定期检查**）
- README 标注最后更新：2026-03-29

## 要看更多

- `README.md` —— 完整配置步骤（Fork → 配 Secrets → 建 workflow → 运行）、三种推送方式、
  企业微信 / 邮箱推送配置示例、使用声明
