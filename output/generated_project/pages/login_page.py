from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    URL = "https://www.saucedemo.com/"

    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "user-name")
        self.password_input = (By.ID, "password")
        self.login_button = (By.ID, "login-button")
        self.error_message = (By.CSS_SELECTOR, "[data-test='error']")

    def open(self):
        """打开登录页并等待用户名输入框可见"""
        self.driver.get(self.URL)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.username_input))

    def get_current_url(self):
        """获取当前页面 URL"""
        return self.driver.current_url

    def login(self, username, password):
        """登录方法"""
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.username_input)).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.login_button).click()

    def get_error_message(self):
        """获取错误信息"""
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.error_message)).text

    def wait_for_login_success(self):
        """等待登录成功"""
        # 登录成功后URL会变化
        WebDriverWait(self.driver, 10).until(EC.url_contains("inventory.html"))
