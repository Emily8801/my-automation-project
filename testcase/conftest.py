import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pytest

from common.logger import get_logger

# 统一锚定项目根目录，避免从不同工作目录启动时路径漂移
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_ROOT / "report" / "report.html"
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"

logger = get_logger("fixture")


def _get_driver(item):
    """兼容两种用例风格获取 driver

    - pytest 风格:driver 由 fixture 注入，存在于 item.funcargs
    - unittest 风格:driver 挂在 TestCase 实例的 self.driver 上，通过 item.instance 获取
    """
    try:
        driver = item.funcargs.get("driver")
    except AttributeError:
        driver = None
    if driver is None:
        driver = getattr(getattr(item, "instance", None), "driver", None)
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图并记录日志"""
    outcome = yield
    report = outcome.get_result()

    # 仅在执行阶段失败时触发（排除 setup/teardown 失败）
    if report.when != "call" or not report.failed:
        return

    # 🟠 修复：原代码只从 item.funcargs 取 driver，但现有用例全部是 unittest.TestCase，
    #    driver 在 self.driver 上，funcargs 里没有 → 截图永远不会触发。
    driver = _get_driver(item)
    if driver is None:
        logger.warning(f"用例 {item.name} 执行失败，但未获取到 driver,跳过截图")
        return

    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        screenshot_path = SCREENSHOT_DIR / f"{item.name}_{timestamp}.png"
        driver.save_screenshot(str(screenshot_path))
        logger.error(f"📸 测试失败截图已保存:{screenshot_path}")
    except Exception as e:
        # 截图失败不能影响测试结果的收集
        logger.error(f"❌ 失败截图保存失败: {e}")


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionfinish(session, exitstatus):
    """测试会话结束后自动发送邮件"""
    yield  # 等待所有测试完成

    # 可选：只在有失败时才发送，取消下面两行注释即可
    # if session.testsfailed == 0:
    #     return

    total = session.testscollected
    failed = session.testsfailed

    # 🟡 邮件的发件人/收件人/SMTP 支持环境变量覆盖，避免散落在代码里
    sender = os.getenv("QQ_MAIL_FROM", "395725813@qq.com")
    recipients = [
        addr.strip()
        for addr in os.getenv("QQ_MAIL_TO", "receiver@example.com").split(",")
        if addr.strip()
    ]

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = f"自动化测试报告 - 通过：{total - failed} 失败：{failed}"

    # 邮件正文
    body = f"本次共执行{total}条用例。失败{failed}条。\n详见附件报告。"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # 添加 HTML 报告附件
    # 🔴 修复：未生成报告（例如直接跑 unittest、或 pytest-html 未安装）时 open 会 FileNotFoundError，
    #    导致整个 sessionfinish 崩溃，这里先做存在性判断
    if REPORT_PATH.exists():
        part = MIMEBase("application", "octet-stream")
        part.set_payload(REPORT_PATH.read_bytes())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="report.html")
        msg.attach(part)
    else:
        logger.warning(f"未找到测试报告 {REPORT_PATH}，将只发送文本邮件")

    auth_code = os.getenv("QQ_MAIL_AUTH_CODE", "")
    if not auth_code:
        logger.error("❌ 未设置 QQ_MAIL_AUTH_CODE 环境变量，跳过邮件发送")
        return

    smtp_host = os.getenv("QQ_MAIL_SMTP", "smtp.qq.com")
    try:
        smtp_port = int(os.getenv("QQ_MAIL_SMTP_PORT", "465"))
    except ValueError:
        smtp_port = 465

    # 🔴 修复：原代码 server.login(...,"你的授权码") 硬编码占位符，与"禁止硬编码密码"的约定冲突
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender, auth_code)
            server.sendmail(sender, recipients, msg.as_string())
        logger.info("✅ 测试报告邮件发送成功")
    except Exception as e:
        logger.error(f"❌ 邮件发送失败: {e}")


# 🟠 结构说明：原文件中的 session 级 driver fixture 和 login fixture 已删除。
#    当前所有用例均为 unittest.TestCase，driver 由各类 setUp 自建、登录由 LoginBase 完成，
#    这两个 fixture 没有任何用例使用，属于死代码；保留会让"两套驱动/登录机制"并存。
#    若后续改成 pytest 风格用例，可在使用处重新引入对应 fixture。
