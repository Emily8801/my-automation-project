import pytest
import allure
from pages.search_page import SearchPage
from pages.product_page import ProductPage

@allure.feature("商品")
@allure.title("搜索已存在的商品")
@pytest.mark.parametrize("product_name", ["测试商品"])
def test_search_existing_product(browser, login, product_data, product_name):
    """
    测试搜索已存在的商品
    """
    search_page = SearchPage(browser)
    product_page = ProductPage(browser)
    
    with allure.step("1. 访问搜索页面"):
        browser.get("https://example.com/search")  # 替换为实际搜索页面URL
    
    with allure.step("2. 输入商品名并搜索"):
        search_page.search_product(product_name)
    
    with allure.step("3. 等待搜索结果加载"):
        search_page.wait_for_results()
    
    with allure.step("4. 验证搜索结果"):
        result_count = search_page.get_result_count()
        assert result_count > 0, f"搜索结果数量应为>0，实际为{result_count}"
        
        # 获取第一个结果商品名称
        first_result = browser.find_element(*search_page.result_items)
        first_result.click()
        
        # 验证商品详情页
        actual_product_name = product_page.get_product_name_text()
        assert product_name in actual_product_name, \
            f"搜索结果商品名称应包含'{product_name}'，实际为'{actual_product_name}'"
