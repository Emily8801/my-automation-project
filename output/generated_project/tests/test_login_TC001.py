import allure
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

@allure.feature("登录")
@allure.title("正确账号密码登录成功")
@pytest.mark.parametrize("username,password", [("standard_user", "secret_sauce")])
def test_login_success(driver, username, password):
    login_page = LoginPage(driver)
    inventory_page = InventoryPage(driver)

    with allure.step("打开登录页面"):
        login_page.open()

    with allure.step("输入用户名和密码"):
        login_page.login(username, password)

    with allure.step("验证登录成功"):
        assert "/inventory.html" in driver.current_url, "登录后URL未跳转到inventory.html"
        inventory_items = inventory_page.get_inventory_items()
        assert len(inventory_items) > 0, "商品列表数量未大于0"
