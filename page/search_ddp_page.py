from page.base_page import BasePage
from selenium.webdriver.common.by import By


class SearchDdpPage(BasePage):
    # 定位符统一管理
    SEARCH_INPUT = (By.ID, "searchbox")
    CLEAR_BTN = (By.XPATH, "//button[@id='clearSearch']")
    # 🔴 修复：原模板 "//div[@class='result-item' and normalize-space(text()).= '{}']" 有两处 XPath 语法错误：
    #    1. normalize-space(text()) 后面多了个点：`. =` 非法
    #    2. 模板占位符 {} 未拼接，且 .format 调用被注释掉，实际无法使用
    RESULT_ITEM = (By.XPATH, "//div[contains(@class,'result-item') and normalize-space(.)='{}']")

    # 🟠 风险：同一个 client iframe 在三个页面里用了三种定位符（此处 ID=client_frame_id，
    #    CopyPMPage 用 NAME="client frame"，PMCreatePage 用 ID="client_frame"），至少有一个是错的，
    #    需按实际 DOM 统一（建议抽到 BasePage 常量）
    DDP_IFRAME = (By.ID, "client_frame")

    def clear_search_and_confirm(self):
        """清除搜索条件并处理可能出现的Alert弹窗"""
        # 🟠 修复：原实现没有先切换 iframe，测试循环中第一次调用时驱动还在主文档，
        #    CLEAR_BTN 位于 client iframe 内会找不到元素。
        self.switch_to_client_frame(self.DDP_IFRAME)
        self.click(self.CLEAR_BTN)
        self.accept_alert()  # 封装在BasePage中的通用弹窗处理
        return self

    def search_view(self, view_name: str):
        """执行搜索动作"""
        self.switch_to_client_frame(self.DDP_IFRAME)
        self.input_text(self.SEARCH_INPUT, view_name)
        self.press_enter(self.SEARCH_INPUT)
        # 🟠 说明：这里仍停留在 iframe 内（下方切回主文档被注释），
        #    调用方必须知道后续操作都在 iframe 上下文中，否则会找错元素
        # self.switch_to_client_frame()
        return self

    def is_result_displayed(self, view_name: str) -> bool:
        """仅返回布尔值，不做断言"""
        # 🔴 修复：原 XPath 有两个致命错误，导致永远定位不到结果元素（正向用例必失败）：
        #    1. div[class='result-item'] 缺少 @ → 应写 @class
        #    2. contains(test(), ...) 拼写错误 → 应为 text()
        #    另外改用 contains(@class,...) 以兼容多 class 属性
        locator = (
            By.XPATH,
            f"//div[contains(@class,'result-item') and contains(normalize-space(.),'{view_name}')]"
        )
        return self.is_element_visible(locator, timeout=5)
