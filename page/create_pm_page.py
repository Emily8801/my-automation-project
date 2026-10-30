from selenium.webdriver.common.by import By
from page.base_page import BasePage



class CreatePMPage (BasePage):
    # ================= 1. 元素定位器 =================
    IFRAME_CLIENT = (By.ID, "client_frame")
    BTN_NEW_BD = (By.NAME,"NewBD")
    INPUT_STYLE_NAME = (By.ID,"param_apppmStyleName")
    INPUT_ABBR_NAME = (By.ID,"param_apppmAbbrStyleName")
    SELECT_INTRO_SEASON = (By.NAME,"param_apppmIntroSeason")
    SELECT_INTRO_DATE = (By.NAME,"param_apppmIntroDate")
    SELECT_BRAND = (By.NAME,"param_apppmBrand")
    SELECT_SUB_BRAND = (By.NAME,"param_apppmSubBrand")
    SELECT_DEPARTMENT = (By.NAME,"param_apppmDepartment")
    BTN_SAVE = (By.NAME, "saveButton")

    # ================= 3. 业务操作方法 =================

    def enter_create_page(self):
        """进入创建页面（切换 iframe 并点击新建）"""
        # 使用您 BasePage 中封装好的 iframe 切换方法
        self.switch_to_client_frame(self.IFRAME_CLIENT)
        # NewBD 按钮加载较慢，利用 BasePage 的 timeout 参数单独设置 60s
        self.click(self.BTN_NEW_BD,timeout=60)
        return self

    def fill_basic_info(self, style_name,abbr_name):
        """填写基础名称信息"""
        self.input_text(self.INPUT_STYLE_NAME, style_name, desc ="Style名称" )
        self.input_text(self.INPUT_ABBR_NAME,abbr_name, desc="Style简称")
        return self

    def select_attributes(self, season, date, brand, sub_brand, department):
        """选择各类下拉框属性"""
        self.select_dropdown(self.SELECT_INTRO_SEASON, season, desc="Season")
        self.select_dropdown(self.SELECT_INTRO_DATE, date, desc="date")
        self.select_dropdown(self.SELECT_BRAND, brand, desc="Brand" )
        self.select_dropdown(self.SELECT_SUB_BRAND, sub_brand, desc="SubBrand")
        self.select_dropdown(self.SELECT_DEPARTMENT, department, desc="Department")
        return self

    def save_and_confirm(self):
        """点击保存并处理可能弹出的 Alert"""
        self.click(self.BTN_SAVE, timeout=60)
        self.accept_alert(timeout=5)
        return self
