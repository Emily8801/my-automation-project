from selenium.webdriver.common.by import By
from page.base_page import BasePage
from page.JD_product_page import JDProductPage


class JDHomePage(BasePage):
    SEARCH_INPUT = (By.ID, "key")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "#search button.button_submit")
    TARGET_BOOK_LINK = (
        By.XPATH,
        "//a[contains(normalize-space(.),'软件测试') and contains(normalize-space(.),'原书第二版')]"
    )

    def open(self, url):
        self.driver.get(url)
        self.driver.maximize_window()
        return self

    def search_product(self, keyword):
        input_el = self.find_element(self.SEARCH_INPUT, "搜索框")
        input_el.clear()
        input_el.send_keys(keyword)
        self.click(self.SEARCH_BUTTON, "搜索按钮")
        return self

    def select_target_book(self) -> 'JDProductPage':
        self.click(self.TARGET_BOOK_LINK, "软件测试原书第二版")
        self.switch_to_new_window()
        return JDProductPage(self.driver)
