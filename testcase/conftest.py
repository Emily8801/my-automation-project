
import os
import pytest
from common.driver_factory import get_driver
from page.login_page import LoginPage
from config.settings import BASE_URL, USERNAME, PASSWORD
from common.logger import get_logger
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = get_logger("fixture")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item,call):
    """测试失败时自动截图并记录日志"""
    outcome = yield
    report = outcome.get_result()

    # 仅在执行阶段失败时触发（排除setup/teardown失败）
    if report.when =="call" and report.failed:
        # 🟠 结构问题：现有用例全部是 unittest.TestCase（driver 存在 self.driver 上），
        #    不是 pytest fixture 注入，item.funcargs 里通常没有 "driver"，因此这段截图逻辑
        #    对这些用例永远不会生效。要么改用 pytest 风格（fixture + 不用 unittest），
        #    要么在这里兼容 isinstance(item, unittest.TestCase) 后取 item.cls/实例。
        driver = item.funcargs.get("driver") # 获取fixture中的driver
        if driver:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            screenshot_dir ="screenshots"
            os.makedirs(screenshot_dir,exist_ok=True)

            screenshot_path = os.path.join(
                screenshot_dir,
                f"{item.name}_{timestamp}.png"
            )
            driver.save_screenshot(screenshot_path)
            logger.error(f"📸 测试失败截图已保存:{screenshot_path}")

        # 【可选】如果后续接入Allure，取消下面注释即可自动附加到报告
        # import allure
        # allure.attach.file(screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)

@pytest.fixture(scope="session")
def driver():
    """整个测试会话共享一个浏览器实例"""
    if os.environ.get("PYTEST_XDIST_WORKER"):
        pytest.skip("session-scoped driver is not supported in parallel mode."
                    "please use function-scoped driver or run without xdist." )
    d= get_driver()
    yield d
    d.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionfinish(session, exitstatus):
    """测试会话结束后自动发送邮件"""
    yield  # 等待所有测试完成

    report_path = "report/report.html"

    # 可选：只在有失败时才发送
    # if session.testsfailed == 0:
    #     return

    msg = MIMEMultipart()
    msg["From"] = "395725813@qq.com"
    msg["To"] = "receiver@example.com"
    # 🔴 修复：pytest 的 Session 属性名是 testscollected（带 s），原代码写成 session.testcollected，
    #    进入 sessionfinish 时会 AttributeError
    total = session.testscollected
    failed = session.testsfailed
    msg["Subject"] = f"自动化测试报告 - 通过：{total - failed} 失败：{failed}"

    # 邮件正文
    body = f"本次共执行{total}条用例。失败{failed}条。\n详见附件报告。"
    msg.attach(MIMEText(body,"plain","utf-8"))

    # 添加 HTML 报告附件
    # 🔴 修复：未生成报告（例如直接跑 unittest、或 pytest-html 未安装）时 open 会 FileNotFoundError，
    #    导致整个 sessionfinish 崩溃，这里先做存在性判断
    if os.path.exists(report_path):
        with open(report_path,"rb")as f:
            part = MIMEBase("application","octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename = "report.html")
            msg.attach(part)
    else:
        logger.warning(f"未找到测试报告 {report_path}，将只发送文本邮件")

    # 发送
    auth_code = os.environ.get ("QQ_MAIL_AUTH_CODE", "")
    if not auth_code:
        logger.error("❌未设置QQ_MAIL_AUTH_CODE环境变量，跳出邮件发送")
        return
    # 🔴 修复：原代码 server.login(...,"你的授权码") 硬编码占位符，与 settings.py 中
    #    "禁止在代码中 hard code 密码" 的约定冲突，且上一步已读取 auth_code 却没用上
    try:
        with smtplib.SMTP_SSL("smtp.qq.com",465) as server:
            server.login("395725813@qq.com",auth_code)
            server.sendmail(msg["From"],msg["To"].split(","),msg.as_string())
        logger.info("✅ 测试报告邮件发送成功")
    except Exception as e:
        logger.error (f"❌ 邮件发送失败: {e}")

@pytest.fixture(scope="function")
def login(driver):
    """每个测试函数前自动登录

    🟠 结构问题：现有 testcase 全部是 unittest.TestCase（setUp 里自建 driver 并登录），
       没有任何用例声明使用本 fixture，因此它是死代码；conftest 与 unittest 两套驱动/登录
       机制并存，维护时容易误解。建议二选一统一。
    """
    # 1. 清除上一轮测试残留状态
    driver.delete_all_cookies()
    # 2. 执行登录并验证结果
    page=LoginPage(driver)
    page.open(BASE_URL)
    try:
        page.login(USERNAME,PASSWORD)
        assert page.is_logged_in(), "login failed:user not authenticated"
    except AssertionError:
        raise
    except Exception as e:
        pytest.fail(f"Login fixture setup failed:{e}")




    # ip = LoginPage(driver)
    # ip.open(BASE_URL)
    # ip.login("admin","password")
    # return ip
