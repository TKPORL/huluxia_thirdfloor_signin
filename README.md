# 葫芦侠三楼每日自动签到 🚀

> **💯38个版块精准签到**
> 
> **🗂️多账号支持**
>
> 
> **🕗每日定时执行**
> 
> **❇️不影响葫芦侠使用**

###### **最后更新日期：2026年03月29日 02点33分**

### 注意⚠️
**使用前请先将葫芦侠账号解除QQ绑定，否则会出现“账号保护已开启，请使用QQ登录”问题。**

### 配置步骤 🛠️

1. **Fork本项目**：
   - 点击右上角`Fork`按钮，将本项目Fork到你的仓库。

2. **设置Github Secrets**：
   - 进入你的仓库，点击`Settings`。
   - 选择`Secrets and variables` -> `Actions`。
   - 点击`New repository secret`，添加名为`NOTIFIER_TYPE`的Secret，值既为可选的推送方式：`wechat`(企业微信群机器人推送)、`email`(邮箱推送)和`none`(默认不推送签到消息）。详情请参考下方消息推送方式。
   - 点击`New repository secret`，添加名为`ACCOUNTS`的Secret，值为你的账号信息，格式如下：<br/>
   [手机号][英文逗号][密码]
     ```
     account1,password1
     account2,password2
     ```

3. **在Github Actions中创建```main.yml```**：
   - 进入你的仓库，点击`Actions`。
   - 点击`New workflow`，选择`Set up a workflow yourself`。
   - 将以下内容粘贴到 `main.yml` 文件中：
     ```yaml
     name: huluxia_signin
     on:
       schedule:    # 定时触发
         - cron: '0 16 * * *'  # 24点
       workflow_dispatch:  # 支持手动触发
     jobs:
       build:
         runs-on: ubuntu-latest
         steps:
           - name: Checkout
             uses: actions/checkout@v7
           - name: '初始化python环境'
             uses: actions/setup-python@v7
             with:
                python-version: 3.10.11
     ```

     > ⚠️ action 版本不要用 `@v3` / `@v4`。GitHub 会定期下线旧版的 Node 运行时，
     > 旧版本会直接启动失败（2026-11-05 本项目连续断签 10 天就是这个原因）。
     > 完整可用的 workflow 以仓库里实际的 `.github/workflows/main.yml` 为准。

4. **运行Github Actions**：
   - 设置好的 schedule 将会每日自动执行签到任务。
   - 你也可以随时进入 `Actions` 页面，选择 `huluxia_signin` workflow，然后点击 `Run workflow` 手动触发签到任务。

### 断签防护与告警 ⚠️（本 Fork 新增）

签到中断过两次，都是几个月后才发现的。现在有三层防护：

| 层 | 机制 | 兜住什么 |
|---|---|---|
| 1 | 保活提交 | 仓库 60 天无提交时 GitHub 会停用定时任务 |
| 2 | 失败告警 `alert_failure.py` | 任意步骤失败立即发邮件 / 企微 |
| 3 | 心跳监控 healthchecks.io | **任务压根没跑**也会告警 |

#### 配置心跳监控（强烈建议，5 分钟）

前两层有个共同盲区：**任务如果根本没被触发，什么都不会发**。GitHub 自己的失败邮件只在「跑了但失败」时才发。

1. 打开 https://healthchecks.io ，用邮箱注册（免费，不要信用卡）
2. 新建一个 Check：Period 填 `1 day`，Grace Time 填 `6 hours`
3. 复制它给你的 Ping URL，形如 `https://hc-ping.com/xxxxxxxx-xxxx-xxxx`
4. 去仓库 `Settings → Secrets and variables → Actions`，新建 Secret 名为 `HEALTHCHECK_URL`，值粘贴这个 URL

配好后：签到成功会上报正常信号；失败会上报 `/fail` 立即告警；**超过 30 小时完全没动静也会发邮件**。

> 注意：`HEALTHCHECK_URL` 没配置时，workflow 会跳过心跳上报，不会报错——但也失去了第三层保护。

### 消息推送方式 📢

目前支持**企业微信群机器人推送**、**邮箱推送**和**不推送**三种方式。
1. **企业微信群机器人推送**：

   - 配置`WECHAT_ROBOT_URL`环境变量，值为企业微信群机器人的Webhook地址，具体获取方法请参考[企业微信群机器人文档](https://open.work.weixin.qq.com/help2/pc/14931?person_id=1)。
   - 该推送方式需要在Github Secrets中设置`WECHAT_ROBOT_URL`变量。

2. **邮箱推送**：

   - 如果你希望通过邮箱进行推送，可以设置`EMAIL_CONFIG`环境变量，格式如下：
     ```json
     {
         "username": "your_email@qq.com",
         "auth_code_or_password": "your_email_auth_code",
         "sender_email": "your_email@qq.com",
         "recipient_email": "recipient_email@qq.com"
     }
     ```
     配置完`EMAIL_CONFIG`后，程序将自动通过SMTP发送推送通知
3. **不推送**：
   - 如果你不希望推送签到消息，可以设置`NOTIFIER_TYPE`环境变量为`none`。
   
如果你有其他推送需求或希望增加其他推送方式，欢迎提交PR或提出Issue。

### 企业微信群机器人推送效果图 📸

![企业微信群机器人推送效果图](src/wechat.jpg)

### 邮箱推送效果图 📸
![邮箱推送推送效果图](src/email.png)


### 使用声明 ⚠️

本项目仅供学习和交流使用，请勿用于任何商业用途。使用者需自行承担因使用本项目而产生的任何风险和责任。

[![Star History Chart](https://api.star-history.com/svg?repos=BoltLv4215/huluxia_thirdfloor_signin&type=Date)](https://star-history.com/#BoltLv4215/huluxia_thirdfloor_signin&Date)<br/>

**🚩By [BoltLv4215](https://github.com/BoltLv4215 "点个Star和Follow吧！")**<br/>

