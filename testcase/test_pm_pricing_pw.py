"""Product Masters - Pricing 用例（Playwright 版）。

与 Selenium 版 test_pm_pricing.py 的差异：
    1. driver 换成了 playwright 的 browser / context / page
    2. 原来继承 LoginBase / EnterPMBase 的 setUp，改为在本类 setUp 里显式登录并进入 Masters
    3. 断言方式一致：改价后读回输入框的 value
"""

import unittest

from playwright.sync_api import sync_playwright

from config.settings import USERNAME, PASSWORD
from page.pw_login_page import PWLoginPage
from page.pw_pm_pricing_page import PMPricingPWPage


class TestPMPricingPlaywright(unittest.TestCase):
    """查询视图 → 过滤 SAP Flag → 修改零售价"""

    # ========== 测试数据 ==========
    VIEW_NAME = "BPPM-SKU(Create PCR) by emily"
    # 🟠 下面三个编号是数据库记录 id，换环境/换记录后会变，需要按实际数据更新
    STYLE_ID = "180136523"
    COLOR_ID = "180136539"
    PRICE_ID = "180136527"
    NEW_PRICE = "650"

    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        # headless=False 便于观察执行过程；CI 环境可改为 True
        cls.browser = cls.playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context(viewport={"width": 1600, "height": 900})
        cls.page = cls.context.new_page()

    @classmethod
    def tearDownClass(cls):
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        # 1. 登录
        self.login_page = PWLoginPage(self.page)
        self.login_page.login(USERNAME, PASSWORD)
        self.assertTrue(self.login_page.is_logged_in(), "登录失败：未检测到用户头像")

        # 2. 进入 Masters → Product Masters
        self.pricing_page = PMPricingPWPage(self.page)
        self.pricing_page.enter_product_master()

    def test_edit_retail_price(self):
        """验证修改某条记录的零售价后，输入框显示新价格"""
        (self.pricing_page
            .enter_view(self.VIEW_NAME)
            .filter_by_sap_flag()
            .enter_pricing_tab(self.STYLE_ID, self.COLOR_ID)
            .edit_retail_price(self.PRICE_ID, self.NEW_PRICE))

        actual = self.pricing_page.get_retail_price(self.PRICE_ID)
        self.assertEqual(
            actual,
            self.NEW_PRICE,
            f"零售价保存失败：期望 {self.NEW_PRICE}，实际 {actual}",
        )


if __name__ == "__main__":
    unittest.main()
