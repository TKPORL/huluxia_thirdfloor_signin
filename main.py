import time
import sys
from signin import HuluxiaSignin
import os
from logger import logger

# 检查环境变量
accounts_str = os.getenv('ACCOUNTS')
if not accounts_str:
    logger.error("环境变量 ACCOUNTS 未设置")
    raise ValueError("环境变量 ACCOUNTS 未设置")

# 解析账号信息，去除空行和异常格式
accounts = []
for acc in accounts_str.split('\n'):
    try:
        phone, password = acc.split(',')
        accounts.append((phone.strip(), password.strip()))
    except ValueError:
        logger.warning(f"账号信息格式不正确：{acc}")

# 实例化 HuluxiaSignin 类
huluxia_signin_obj = HuluxiaSignin()

# 遍历账号进行签到
failed = 0
for phone, password in accounts:
    try:
        huluxia_signin_obj.huluxia_signin(phone, password)
        logger.info(f"账号 {phone} 签到成功")
    except Exception as e:
        failed += 1
        logger.error(f"账号 {phone} 签到失败: {e}")
    time.sleep(60)  # 每次签到间隔60秒

# 有账号失败就让任务以失败状态结束，这样 GitHub 会发邮件提醒，不会再悄悄断签
if accounts and failed == len(accounts):
    logger.error("全部账号签到失败")
    sys.exit(1)
