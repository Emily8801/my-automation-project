import unittest
# 🟡 原文件导入了 get_driver、BROWSER 但从未使用（driver 由父类 setUp 创建），已移除
from page.view_management_page import ViewManagementPage
from testcase.test_login import LoginBase


class TestViewManagement(LoginBase):

    def setUp(self):
        super().setUp()   # 复用父类的 driver 初始化 + 登录流程
        self.view_page = ViewManagementPage(self.driver)

    def test_enter_ddp_has_data(self):
        """验证DDP列表加载且包含数据"""
        # 操作与验证分离
        self.view_page.enter_ddp_view_list()
        # 多重断言：先验证加载，再验证数据
        self.assertTrue(
            self.view_page.is_ddp_list_loaded(),
            "DDP列表未加载"
        )
        row_count = self.view_page.get_ddp_list_row_count()
        # 🟠 说明：若 UAT 环境的 DDP 列表允许为空，此断言会误报，需确认测试数据的预期
        self.assertGreater(
            row_count, 0,
            f"DDP列表已加载但无数据,实际行数：{row_count}"
        )


if __name__ == '__main__':
    unittest.main()
