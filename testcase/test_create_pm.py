import time
import unittest
from testcase.test_enter_pm import EnterPMBase
from page.create_pm_page import CreatePMPage


class TestCreatePM(EnterPMBase):
    """验证创建 Product Master 功能"""

    def setUp(self):
        # 🟠 结构修复：原类直接继承 TestEnterPM，会额外继承执行 test_enter_product_masters；
        #    现改为继承不含用例的 EnterPMBase
        super().setUp()

    def test_create_pm_success(self):
        """测试成功创建一条新的 Product Master"""
        # 1. 准备动态测试数据（使用时间戳避免重名）
        timestamp = int(time.time())
        style_name = f"AutoTest_Style_{timestamp}"
        abbr_name = f"AT_{timestamp}"

        # 2. 执行创建操作（进入列表页 -> 进入创建页 -> 填写 -> 保存）
        self.masters_page.enter_product_master()
        create_page = CreatePMPage(self.driver)
        (create_page
            .enter_create_page()
            .fill_basic_info(style_name, abbr_name)
        # 🟠 风险：season/date/brand 等取值是硬编码猜测值，必须与 UAT 环境下拉框的
        #    实际 option value 一致，否则 select_by_value 会抛 NoSuchElementException
            .select_attributes(
            season="SS26",
            date="2026-01-01",
            brand="BRAND_A",
            sub_brand="SUB_A",
            department="DEPT_01"
        )
        .save_and_confirm()
        )

        # 3. ✅ 断言1：保存后无报错且回到列表页（表格重新可见）
        self.assertTrue(
            self.masters_page.is_product_master_loaded(),
            "保存后未正确返回 Product Master 列表页"
        )
        # 4. ✅ 断言2：验证新创建的数据出现在列表中
        table_text = self.masters_page.find_element(
            self.masters_page.PRODUCT_LIST_TABLE).text
        self.assertIn(
            style_name, table_text,
            f"创建失败：列表中未找到新创建的 Style[{style_name}]"
        )
        # 🟡 说明：用例结束后没有清理刚创建的 PM，长期运行会在 UAT 环境堆积脏数据，
        #    建议补充 tearDown 删除（若系统支持）或使用固定可复用的测试数据池


if __name__ == '__main__':
    unittest.main()
