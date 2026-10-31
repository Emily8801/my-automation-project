from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SearchPage:
    def __init__(self, driver):
        self.driver = driver
        self.search_input = (By.NAME, "search")  # 假设搜索框name属性为search
        self.search_button = (By.CSS_SELECTOR, "button[type='submit']")  # 通用搜索按钮定位
        self.result_items = (By.CSS_SELECTOR, ".search-result-item")  # 搜索结果项容器

    def search_product(self, product_name):
        """输入商品名并执行搜索"""
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.search_input)
        )
        search_input.clear()
        search_input.send_keys(product_name)
        
        search_button = self.driver.find_element(*self.search_button)
        search_button.click()

    def wait_for_results(self):
        """等待搜索结果加载完成"""
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.result_items)
        )

    def get_result_count(self):
        """获取搜索结果数量"""
        return len(self.driver.find_elements(*self.result_items))
