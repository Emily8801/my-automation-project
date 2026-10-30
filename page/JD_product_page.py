from selenium.webdriver.common.by import By
from .base_page import BasePage
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JDProductPage(BasePage):
    ADD_CART_BTN = (By.XPATH, "//a[text()='加入购物车'] | //button[text()='加入购物车']")
    SUCCESS_MSG = (By.XPATH, "//*[contains(text(),'商品已加入购物车')]")
    QUANTITY_INPUT = (By.ID, "bu-num")
    CART_COUNT_BADGE = (By.CSS_SELECTOR, ".cart-cart_num")

    def add_to_cart(self):
        self.click(self.ADD_CART_BTN, "加入购物车按钮")
        return self

    def get_success_message(self):
        el = self.find_element(self.SUCCESS_MSG, "加购成功提示")
        return el.text

    def get_cart_quantity(self):
        try:
            qty_el = WebDriverWait(self.driver,3).until(
                EC.presence_of_element_located(self.QUANTITY_INPUT)
            )
            return qty_el.get_attribute("value")
        except TimeoutException:  # ✅ 修正：捕获正确的异常类型
            try:
                badge_el = self.find_element(self.CART_COUNT_BADGE, "购物车角标", timeout=2)
                return badge_el.text.strip()
            except TimeoutException:
                self.logger.warning("购物车数量输入框和角标均未找到")
                return "0"
