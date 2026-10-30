import unittest
from selenium import webdriver
from page.JD_home_page import JDHomePage


class TestJDBookPurchase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(10)
        cls.base_url = "https://www.jd.com"

    def test_purchase_book(self):
        # 1. 访问首页并搜索
        home_page = JDHomePage(self.driver).open(self.base_url).search_product("软件测试")
        # 2. 选择目标书籍并进入详情页
        product_page = home_page.select_target_book()
        # 3. 加入购物车
        product_page.add_to_cart()
        # 4. 断言成功提示
        success_text = product_page.get_success_message()

        self.assertIn("商品已加入购物车", success_text, "未找到成功提示信息")
        # 5. 断言数量为 1
        quantity = product_page.get_cart_quantity()
        self.assertEqual(quantity, "1", f"购物车数量期望为1,实际为{quantity}")
        print(f"测试通过:商品已加入购物车且数量为1")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()
