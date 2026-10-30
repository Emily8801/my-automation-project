"""Product Masters - Pricing 页签页面对象（Playwright 版）。

由旧脚本 pmPricing.py 迁移，改造点：
    1. find_element_by_xpath + time.sleep(15/20/10) → locator + 自动等待
    2. switch_to_frame("clientframe")     → frame_locator
    3. switch_to_frame("..._iframe")     → 在 client 作用域下再 frame_locator（嵌套）
    4. switch_to_alert()                 → page.on("dialog", ...) 在基类里统一处理
    5. 散落在脚本里的定位符               → 类常量 + 静态方法（动态 id）
"""

from page.pw_base_page import PWBasePage


class PMPricingPWPage(PWBasePage):
    """Masters → Product Masters → 视图搜索 → SAP Flag 过滤 → Pricing 改价"""

    # ========== 顶层页面 ==========
    PAGE_TITLE = "h1.page-title"

    # ========== client iframe 内 ==========
    # 🟠 旧脚本写的是 "clientframe"，项目里其它页面写的是 "client_frame"，
    #    这里两种都兼容，实际运行前建议用 F12 确认唯一的 iframe id/name
    FRAME_CLIENT = (
        "iframe#clientframe, iframe[name='clientframe'], "
        "iframe#client_frame, iframe[name='client_frame']"
    )

    BTN_CLEAR_ALL_SEARCH = "#searchClearAllButton"
    INPUT_VIEW_NAME = "#searchparam_viewName_input"
    BTN_SEARCH_SUBMIT = "#searchSubmitButton"
    BTN_CLEAR_ALL = "input[value='Clear All']"
    DROPDOWN_TOGGLE = "span.ui-icon.ui-icon-triangle-1-s"
    CHECKBOX_SAP_FLAG = "#ui-multiselect-searchparam_appplmSAPFlag_multiselect-option-1"

    # 🟠 旧脚本用的是绝对 XPath，页面结构一改就失效；稳定后建议换成 text=Pricing
    PRICING_TAB = "xpath=/html/body/form/div[1]/div[1]/table/tbody/tr/td[10]/a"

    # ========== Pricing 区域内层 iframe ==========
    FRAME_PRICING = "iframe#apppmPricingRetailListSection01_iframe"
    BTN_EDIT = "input.button[value='Edit']"
    BTN_SAVE = "input.button[value='Save']"

    # ========== 动态定位器（id 里带记录编号，随数据变化） ==========
    @staticmethod
    def view_link(view_name):
        """搜索结果里的视图链接：a 标签且文本完全等于视图名"""
        return f'a:text-is("{view_name}")'

    @staticmethod
    def result_field(style_id, color_id):
        """查询结果里的记录项，例如 resultfield_apppmStyleNo_APP_PM--180136523__APP_PM_COLOR--180136539"""
        return f"#resultfield_apppmStyleNo_APP_PM--{style_id}__APP_PM_COLOR--{color_id}"

    @staticmethod
    def retail_price_input(price_id):
        """零售价输入框，例如 param_APP_PM_PRICING_RETAIL__APPPMRETAILRETAILPRICE__180136527"""
        return f"#param_APP_PM_PRICING_RETAIL__APPPMRETAILRETAILPRICE__{price_id}"

    # ========== 作用域 ==========
    def client(self):
        """client iframe 的作用域，相当于旧脚本的 switch_to_frame("clientframe")"""
        return self.frame(self.FRAME_CLIENT)

    def pricing_area(self):
        """Pricing 区域的嵌套 iframe：先定位 client，再往里定位一层"""
        return self.client().frame_locator(self.FRAME_PRICING)

    # ========== 业务操作 ==========
    def enter_product_master(self):
        """Masters → Product Masters，作为本页所有操作的前置"""
        self.click(
            self.page.get_by_role("link", name="Masters", exact=True).first,
            "Masters 菜单",
        )
        self.click(
            self.page.get_by_role("link", name="Product Masters", exact=True).first,
            "Product Masters 菜单",
        )
        self.page.locator(self.PAGE_TITLE).wait_for(state="visible", timeout=30000)
        return self

    def enter_view(self, view_name):
        """清空搜索条件 → 按视图名搜索 → 打开该视图"""
        client = self.client()
        self.click(client.locator(self.BTN_CLEAR_ALL_SEARCH), "清空搜索按钮", timeout=60000)
        # 弹窗由基类的 dialog 监听自动确认，这里不需要单独处理
        self.fill(client.locator(self.INPUT_VIEW_NAME), view_name, desc="视图名称")
        self.click(client.locator(self.BTN_SEARCH_SUBMIT), "搜索提交按钮", timeout=60000)
        self.click(client.locator(self.view_link(view_name)), f"视图[{view_name}]", timeout=60000)
        return self

    def filter_by_sap_flag(self):
        """Clear All → 勾选 SAP Flag → 重新搜索"""
        client = self.client()
        self.click(client.locator(self.BTN_CLEAR_ALL), "Clear All 按钮", timeout=60000)
        self.click(client.locator(self.DROPDOWN_TOGGLE), "多选下拉箭头", timeout=30000)
        self.click(client.locator(self.CHECKBOX_SAP_FLAG), "SAP Flag 选项", timeout=30000)
        self.click(client.locator(self.BTN_SEARCH_SUBMIT), "搜索提交按钮", timeout=60000)
        return self

    def enter_pricing_tab(self, style_id, color_id):
        """打开目标记录 → 切到 Pricing 页签"""
        client = self.client()
        self.click(
            client.locator(self.result_field(style_id, color_id)),
            "查询结果记录",
            timeout=60000,
        )
        self.click(client.locator(self.PRICING_TAB), "Pricing 页签", timeout=30000)
        return self

    def edit_retail_price(self, price_id, price):
        """点 Edit → 填新价格 → 点 Save（确认弹窗自动接受）"""
        pricing = self.pricing_area()
        self.click(pricing.locator(self.BTN_EDIT), "Edit 按钮", timeout=30000)
        self.fill(pricing.locator(self.retail_price_input(price_id)), price, desc="零售价")
        self.click(pricing.locator(self.BTN_SAVE), "Save 按钮", timeout=30000)
        return self

    def get_retail_price(self, price_id):
        """读取零售价输入框当前值"""
        return self.get_value(self.pricing_area().locator(self.retail_price_input(price_id)))
