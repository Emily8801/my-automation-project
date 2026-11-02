import unittest
from common.driver_factory import get_driver
from page.login_coach_page import LoginPage
from config.settings import BASE_URL, BROWSER, USERNAME, PASSWORD


class LoginBase(unittest.TestCase):
    """登录前置基类：只做 driver 初始化 + 登录，不包含 test_ 方法，供其它用例继承。"""
    def setUp(self):
        self.driver = get_driver(BROWSER)
        self.login_page = LoginPage(self.driver)
        (self.login_page
         .open(BASE_URL)
         .wait_for_page_load()
         .login(USERNAME, PASSWORD)
         .accept_alert())
        self.assertTrue(self.login_page.is_logged_in(), "登录失败")

    def tearDown(self):
        if self.driver:
            self.driver.quit()


class TestLogin(LoginBase):
    """登录成功用例"""
    def test_login_success(self):
        """测试登录成功"""
        self.assertTrue(
            self.login_page.is_logged_in(),
            "登录失败：未检测到已登录状态"
        )


if __name__ == "__main__":
    unittest.main()
