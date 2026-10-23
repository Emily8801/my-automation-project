from selenium.webdriver.common.by import By
# 🟡 原代码从 support.ui 同时导入 WebDriverWait 和 Select，其中 WebDriverWait 从未使用，已移除
from selenium.webdriver.support.ui import Select
from page.base_page import BasePage



class CopyPMPage(BasePage):

    # 🟠 风险：By.NAME 要求 iframe 的 name 属性真是 "client frame"（含空格，极不常见）；
    #    同为 client iframe，PMCreatePage 用 By.ID "client_frame"，SearchDdpPage 用 ID "client_frame_id"，
    #    三者不一致，需按真实 DOM 统一
    FRAME_CLIENT = (By.NAME, "client_frame")
    BTN_RESET = (By.NAME,"resetButton")
    BTN_RUN = (By.NAME,"runButton")
    INPUT_APP_PM = (By.XPATH,"//input[contains(@value='APP_PM&&')]")
    SELECT_OPERATIONS = (By.NAME,"objectOperations")
    DIALOG_IFRAME = (By.CLASS_NAME,"ecv-dialog-iframe")
    INPUT_STYLE_NAME = (By.CSS_SELECTOR,"input[id^='param_APP_PM_APPPMSTYLENAME_']")
    INPUT_ABBR_STYLE_NAME = (By.CSS_SELECTOR,"input[id^='param_APP_PM_APPPMABBRSTYLENAME_']")
    BTN_SAVE = (By.NAME,"saveButton")

    # ========== 业务操作方法 ==========
    def reset_and_run(self):
        # 复用 BasePage 的 iframe 切换方法
        self.switch_to_client_frame(self.FRAME_CLIENT)
        # 复用 BasePage 的 click 方法（自带显式等待）
        self.click(self.BTN_RESET,timeout=60)
        self.click(self.BTN_RUN, timeout=60)
        return self

    def select_copy_operation(self):
        """选中目标记录并选择复制操作"""
        self.click(self.INPUT_APP_PM)
        # 下拉框需要特殊处理，使用 find_element 获取元素后传给 Select
        select_el = self.find_element(self.SELECT_OPERATIONS,desc="操作下拉框" )
        Select(select_el).select_by_value("copyBDInVT()")
        return self

    def fill_copy_form(self, style_name:str,abbr_style_name: str):
        """切换到弹窗iframe，填写复制表单"""
        self.switch_to_client_frame(self.DIALOG_IFRAME)
        # 复用 BasePage 的 input_text 方法（自带清空和输入）
        self.input_text(self.INPUT_STYLE_NAME, style_name, desc="样式名称")
        self.input_text(self.INPUT_ABBR_STYLE_NAME, abbr_style_name,desc = "简称")
        return self
    def save_and_confirm(self):
        """点击保存并处理确认弹窗"""
        self.click(self.BTN_SAVE)
        # 🟠 风险：accept_alert 找不到弹窗时会静默跳过（BasePage 里 pass 掉了），
        #    保存失败/校验报错不会被发现，测试会"假通过"。建议区分成功弹窗与错误弹窗。
        self.accept_alert(timeout=10)
        return self

    def copy_pm(self, style_name: str,abbr_style_name:str):
        """组合方法: 一键完成复制PM全流程"""
        self.reset_and_run()
        self.select_copy_operation()
        self.fill_copy_form(style_name, abbr_style_name)
        self.save_and_confirm()
        return self