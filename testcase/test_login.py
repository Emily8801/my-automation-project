import unittest
from common.driver_factory import get_driver
from page.login_page import LoginPage
from config.settings import BASE_URL, BROWSER, USERNAME, PASSWORD


class LoginBase(unittest.TestCase):
    """登录前置基类：只做 driver 初始化 + 登录，不包含 test_ 方法，供其它用例继承。

    🔴 结构问题修复：原 TestLogin 里唯一的用例 test_login_success 被整段注释掉了，
       而残留的 assertTrue 由于缩进落进了 tearDown 内（在 driver.quit() 之后执行），
       结果是：TestLogin 本身执行 0 条用例，且 tearDown 必然抛异常。
    """

    def setUp(self):
        self.driver = get_driver(BROWSER)
        self.login_page = LoginPage(self.driver)
        # 🔴 修复：原调用 open("/coachportal") 会与 BASE_URL 重复拼接成 .../coachportal//coachportal，
        #    现改为传完整 BASE_URL（BasePage.open 已支持绝对地址）
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
