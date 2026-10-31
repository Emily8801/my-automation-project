from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProductPage:
    def __init__(self, driver):
        self.driver = driver
        self.product_name = (By.CSS_SELECTOR, ".product-name")  # 商品名称元素

    def get_product_name_text(self):
        """获取商品名称文本"""
        product_name_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.product_name)
        )
        return product_name_element.text
