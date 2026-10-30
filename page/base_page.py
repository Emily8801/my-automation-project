from typing import Self
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.settings import BASE_URL, WAIT_TIMEOUT
from common.logger import get_logger
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select


class BasePage:
    """所有页面对象的基类，封装通用的浏览器操作"""
    def __init__(self, driver):
        self.driver = driver
        self.logger = get_logger("PageObject")
        self.default_timeout = WAIT_TIMEOUT
        self.wait = WebDriverWait(self.driver, self.default_timeout)

    def wait_for_page_load(self, timeout=30, poll_frequency=0.5):
        WebDriverWait(self.driver, timeout, poll_frequency=poll_frequency).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return self

    def open(self, url):
        """打开指定 URL
        - test_login 传 "/coachportal"(BASE_URL 已含 /coachportal/）→ /coachportal//coachportal
        现规则：完整 http(s) URL 直接打开，相对路径才与 BASE_URL 拼接。
        """
        if url.startswith(("http://", "https://")):
            self.driver.get(url)
        else:
            self.driver.get(f"{BASE_URL.rstrip('/')}/{url.lstrip('/')}")
        return self

    def find_element(self, locator, desc="元素", timeout=None):
        """
        统一显式等待封装
        :param locator: 元素定位器 (By.XPATH, "//div")
        :param desc: 元素描述，用于日志和异常提示# 假设有人之前这样调用（第二个位置参数是 desc）
self.find_element(LOGIN_BTN, "登录按钮")

# 如果你把定义换成 (self, locator, timeout=None, desc="元素")
# 这句调用就变成把 "登录按钮" 塞给了 timeout → 逻辑全错，还不一定报错
        :param timeout: 自定义超时, None则使用默认值
        """
        #self.logger.info(f"🔍查找{desc}:{locator}")
        # 兼容旧调用

        wait_time = timeout if timeout is not None else self.default_timeout
        try:
            element = WebDriverWait(self.driver,wait_time).until(
                EC.presence_of_element_located(locator),
            )
            self.logger.info(f"✅{desc}查找成功")
            return element
        except TimeoutException:
            raise TimeoutException(f"❌ {desc}在{wait_time}秒内未找到:{locator}") from None

    def find_elements(self, locator, timeout=None):
        """查找多个元素，找不到时安全返回空列表"""
        wait_time = timeout or self.default_timeout
        try:
            elements = WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_any_elements_located(locator)
            )
            # 兼容 Selenium 4 可能返回 False 的情况
            return elements if isinstance(elements, list) else []
        except TimeoutException:
            return []

    # ========== 获取元素文本 ==========
    def get_text(self, locator, timeout=None):
        """
        等待元素可见后获取其文本内容
        :return: str 元素文本，去除首尾空白
        """
        element = self.find_element(locator, timeout=timeout)
        return element.text.strip()

    def click(self, locator, desc="button", timeout=None):
        """等待元素可点击后执行点击"""
        wait_time = timeout or self.default_timeout
        try:
            element = WebDriverWait(self.driver,wait_time).until(
            EC.element_to_be_clickable(locator)
            )
            element.click()
        except TimeoutException:
            raise TimeoutException(f"❌{desc}在{wait_time}秒内不可点击：{locator}")

        return self

    def safe_click(self, locator, timeout=None):
        wait_time = timeout or self.default_timeout
        element = WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable(locator)
        )
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)
        return self

    def get_attribute(self, locator, attr, timeout=None):
        """获取元素属性，支持自定义超时"""
        element = self.find_element(locator, timeout=timeout)
        return element.get_attribute(attr)

    def input_text(self, locator, text, desc="输入框"):
        """清空并输入文本"""
        self.logger.info(f"⌨️ 输入{desc}:{'*' * len(text)}")
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
        return self

    def press_enter(self, locator):
        element = self.find_element(locator)
        element.send_keys(Keys.ENTER)
        return self

    def accept_alert(self, timeout=5):
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert.accept()
        except TimeoutException:
            pass  # self.logger.warning(f"等待{timeout}s,没有alert跳出，跳过accept")

    def switch_to_client_frame(self, frame_locator=None):
        """✅ 补充：切换到 iframe, 如果传入了 locator 则切换到指定 iframe, 否则切回主文档"""
        self.driver.switch_to.default_content()
        if frame_locator:  # 先切回主页，防止嵌套 iframe 导致找不到
            iframe = self.find_element(frame_locator)
            self.driver.switch_to.frame(iframe)

    # def wait_for_element_visible(self, locator, timeout=None):
    #     """
    #     等待元素变为可见状态（用于流程阻塞，找不到会抛出 TimeoutException）
    #     """
    #     wait_time = timeout or self.default_timeout
    #     WebDriverWait(self.driver, wait_time).until(
    #         EC.visibility_of_element_located(locator)
    #     )
    #     return True

    def is_element_visible(self, locator, timeout=None):
        """
        ✅ 核心补充：判断元素是否可见，找不到返回 False,不抛异常(专用于 if 判断和断言)
        """
        wait_time = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def select_dropdown(self, locator, value, desc="下拉框"):
        """通用下拉框选择(按value)"""
        el = self.find_element(locator, desc=desc)
        Select(el).select_by_value(value)
        self.logger.info(f"🔽{desc}选中value:{value}")
        return self

    def switch_to_new_window(self):
        """切换到最新打开的新窗口（如从商品列表点击详情页）"""
        all_handles = self.driver.window_handles
        new_handle = all_handles[-1]
        self.driver.switch_to.window(new_handle)
