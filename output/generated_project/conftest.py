import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def browser():
    """浏览器初始化fixture"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def login(browser):
    """登录fixture - 实际项目中应实现具体登录逻辑"""
    # 这里简化处理，实际项目中应实现登录流程
    # yield browser
    pass

@pytest.fixture(scope="function")
def product_data():
    """商品数据预置fixture"""
    # 这里简化处理，实际项目中应实现数据预置
    # yield {"product_name": "测试商品"}
    pass

CASE_META = {
    "test_failed_login_with_wrong_password": {"id": "TC-002", "priority": "P1", "module": "登录"},

    "test_login_success": {"id": "TC-001", "priority": "P0", "module": "登录"},

    "test_search_existing_product": {"id": "TC-003", "priority": "P1", "module": "商品"},
}
