import unittest
from page.masters_page import MastersPage
from testcase.test_login import LoginBase


class EnterPMBase(LoginBase):
    """进入 Product Masters 的公共前置（不含 test_ 方法，避免子类重复继承父类用例）

    🟠 结构问题修复：原 TestCopyPM / TestCreatePM 直接继承 TestEnterPM，
    会把 TestEnterPM.test_enter_product_masters 也一并继承执行，造成用例重复与状态污染。
    """
    def setUp(self):
        super().setUp()  # 确保父类的 driver 初始化和登录流程被执行
        self.masters_page = MastersPage(self.driver)


class TestEnterPM(EnterPMBase):
    """验证进入 Product Masters 页面"""
    def test_enter_product_masters(self):
        """点击 Masters → Product Masters，验证页面加载成功"""
        self.masters_page.enter_product_master()
        # ✅ 断言放在这里，紧接操作之后
        self.assertTrue(
            self.masters_page.is_product_master_loaded(),
            "Product Masters 页面未加载成功：标题或列表容器未出现"
        )
        # 🟠 修复：原期望值写成小写 "product Masters"，实际页面标题是 "Product Masters"（首字母大写），
        #    该 assertEqual 必然失败；同时 get_page_title_text() 已改为走 get_text() 裁剪空白
        self.assertEqual(
            self.masters_page.get_page_title_text(),
            "Product Masters",
            "页面标题文本与预期不符"
        )
