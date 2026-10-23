from selenium.webdriver.common.by import By
from page.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


class LoginPage(BasePage):
    """登录页面对象"""
    # 🟡 原 FROM_LOAD 与 USERNAME_INPUT 定位符完全一样且没有任何地方使用（笔误），已删除
    USERNAME_INPUT = (By.XPATH, "//input[@class = 'logininput' and @name = 'email']")
    PASSWORD_INPUT = (By.XPATH, "//input[@class = 'logininput' and @name = 'password']")
    # 🟠 风险：该元素是 <img> 且 class 名为 termsChecked（"已勾选"语义），
    #    login() 每次都无条件点击，若进入页面时已勾选，点击反而会取消勾选导致登录失败。
    #    实际项目中需按元素状态判断后再点击，或改用真正的 checkbox 定位。
    TERMS_CHECKBOX = (By.XPATH, "//img[@class = 'termsChecked']")
    SUBMIT_BUTTON = (By.XPATH, "//input[@class = 'submit_button']")

    # 🟠 风险：登录成功特征的定位符是占位值（原注释"需根据实际项目替换"），
    #    若实际页面没有 div.user-avatar，is_logged_in() 永远返回 False，所有用例都会失败。
    USER_AVATAR = (By.XPATH, "//div[@class='user-avatar']")

    def wait_for_page_load(self, timeout=30, poll_frequency=0.5):
        """等待登录表单加载完成"""
        # 🟡 原 lambda 里的 isinstance(d, WebDriver) 恒为 True（d 必然是 WebDriver），是无效判断，已简化
        WebDriverWait(self.driver, timeout, poll_frequency=poll_frequency).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return self

    def login(self, username, password):
        """执行完整的登录动作"""
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click(self.TERMS_CHECKBOX)
        self.click(self.SUBMIT_BUTTON)
        return self

    def is_logged_in(self):
        try:
            # 使用显式等待检查登录后才出现的元素，避免页面跳转未完成就判定失败
            self.find_element(self.USER_AVATAR, timeout=10, desc="用户头像")
            return True
        # 🟠 修复：原代码 except Exception 会吞掉脚本错误、驱动异常等所有问题，
        #    这里只捕获"元素等待超时"这一预期内的失败
        except TimeoutException:
            return False
