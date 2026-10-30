from selenium.webdriver.common.by import By
from page.base_page import BasePage

class ViewManagementPage(BasePage):
    """视图管理页面对象"""
    # ========== 元素定位器集中管理 ==========
    VIEW_MANAGEMENT_LINK = (By.LINK_TEXT,"View Management")
    DDP_VIEW_LIST_LINK = (By.LINK_TEXT,"Dynamic Data View List")
    DDP_LIST_CONTAINER = (By.CSS_SELECTOR,"table.ddp-view-list")
    PAGE_TITLE = (By.CSS_SELECTOR,"h1.page-title")

    # ========== 业务操作方法 ==========
    def enter_ddp_view_list(self):
        """进入动态数据面板视图列表"""
        self.click(self.VIEW_MANAGEMENT_LINK)
        self.click(self.DDP_VIEW_LIST_LINK)
        return self

    # ========== ✅ 新增：验证方法 ==========
    def is_ddp_list_loaded(self, timeout=10):
        """
        验证DDP视图列表是否成功加载
        :param timeout: 最大等待时间(秒)
        :return: bool 列表可见返回 True,超时返回 False
        """
        return self.is_element_visible(self.DDP_LIST_CONTAINER, timeout=timeout)

    def get_ddp_list_row_count(self):
        """获取DDP列表的数据行数"""
        rows = self.find_elements((By.CSS_SELECTOR,"table.ddp-view-list tbody tr"))
        return len(rows)

    def get_page_title_text(self):
        """获取当前页面标题文本"""
        return self.get_text(self.PAGE_TITLE)
