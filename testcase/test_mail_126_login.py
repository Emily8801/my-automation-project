import unittest

from common.driver_factory import get_driver
from config.settings import BROWSER, MAIL_PASS, MAIL_USER
from page.mail_126_page import Mail126Page


@unittest.skipUnless(MAIL_USER and MAIL_PASS, "未配置 MAIL_USER / MAIL_PASS，跳过 126 邮箱登录用例")
class TestMail126Login(unittest.TestCase):
    """126 邮箱登录：打开登录页 → 输入账号密码 → 进入邮箱主页"""

    def setUp(self):
        self.driver = get_driver(BROWSER)
        self.mail_page = Mail126Page(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_login_success(self):
        """测试登录成功并进入邮箱主页"""
        (self.mail_page
         .open_login_page()
         .login(MAIL_USER, MAIL_PASS))
        self.assertTrue(
            self.mail_page.is_logged_in(timeout=20),
            "126 邮箱登录失败：未进入邮箱主页"
        )


if __name__ == "__main__":
    unittest.main()
