"""Swag Labs 登录页 Page Object。

职责边界：只封装元素定位与原子操作（输入 / 点击 / 取文本 / 取 URL / 状态查询），
不包含任何断言，所有断言留在测试用例层。
"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 登录页地址
BASE_URL = "https://www.saucedemo.com/"

# 统一显式等待超时时间（秒）
DEFAULT_TIMEOUT = 10


class LoginPage:
    """登录页：定位 + 原子操作。"""

    # ---------- 元素定位：By.ID 优先，其次 By.CSS_SELECTOR，禁止绝对 XPath ----------
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    # 错误提示条
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")
    # 登录成功后的商品列表容器
    INVENTORY_CONTAINER = (By.CSS_SELECTOR, "[data-test='inventory-container']")

    def __init__(self, driver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    # ---------------- 私有等待封装：任何操作前先等元素就绪 ----------------
    def _wait_clickable(self, locator: tuple) -> WebElement:
        """等待元素可见且可交互，返回元素本身（用于输入 / 点击）。"""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def _wait_visible(self, locator: tuple) -> WebElement:
        """等待元素可见，返回元素本身（用于取文本 / 判断展示）。"""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _is_displayed(self, locator: tuple) -> bool:
        """等待元素可见后返回展示状态；超时视为不可见（不做断言，仅返回结果）。"""
        try:
            return self._wait_visible(locator).is_displayed()
        except TimeoutException:
            return False

    # ---------------- 原子操作 ----------------
    def open(self) -> None:
        """打开登录页。"""
        self.driver.get(BASE_URL)

    def input_username(self, username: str) -> None:
        """输入用户名：先清空，避免上一步残留文本干扰。"""
        element = self._wait_clickable(self.USERNAME_INPUT)
        element.clear()
        element.send_keys(username)

    def input_password(self, password: str) -> None:
        """输入密码：先清空，避免上一步残留文本干扰。"""
        element = self._wait_clickable(self.PASSWORD_INPUT)
        element.clear()
        element.send_keys(password)

    def click_login(self) -> None:
        """点击登录按钮（先等可点击，防止元素未渲染完成就点击）。"""
        self._wait_clickable(self.LOGIN_BUTTON).click()

    def submit_login(self, username: str, password: str) -> None:
        """组合操作：填账号 → 填密码 → 点登录。"""
        self.input_username(username)
        self.input_password(password)
        self.click_login()

    # ---------------- 取文本 / 取 URL ----------------
    def get_current_url(self) -> str:
        """获取当前页面 URL。"""
        return self.driver.current_url

    def get_error_message(self) -> str:
        """获取错误提示文案（等待可见后再取文本，去掉首尾空白）。"""
        return self._wait_visible(self.ERROR_MESSAGE).text.strip()

    # ---------------- 状态查询：只返回结果，断言交给用例层 ----------------
    def is_error_visible(self) -> bool:
        """错误提示条是否可见。"""
        return self._is_displayed(self.ERROR_MESSAGE)

    def is_login_button_visible(self) -> bool:
        """登录按钮是否可见（用于判断是否仍停留在登录页）。"""
        return self._is_displayed(self.LOGIN_BUTTON)

    def is_inventory_container_visible(self) -> bool:
        """商品列表容器是否可见（登录成功的页面级标志）。"""
        return self._is_displayed(self.INVENTORY_CONTAINER)
