from selenium.webdriver.common.by import By
from page.base_page import BasePage


class PMPricingPage(BasePage):
    """Product Masters - Pricing 页签页面对象

    由旧脚本 pmPricing.py 迁移，做了以下改造：
    1. Selenium 2 写法 → Selenium 4：
       find_element_by_xpath(...) → find_element(By.XPATH, ...)
       switch_to_frame(...)      → switch_to.frame(...)
       switch_to_alert()         → switch_to.alert / accept_alert()
    2. 固定 time.sleep(15/20/10) → BasePage 的显式等待（WebDriverWait）
    3. 散落在用例里的 xpath → 集中到类属性，动态部分用方法生成
    """

    # ========== 元素定位器 ==========
    # 🟠 旧脚本用的是 switch_to_frame("clientframe")，本项目其它页面用 (By.ID, "client_frame")
    #    这里保留旧值以免改变行为，实际运行前请用 F12 确认 iframe 的 id / name 后统一
    FRAME_CLIENT = (By.NAME, "client_frame")

    BTN_CLEAR_ALL_SEARCH = (By.ID, "searchClearAllButton")
    INPUT_VIEW_NAME = (By.ID, "searchparam_viewName_input")
    BTN_SEARCH_SUBMIT = (By.ID, "searchSubmitButton")
    BTN_CLEAR_ALL = (By.XPATH, "//input[@value='Clear All']")
    DROPDOWN_TOGGLE = (By.XPATH, "//span[@class='ui-icon ui-icon-triangle-1-s']")
    CHECKBOX_SAP_FLAG = (By.ID, "ui-multiselect-searchparam_appplmSAPFlag_multiselect-option-1")

    # 🟠 旧脚本用的是绝对路径 /html/body/form/div[1]/div[1]/table/tbody/tr/td[10]/a，
    #    页面结构一改就失效；稳定后建议换成 By.LINK_TEXT "Pricing"
    PRICING_TAB = (By.XPATH, "/html/body/form/div[1]/div[1]/table/tbody/tr/td[10]/a")

    FRAME_PRICING = (By.ID, "apppmPricingRetailListSection01_iframe")
    BTN_EDIT = (By.XPATH, "//input[@class='button' and @value='Edit']")
    BTN_SAVE = (By.XPATH, "//input[@class='button' and @value='Save']")

    # ========== 动态定位器（id 里带记录编号，随数据变化） ==========
    @staticmethod
    def view_link(view_name):
        """搜索结果里的视图链接，按链接文本定位"""
        return (By.LINK_TEXT, view_name)

    @staticmethod
    def result_field(style_id, color_id):
        """查询结果里的记录项，例如 resultfield_apppmStyleNo_APP_PM--180136523__APP_PM_COLOR--180136539"""
        return (
            By.ID,
            f"resultfield_apppmStyleNo_APP_PM--{style_id}__APP_PM_COLOR--{color_id}",
        )

    @staticmethod
    def retail_price_input(price_id):
        """零售价输入框，例如 param_APP_PM_PRICING_RETAIL__APPPMRETAILRETAILPRICE__180136527"""
        return (
            By.ID,
            f"param_APP_PM_PRICING_RETAIL__APPPMRETAILRETAILPRICE__{price_id}",
        )

    # ========== 原子操作 ==========
    def enter_view(self, view_name):
        """清空搜索条件 → 按视图名搜索 → 打开该视图"""
        self.switch_to_client_frame(self.FRAME_CLIENT)
        self.click(self.BTN_CLEAR_ALL_SEARCH, "清空搜索按钮", timeout=60)
        self.accept_alert(timeout=10)
        self.input_text(self.INPUT_VIEW_NAME, view_name, desc="视图名称")
        self.click(self.BTN_SEARCH_SUBMIT, "搜索提交按钮", timeout=60)
        self.click(self.view_link(view_name), f"视图[{view_name}]", timeout=60)
        return self

    def filter_by_sap_flag(self):
        """Clear All → 勾选 SAP Flag 选项 → 重新搜索"""
        self.switch_to_client_frame(self.FRAME_CLIENT)
        self.click(self.BTN_CLEAR_ALL, "Clear All 按钮", timeout=60)
        self.accept_alert(timeout=10)
        self.click(self.DROPDOWN_TOGGLE, "多选下拉箭头", timeout=30)
        self.click(self.CHECKBOX_SAP_FLAG, "SAP Flag 选项", timeout=30)
        self.click(self.BTN_SEARCH_SUBMIT, "搜索提交按钮", timeout=60)
        return self

    def switch_to_pricing_frame(self):
        """回到 client frame 后，再进入嵌套的 Pricing 区域 iframe"""
        self.switch_to_client_frame(self.FRAME_CLIENT)
        iframe = self.find_element(self.FRAME_PRICING, "Pricing 区域 iframe", timeout=30)
        self.driver.switch_to.frame(iframe)
        return self

    def enter_pricing_tab(self, style_id, color_id):
        """打开目标记录 → 切到 Pricing 页签 → 进入 Pricing 区域 iframe"""
        self.switch_to_client_frame(self.FRAME_CLIENT)
        self.click(self.result_field(style_id, color_id), "查询结果记录", timeout=60)
        self.click(self.PRICING_TAB, "Pricing 页签", timeout=30)
        return self.switch_to_pricing_frame()

    def edit_retail_price(self, price_id, price):
        """点 Edit → 修改零售价 → 点 Save → 处理确认弹窗"""
        self.click(self.BTN_EDIT, "Edit 按钮", timeout=30)
        self.input_text(self.retail_price_input(price_id), str(price), desc="零售价")
        self.click(self.BTN_SAVE, "Save 按钮", timeout=30)
        self.accept_alert(timeout=30)
        return self

    def get_retail_price(self, price_id):
        """读取零售价输入框当前值（输入框内容在 value 属性里，不是 text）"""
        return self.get_attribute(self.retail_price_input(price_id), "value", timeout=30)
