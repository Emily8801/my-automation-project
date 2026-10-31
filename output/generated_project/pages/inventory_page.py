from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class InventoryPage:
    def __init__(self, driver):
        self.driver = driver
        self.add_to_cart_backpack = (By.ID, "add-to-cart-sauce-labs-backpack")
        self.shopping_cart_badge = (By.CLASS_NAME, "shopping_cart_badge")
        self.inventory_items = (By.CLASS_NAME, "inventory_item")

    def get_inventory_items(self):
        """获取商品列表元素"""
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.inventory_items))
        return self.driver.find_elements(*self.inventory_items)

    def add_backpack_to_cart(self):
        """添加背包到购物车"""
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.add_to_cart_backpack)).click()

    def get_cart_badge_count(self):
        """获取购物车角标数量"""
        try:
            badge = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.shopping_cart_badge))
            return int(badge.text)
        except:
            return 0
