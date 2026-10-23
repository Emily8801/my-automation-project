import unittest
from testcase.test_login import LoginBase
from page.view_management_page import ViewManagementPage
from page.search_ddp_page import SearchDdpPage
from config.ddp_test_data import DDP_SEARCH_CASES

class TestSearchDDP(LoginBase):
    # 🟠 修复：原代码定义了 setUpClass 并调用 super().setUpClass()，但父类并没有 setUpClass
    #    （最终落到 unittest.TestCase.setUpClass 的空实现），这段是无效代码，已删除。

    def setUp(self):
        super().setUp()    # 先执行父类的前置
        self.view_page = ViewManagementPage(self.driver)  # 再初始化页面对象
        self.search_page = SearchDdpPage(self.driver)

        # ✅ 关键：每条用例执行前确保在 DDP 页面
        self.view_page.enter_ddp_view_list()
        self.assertTrue(self.view_page.is_ddp_list_loaded(), "DDP页面加载失败，终止测试")


    def test_search_ddp_views(self):
        """数据驱动：批量验证DDP搜索功能"""
        for case in DDP_SEARCH_CASES:
            # 🔴 修复：原代码断言里引用 case['desc']，但 ddp_test_data.py 中没有 desc 字段，
            #    会直接 KeyError；这里用 .get 兜底
            desc = case.get("desc", case["view_name"])
            with self.subTest(view_name=case["view_name"]):
                # 1. 清理上一次的状态
                self.search_page.clear_search_and_confirm()
                # 2. 执行搜索
                self.search_page.search_view(case["view_name"])
                # 3. 获取实际结果并断言
                # 🔴 修复：原代码这几行缩进停在 12 空格（在 with 之外），subTest 上下文没包住断言，
                #    失败归属到错误的子用例；且引用了未定义的裸变量 view_name。现已归位到 with 内部。
                is_found = self.search_page.is_result_displayed(case["view_name"])
                if case["should_find"]:
                    self.assertTrue(
                        is_found,
                        f"[{desc}]预期找到 {case['view_name']} 但未找到"
                    )
                else:
                    self.assertFalse(
                        is_found,
                        f"[{desc}]预期无结果但找到了 {case['view_name']}"
                    )

if __name__ == '__main__':
    unittest.main()
