from selenium.webdriver.common.by import By
from page.base_page import BasePage
from selenium.common.exceptions import TimeoutException

class MastersPage(BasePage):
        # 定位符统一管理
    """Masters 模块页面对象"""
    MASTERS_LINK = (By.LINK_TEXT,"Masters")
    PRODUCT_MASTERS_LINK = (By.LINK_TEXT,"Product Masters")
    PAGE_TITLE = (By.CSS_SELECTOR,"h1.page-title")
    PRODUCT_LIST_TABLE = (By.CSS_SELECTOR,"table.product-master-list")

    def enter_product_master(self):
        """导航进入 Product Masters 页面"""
        self.click(self.MASTERS_LINK)
        self.click(self.PRODUCT_MASTERS_LINK)
        return self

    def is_product_master_loaded(self) ->bool:
        """检查 Product Masters 页面是否加载完成"""
        try:
            #等待标题或列表容器任一出现即视为加载成功
            self.find_element(self.PAGE_TITLE,timeout=20)
            return True
        except TimeoutException:
            return False

    def get_page_title_text(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def is_pm_in_list(self, style_name: str) -> bool:
        try:
            table = self.find_element(self.PRODUCT_LIST_TABLE)
            return style_name in table.text
        except TimeoutException:
            return False
