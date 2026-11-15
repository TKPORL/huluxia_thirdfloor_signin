"""
签到失败兜底告警。

设计约束（很重要）：
1. 只用标准库，不 import requests —— 因为本脚本可能在任何步骤失败后被调用，
   那时 pip install 可能根本没执行。
2. 必须由系统解释器 /usr/bin/python3 运行，不能依赖 actions/setup-python 装出来的 python。
3. 邮箱与企业微信两条通道都尝试，能发出去一条就算成功。
"""

import datetime
import json
import os
import smtplib
import urllib.request
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

RUN_URL = os.environ.get("RUN_URL", "").strip()
RUN_NUMBER = os.environ.get("RUN_NUMBER", "?").strip()
WORKFLOW_NAME = os.environ.get("WORKFLOW_NAME", "huluxia_signin").strip()
NOW_UTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

BODY = f"""葫芦侠自动签到本次执行失败。

工作流：{WORKFLOW_NAME}
运行编号：#{RUN_NUMBER}
运行时间：{NOW_UTC}
运行详情：{RUN_URL}

请点开上面的链接，红色叉号所在的那一步就是原因。

常见原因，按概率排序：
1. GitHub 平台变更，导致某个 action 版本失效（2026-11-05 那次就是这个）
2. 葫芦侠账号密码被修改，或账号被风控
3. 葫芦侠账号开启了 QQ 绑定保护（需先在 App 内解绑 QQ）
4. 葫芦侠接口地址或签名规则调整
5. GitHub Actions 额度用尽 / 仓库被限制

修复后，进入 Actions 页面点 Run workflow 手动跑一次即可立刻验证。
"""


def send_email() -> bool:
    raw = os.environ.get("EMAIL_CONFIG", "").strip()
    if not raw:
        print("未配置 EMAIL_CONFIG，跳过邮件告警")
        return False

    try:
        cfg = json.loads(raw)
    except Exception as exc:
        print(f"EMAIL_CONFIG 不是合法 JSON，跳过邮件告警：{exc}")
        return False

    username = cfg.get("username")
    auth_code = cfg.get("auth_code_or_password")
    recipient = cfg.get("recipient_email")
    sender = cfg.get("sender_email") or username

    if not (username and auth_code and recipient):
        print("EMAIL_CONFIG 字段不全（需要 username / auth_code_or_password / recipient_email），跳过邮件告警")
        return False

    try:
        msg = MIMEText(BODY, "plain", "utf-8")
        msg["From"] = formataddr((str(Header(sender, "utf-8")), sender))
        msg["To"] = formataddr((str(Header(recipient, "utf-8")), recipient))
        msg["Subject"] = Header(f"【签到失败】葫芦侠自动签到 #{RUN_NUMBER} 没有成功", "utf-8")

        smtp_server = cfg.get("smtp_server") or "smtp.qq.com"
        port = int(cfg.get("port") or 465)

        if port == 465:
            server = smtplib.SMTP_SSL(smtp_server, port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_server, port, timeout=30)

        with server:
            if port != 465:
                server.starttls()
            server.login(username, auth_code)
            server.sendmail(sender, [recipient], msg.as_string())

        print(f"失败告警邮件已发送至 {recipient}")
        return True
    except Exception as exc:
        print(f"邮件告警发送失败：{type(exc).__name__}: {exc}")
        return False


def send_wechat() -> bool:
    hook = os.environ.get("WECHAT_ROBOT_URL", "").strip()
    if not hook:
        print("未配置 WECHAT_ROBOT_URL，跳过企业微信告警")
        return False

    content = (
        f"**葫芦侠签到失败**\n"
        f"> 运行编号：#{RUN_NUMBER}\n"
        f"> 时间：{NOW_UTC}\n"
        f"> [点此查看失败详情]({RUN_URL})"
    )
    payload = json.dumps({"msgtype": "markdown", "markdown": {"content": content}}).encode("utf-8")

    try:
        req = urllib.request.Request(hook, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
        print("失败告警已推送到企业微信")
        return True
    except Exception as exc:
        print(f"企业微信告警发送失败：{type(exc).__name__}: {exc}")
        return False


def main():
    print(f"开始发送失败告警（运行 #{RUN_NUMBER}）")
    ok = send_email()
    ok = send_wechat() or ok

    if not ok:
        print("所有告警通道都不可用或被跳过，本次失败没有外发通知")
        print("请检查仓库 Secrets 中 EMAIL_CONFIG / WECHAT_ROBOT_URL 是否配置正确")


if __name__ == "__main__":
    main()
