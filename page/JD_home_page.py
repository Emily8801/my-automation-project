from selenium.webdriver.common.by import By
from page.base_page import BasePage
from page.JD_product_page import JDProductPage


class JDHomePage(BasePage):
    SEARCH_INPUT = (By.ID, "key")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "#search button.button_submit")

    # 🔴 FIX: 原 XPath 有多处语法错误：
    #   1. normalise-space() 拼写错误（少了一个 z）→ normalize-space()
    #   2. normalize-space() 后面缺少逗号，函数调用没传参数 → normalize-space(.)
    #   3. 用了中文右括号 ） → 英文 )
    #   4. 两个 contains 逻辑混乱，应该同时对同一个元素文本判断
    # 🟠 FIX: "原数第二版" 应为 "原书第二版"（"数" → "书"）
    TARGET_BOOK_LINK = (
        By.XPATH,
        "//a[contains(normalize-space(.),'软件测试') and contains(normalize-space(.),'原书第二版')]"
    )

    def open(self, url):
        """🟠 FIX: 重写 open 接收完整 URL，绕过 BasePage.open 拼接 BASE_URL 的逻辑。
        但这个设计不一致 —— 测试传入完整 URL 时 BasePage.open 会变成 BASE_URL + url，
        这里重写后用 self.driver.get(url) 直接打开，两种调用方式并存需要统一。"""
        self.driver.get(url)
        self.driver.maximize_window()
        return self

    def search_product(self, keyword):
        """🟠 FIX: 参数名 'keyboard' 看起来像拼写错误，应为 'keyword'（关键词）"""
        # 🟠 FIX: base_page 调整了参数顺序为 (locator, desc, timeout)，
        #         现在 self.find_element(self.SEARCH_INPUT, "搜索框") 中 "搜索框" 正确传给 desc
        input_el = self.find_element(self.SEARCH_INPUT, "搜索框")
        input_el.clear()
        input_el.send_keys(keyword)
        # 🟠 FIX: 同上，"搜索按钮" 正确传给 click 的 desc 参数
        self.click(self.SEARCH_BUTTON, "搜索按钮")
        return self

    def select_target_book(self) -> 'JDProductPage':
        self.click(self.TARGET_BOOK_LINK, "软件测试原书第二版")
        # 🔴 FIX: switch_to_new_window 原只存在于 base_page.py 的内部重复类中，
        #         外部 BasePage 没有这个方法，会 AttributeError。
        #         已修复 base_page.py 删除内部类、把方法迁移到外部类。
        self.switch_to_new_window()
        return JDProductPage(self.driver)
