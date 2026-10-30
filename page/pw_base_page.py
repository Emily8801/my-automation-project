"""Playwright 版页面对象基类（对应 Selenium 版的 BasePage）。

Selenium 与 Playwright 的核心差异：
    1. 定位器：Selenium 用 (By.ID, "xxx") 二元组，Playwright 直接用 CSS / XPath 字符串
    2. 等待：Selenium 要写 WebDriverWait，Playwright 的 click/fill 自带自动等待
    3. iframe：Selenium 要 switch_to.frame，Playwright 用 frame_locator 拿到作用域，不用“切”
    4. 弹窗：Selenium 要 switch_to.alert，Playwright 用 page.on("dialog", ...) 事件监听
"""

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from common.logger import get_logger


class PWBasePage:
    """把常用的浏览器动作封装成方法，供各页面对象继承"""

    def __init__(self, page):
        self.page = page
        self.logger = get_logger("PWPageObject")
        # 弹窗统一自动点“确定”。同一个 page 只注册一次，
        # 否则多次注册会让同一个弹窗被 accept 多次而报错。
        if not getattr(page, "_dialog_hooked", False):
            page.on("dialog", self._accept_dialog)
            page._dialog_hooked = True

    @staticmethod
    def _accept_dialog(dialog):
        """alert / confirm 一律接受"""
        dialog.accept()

    # ========== 导航 ==========
    def open(self, url):
        self.logger.info(f"🌐 打开页面：{url}")
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    # ========== iframe ==========
    def frame(self, frame_selector):
        """返回 iframe 内的定位作用域，后续用 frame.locator(...) 找元素"""
        return self.page.frame_locator(frame_selector)

    # ========== 原子操作 ==========
    def click(self, target, desc="按钮", timeout=30000):
        """target 是已经定位好的 Locator 对象（Playwright 会自动等到可点击）"""
        self.logger.info(f"🖱️ 点击{desc}")
        target.click(timeout=timeout)
        return self

    def fill(self, target, text, desc="输入框", timeout=30000):
        """fill = 清空 + 输入，等价于 Selenium 的 clear() + send_keys()"""
        text = str(text)
        self.logger.info(f"⌨️ 输入{desc}:{'*' * len(text)}")
        target.fill(text, timeout=timeout)
        return self

    def get_value(self, target, timeout=30000):
        """读输入框的 value（对应 Selenium 的 get_attribute("value")）"""
        target.wait_for(state="visible", timeout=timeout)
        return target.input_value()

    def get_text(self, target, timeout=30000):
        """读元素的可视文本（对应 Selenium 的 element.text）"""
        target.wait_for(state="visible", timeout=timeout)
        return target.inner_text().strip()

    def is_visible(self, target, timeout=5000):
        """元素在超时内可见返回 True，否则 False（不抛异常）"""
        try:
            target.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False
