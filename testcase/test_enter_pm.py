import unittest
from page.masters_page import MastersPage
from testcase.test_coach_login import LoginBase


class EnterPMBase(LoginBase):
    """进入 Product Masters 的公共前置（不含 test_ 方法，避免子类重复继承父类用例）
    """
    def setUp(self):
        super().setUp()  # 确保父类的 driver 初始化和登录流程被执行
        self.masters_page = MastersPage(self.driver)


class TestEnterPM(EnterPMBase):
    """验证进入 Product Masters 页面"""
    def test_enter_product_masters(self):
        """点击 Masters → Product Masters,验证页面加载成功"""
        self.masters_page.enter_product_master()
        # ✅ 断言放在这里，紧接操作之后
        self.assertTrue(
            self.masters_page.is_product_master_loaded(),
            "Product Masters 页面未加载成功：标题或列表容器未出现"
        )
        self.assertEqual(
            self.masters_page.get_page_title_text(),
            "Product Masters",
            "页面标题文本与预期不符"
        )
