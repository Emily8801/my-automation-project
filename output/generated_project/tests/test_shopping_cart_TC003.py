import pytest
from allure import title, feature, step
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

@feature("购物车")
@title("登录后添加商品到购物车")
@pytest.mark.parametrize("username,password", [("standard_user", "secret_sauce")])
def test_add_to_cart(driver, username, password):
    """
    测试登录后添加商品到购物车
    用例编号: TC-003
    """
    login_page = LoginPage(driver)
    inventory_page = InventoryPage(driver)

    with step("登录系统"):
        login_page.open()
        login_page.login(username, password)
        login_page.wait_for_login_success()
        assert "inventory.html" in driver.current_url, "登录后URL未正确跳转"

    with step("添加背包到购物车"):
        inventory_page.add_backpack_to_cart()

    with step("验证购物车角标数量"):
        cart_count = inventory_page.get_cart_badge_count()
        assert cart_count == 1, f"购物车角标数量应为1，实际为{cart_count}"
