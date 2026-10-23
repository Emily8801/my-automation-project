import unittest
from selenium.webdriver.common.by import By
from testcase.test_enter_pm import EnterPMBase
from page.copy_pm_page import CopyPMPage

class TestCopyPM(EnterPMBase):
    # 将测试数据提取为类常量，便于统一管理和清理
    TEST_STYLE_NAME = "Auto1"
    TEST_ABBR_STYLE_NAME = "auto1"

    def setUp(self):
        # ✅ 自动执行: driver初始化 → 登录 → 初始化 MastersPage
        super().setUp()
        # 🔴 修复：原 setUp 只 new 了 CopyPMPage，从未进入 Product Masters 页面，
        #    导致 copy_pm() 里的 resetButton/runButton 不存在，用例必然超时失败。
        self.masters_page.enter_product_master()
        self.assertTrue(
            self.masters_page.is_product_master_loaded(),
            "进入 Product Masters 页面失败，无法执行复制操作"
        )
        self.copy_pm_page = CopyPMPage(self.driver)

    def test_copy_pm_success(self):
        """验证复制PM功能正常执行并生效"""
        # 核心业务操作（CopyPMPage 已封装完整流程）
        self.copy_pm_page.copy_pm(self.TEST_STYLE_NAME, abbr_style_name=self.TEST_ABBR_STYLE_NAME)
        # 断言：切回主框架验证结果
        self.copy_pm_page.switch_to_client_frame(CopyPMPage.FRAME_CLIENT)
        new_pm_locator = (By.XPATH, f"//td[contains(text(),'{self.TEST_STYLE_NAME}')]")

        # 🟠 风险：该定位符会同时匹配"名称中包含 Auto1"的任意行（包括复制前的源记录），
        #    即使复制失败也可能断言通过；建议改用时间戳生成的唯一名称，或精确定位新增行。
        self.assertTrue(
            self.copy_pm_page.is_element_visible(new_pm_locator, timeout=10),
            "复制后的 PM 'Auto1' 未出现在列表中"
        )

    def test_copy_pm_duplicate_name(self):
        """验证重复名称时的错误提示"""
        # 🔴 修复：原用例只复制一次就断言出现重复错误，但每条用例都会新建 driver + 重新登录，
        #    上一条用例的数据不会保留，首次复制必然成功 → 断言必然失败。
        #    改为同一会话内连续复制两次：第一次成功，第二次使用同名触发重复校验。
        self.copy_pm_page.copy_pm(style_name=self.TEST_STYLE_NAME, abbr_style_name=self.TEST_ABBR_STYLE_NAME)
        self.copy_pm_page.copy_pm(style_name=self.TEST_STYLE_NAME, abbr_style_name=self.TEST_ABBR_STYLE_NAME)

        # 🟠 风险：错误提示形态未确认（页面内联 .error-message 还是 alert 弹窗）。
        #    且 save_and_confirm() 内部的 accept_alert() 会把 alert 直接点掉，
        #    若重复错误是以 alert 呈现，此断言永远失败，需要按真实交互调整。
        error_locator = (By.CLASS_NAME, "error-message")
        self.assertTrue(
            self.copy_pm_page.is_element_visible(error_locator, timeout=5),
            "重复名称未触发错误提示"
        )


if __name__ == '__main__':
    unittest.main()
