from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import MAIL_URL
from page.base_page import BasePage


class Mail126Page(BasePage):
    """126 邮箱登录页

    126/163 邮箱登录页改版过程中出现过两种形态：
    1. 旧版：表单在 iframe 里（#loginIframe / #x-URS-iframe）；
    2. 新版：表单直接渲染在主文档。
    所以账号/密码/按钮都用"候选定位器"依次尝试，不写死单一选择器。
    """

    LOGIN_URL = MAIL_URL

    # 登录框所在 iframe（不存在时按主文档处理）
    LOGIN_IFRAME_CANDIDATES = (
        (By.ID, "loginIframe"),
        (By.ID, "x-URS-iframe"),
        (By.XPATH, "//iframe[contains(@id,'loginIframe') or contains(@id,'URS-iframe')]"),
    )

    # 账号输入框
    ACCOUNT_INPUT_CANDIDATES = (
        (By.XPATH, "//input[@name='email']"),
        (By.XPATH, "//input[contains(@placeholder,'邮箱') or contains(@placeholder,'账号')]"),
        (By.CSS_SELECTOR, "input#mail"),
        (By.CSS_SELECTOR, "input[type='text']"),
    )

    # 密码输入框
    PASSWORD_INPUT_CANDIDATES = (
        (By.XPATH, "//input[@name='password']"),
        (By.CSS_SELECTOR, "input[type='password']"),
    )

    # 登录按钮
    LOGIN_BUTTON_CANDIDATES = (
        (By.ID, "dologin"),
        (By.XPATH, "//a[contains(@class,'loginBtn') or @id='dologin']"),
        (By.XPATH, "//button[contains(normalize-space(.),'登录')]"),
    )

    # 服务条款勾选框（新版登录页可能出现，未勾选会导致登录被拦截）
    AGREEMENT_CHECKBOX_CANDIDATES = (
        (By.CSS_SELECTOR, "input#un-login-agree"),
        (By.XPATH, "//input[@type='checkbox' and contains(@class,'agree')]"),
    )

    # 登录成功后邮箱主页左侧的收件箱入口
    INBOX_ENTRY = (By.XPATH, "//*[normalize-space(text())='收件箱']")

    # ========== 内部工具方法 ==========
    def _switch_into_login_frame(self):
        """登录框在 iframe 内则切进去，否则停留在主文档"""
        self.driver.switch_to.default_content()
        for locator in self.LOGIN_IFRAME_CANDIDATES:
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.frame_to_be_available_and_switch_to_it(locator)
                )
                self.logger.info(f"✅已切换到登录框 iframe:{locator}")
                return True
            except TimeoutException:
                self.driver.switch_to.default_content()
        self.logger.info("未发现登录 iframe，按主文档处理")
        return False

    def _find_first(self, candidates, desc, per_try_timeout=4):
        """按候选定位器顺序查找，返回第一个命中的元素"""
        for locator in candidates:
            try:
                return self.find_element(locator, desc=desc, timeout=per_try_timeout)
            except TimeoutException:
                self.logger.info(f"未命中定位器 {locator}，继续尝试下一个")
        raise TimeoutException(f"❌ {desc}未找到，已尝试全部候选定位器:{candidates}")

    def _click_first(self, candidates, desc, per_try_timeout=4):
        """按候选定位器顺序点击第一个可点击元素"""
        for locator in candidates:
            try:
                element = WebDriverWait(self.driver, per_try_timeout).until(
                    EC.element_to_be_clickable(locator)
                )
            except TimeoutException:
                self.logger.info(f"未命中定位器 {locator}，继续尝试下一个")
                continue
            try:
                element.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", element)
            self.logger.info(f"🖱️ 已点击{desc}:{locator}")
            return True
        raise TimeoutException(f"❌ {desc}不可点击，已尝试全部候选定位器:{candidates}")

    def _accept_agreement_if_present(self):
        """新版登录页可能要求勾选服务条款，勾选后才允许提交"""
        for locator in self.AGREEMENT_CHECKBOX_CANDIDATES:
            elements = self.find_elements(locator, timeout=1)
            if not elements:
                continue
            checkbox = elements[0]
            try:
                if checkbox.is_selected():
                    return True
                checkbox.click()
            except Exception:
                # 勾选框常被其它图层遮挡，直接点击失败时用 JS 点击兜底
                self.driver.execute_script("arguments[0].click();", checkbox)
            self.logger.info("☑️ 已勾选服务条款")
            return True
        return False

    # ========== 业务操作方法 ==========
    def open_login_page(self, url=None):
        """打开 126 邮箱登录页，并进入登录框所在上下文"""
        self.open(url or self.LOGIN_URL)
        self.wait_for_page_load()
        self._switch_into_login_frame()
        return self

    def login(self, username, password):
        """输入账号密码并提交登录"""
        self._accept_agreement_if_present()

        account_input = self._find_first(self.ACCOUNT_INPUT_CANDIDATES, "账号输入框")
        account_input.clear()
        account_input.send_keys(username)
        self.logger.info(f"⌨️ 输入126邮箱账号:{username}")

        password_input = self._find_first(self.PASSWORD_INPUT_CANDIDATES, "密码输入框")
        password_input.clear()
        password_input.send_keys(password)
        self.logger.info("⌨️ 输入126邮箱密码:******")

        self._click_first(self.LOGIN_BUTTON_CANDIDATES, "登录按钮")
        return self

    def is_logged_in(self, timeout=None):
        """判断是否进入邮箱主页：URL 跳到 js6 主框架，或出现左侧收件箱入口"""
        wait_time = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, wait_time).until(self._has_entered_inbox)
            self.logger.info("✅已进入126邮箱主页")
            return True
        except TimeoutException:
            self.logger.error(f"❌ {wait_time}秒内未进入邮箱主页，当前URL:{self.driver.current_url}")
            return False

    @staticmethod
    def _has_entered_inbox(driver):
        if "js6" in driver.current_url:
            return True
        try:
            return any(el.is_displayed() for el in driver.find_elements(*Mail126Page.INBOX_ENTRY))
        except Exception:
            # 登录过程中页面跳转/iframe 卸载时，find_elements 可能短暂报错
            return False
