import unittest
from page.pm_pricing_page import PMPricingPage
from testcase.test_enter_pm import EnterPMBase


class TestPMPricing(EnterPMBase):
    """Product Masters - Pricing 页签：查询视图 → 过滤 SAP Flag → 修改零售价

    由旧脚本 pmPricing.py 迁移。旧脚本依赖 Enterddp 模块里的全局 driver，
    这里改为复用 LoginBase 的 driver 初始化 + 登录，再由 EnterPMBase 提供 MastersPage。
    """

    # ========== 测试数据 ==========
    # 🟠 旧脚本里视图名前面有一个空格（' BPPM-SKU...'），属于手误，这里去掉
    VIEW_NAME = "BPPM-SKU(Create PCR) by emily"
    # 🟠 下面三个编号是数据库记录 id，换环境/换记录后会变，需要按实际数据更新
    STYLE_ID = "180136523"
    COLOR_ID = "180136539"
    PRICE_ID = "180136527"
    NEW_PRICE = "650"

    def setUp(self):
        super().setUp()
        # 旧脚本默认已在 Product Masters 搜索页，这里显式进入，避免依赖上一状态
        self.masters_page.enter_product_master()
        self.assertTrue(
            self.masters_page.is_product_master_loaded(),
            "进入 Product Masters 页面失败，无法执行 Pricing 操作"
        )
        self.pricing_page = PMPricingPage(self.driver)

    def test_edit_retail_price(self):
        """验证修改某条记录的零售价后，输入框显示新价格"""
        (self.pricing_page
            .enter_view(self.VIEW_NAME)
            .filter_by_sap_flag()
            .enter_pricing_tab(self.STYLE_ID, self.COLOR_ID)
            .edit_retail_price(self.PRICE_ID, self.NEW_PRICE))

        # 保存后区域可能局部刷新，重新进入一次 iframe 再读取，避免 StaleElementReference
        self.pricing_page.switch_to_pricing_frame()
        self.assertEqual(
            self.pricing_page.get_retail_price(self.PRICE_ID),
            self.NEW_PRICE,
            f"零售价保存失败：期望 {self.NEW_PRICE}，实际 {self.pricing_page.get_retail_price(self.PRICE_ID)}"
        )


if __name__ == "__main__":
    unittest.main()
