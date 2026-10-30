"""登录页面对象（Playwright 版）。

与 Selenium 版 login_page.py 的定位器一一对应，只是写法从
(By.XPATH, "//input[@class='logininput' and @name='email']")
换成了 CSS：input.logininput[name='email']
"""

from config.settings import BASE_URL
from page.pw_base_page import PWBasePage


class PWLoginPage(PWBasePage):
    """登录页面对象"""

    USERNAME_INPUT = "input.logininput[name='email']"
    PASSWORD_INPUT = "input.logininput[name='password']"
    TERMS_CHECKBOX = "img.termsChecked"
    SUBMIT_BUTTON = "input.submit_button"
    USER_AVATAR = "div.user-avatar"

    def login(self, username, password):
        """打开站点并完成登录"""
        self.open(BASE_URL)
        self.fill(self.page.locator(self.USERNAME_INPUT), username, desc="用户名")
        self.fill(self.page.locator(self.PASSWORD_INPUT), password, desc="密码")

        # 🟠 条款勾选框是一个 <img>，没有 checked 属性，
        #    这里沿用旧逻辑：可见就点一下。若默认已勾选，点击会取消勾选，需要现场确认。
        terms = self.page.locator(self.TERMS_CHECKBOX)
        if self.is_visible(terms, timeout=3000):
            self.click(terms.first, "同意条款")

        self.click(self.page.locator(self.SUBMIT_BUTTON), "登录按钮")
        return self

    def is_logged_in(self, timeout=15000):
        """登录后才出现的用户头像可见，说明登录成功"""
        return self.is_visible(self.page.locator(self.USER_AVATAR), timeout=timeout)
