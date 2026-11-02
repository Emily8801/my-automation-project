from selenium.webdriver.common.by import By
from page.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


class LoginPage(BasePage):
    """登录页面对象"""
    USERNAME_INPUT = (By.XPATH, "//input[@class = 'logininput' and @name = 'email']")
    PASSWORD_INPUT = (By.XPATH, "//input[@class = 'logininput' and @name = 'password']")
    TERMS_CHECKBOX = (By.XPATH, "//img[@class = 'termsChecked']")
    SUBMIT_BUTTON = (By.XPATH, "//input[@class = 'submit_button']")
    USER_AVATAR = (By.XPATH, "//div[@class='user-avatar']")

    # ========== 业务操作方法 ==========
    def login(self, username, password):
        """执行完整的登录动作"""
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        checkbox = self.find_element(self.TERMS_CHECKBOX)
        if checkbox.get_attribute("checked") != "true":
            self.click(self.TERMS_CHECKBOX)
        self.click(self.SUBMIT_BUTTON)
        return self
    
    def is_logged_in(self):
        try:
            # 使用显式等待检查登录后才出现的元素，避免页面跳转未完成就判定失败
            self.find_element(self.USER_AVATAR, timeout=10, desc="用户头像")
            return True
        except TimeoutException:
            return False
