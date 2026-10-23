from selenium.webdriver.common.by import By
# 🔴 FIX: 原代码 from.base_page import BasePage 点号后没有空格，是 Python 语法错误
#         正确写法：相对导入 from .base_page import 或绝对导入 from page.base_page import
from .base_page import BasePage
# 🔴 FIX: 原代码只导入了 NoSuchElementException，但 get_cart_quantity 里用了 TimeoutException，
#         需要额外导入；同时 NoSuchElementException 实际没用了，换一下
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JDProductPage(BasePage):
    # 🟠 FIX: JD 商品详情页的"加入购物车"通常是 <a> 或 <button>，不一定有 LINK_TEXT，
    #         用 XPATH 更保险，能兼容 <a> 和 <button> 两种标签
    ADD_CART_BTN = (By.XPATH, "//a[text()='加入购物车'] | //button[text()='加入购物车']")
    # 🔴 FIX: 这里的文案要和 test_jd_book_purchase.py 里的 assertIn 保持一致，
    #         京东实际提示是 "商品已加入购物车"（不含"成功"）
    SUCCESS_MSG = (By.XPATH, "//*[contains(text(),'商品已加入购物车')]")
    QUANTITY_INPUT = (By.ID, "bu-num")
    # 🟠 FIX: JD 购物车角标实际可能是 #J-cart-count 或 .cart-num，
    #         .cart-count 不一定存在，需要实际验证
    CART_COUNT_BADGE = (By.CSS_SELECTOR, ".cart-cart_num")

    def add_to_cart(self):
        # 🟠 FIX: base_page 已调整参数顺序为 (locator, desc, timeout)，
        #         这里 "加入购物车按钮" 正确传给 desc
        self.click(self.ADD_CART_BTN, "加入购物车按钮")
        return self

    def get_success_message(self):
        # 🟠 FIX: "加购成功提示" 正确传给 desc
        el = self.find_element(self.SUCCESS_MSG, "加购成功提示")
        return el.text

    def get_cart_quantity(self):
        # 🔴 FIX: 原代码 except NoSuchElementException 永远不会被触发！
        #         WebDriverWait().until() 超时抛的是 TimeoutException，不是 NoSuchElementException。
        #         原代码 except 块里的 CART_COUNT_BADGE 兜底逻辑根本执行不到。
        try:
            qty_el = WebDriverWait(self.driver,3).until(
                EC.presence_of_element_located(self.QUANTITY_INPUT)
            )
            return qty_el.get_attribute("value")
        except TimeoutException:  # ✅ 修正：捕获正确的异常类型
            try:
                # 🟠 FIX: "购物车角标" 正确传给 desc
                badge_el = self.find_element(self.CART_COUNT_BADGE, "购物车角标", timeout=2)
                return badge_el.text.strip()
            except TimeoutException:
                # 🟠 FIX: 两层都找不到时，返回 0 或抛明确异常，不要静默吞掉
                self.logger.warning("购物车数量输入框和角标均未找到")
                return "0"
