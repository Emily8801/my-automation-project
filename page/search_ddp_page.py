from page.base_page import BasePage
from selenium.webdriver.common.by import By

class SearchDdpPage(BasePage):
    # 定位符统一管理
    SEARCH_INPUT = (By.ID, "searchbox")
    CLEAR_BTN = (By.XPATH, "//button[@id='clearSearch']")
    RESULT_ITEM = (By.XPATH, "//div[contains(@class,'result-item') and contains(normalize-space(.),'{}')]")
    DDP_IFRAME = (By.ID, "client_frame")

    def clear_search_and_confirm(self):
        """清除搜索条件并处理可能出现的Alert弹窗"""
        self.switch_to_client_frame(self.DDP_IFRAME)
        self.click(self.CLEAR_BTN)
        self.accept_alert()  # 封装在BasePage中的通用弹窗处理
        return self

    def search_view(self, view_name: str):
        """执行搜索动作"""
        self.switch_to_client_frame(self.DDP_IFRAME)
        self.input_text(self.SEARCH_INPUT, view_name)
        self.press_enter(self.SEARCH_INPUT)
        # self.switch_to_client_frame()
        return self

    def is_result_displayed(self, view_name: str) -> bool:
        """仅返回布尔值，不做断言"""
        locator = (
            By.XPATH,
            f"//div[contains(@class,'result-item') and contains(normalize-space(.),'{view_name}')]"
        )
        return self.is_element_visible(locator, timeout=5)
