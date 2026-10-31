import allure
import pytest
from pages.login_page import LoginPage

@allure.feature("登录")
@allure.title("错误密码登录失败提示")
@pytest.mark.parametrize("username,password", [("standard_user", "wrong_password")])
def test_login_with_wrong_password(driver, username, password):
    login_page = LoginPage(driver)
    
    with allure.step("打开登录页面"):
        login_page.open()
        assert login_page.get_current_url() == "https://www.saucedemo.com/", "登录页面未正确加载"
    
    with allure.step("输入用户名和错误密码"):
        login_page.login(username, password)
    
    with allure.step("验证错误提示显示"):
        error_text = login_page.get_error_message()
        assert "Epic sadface" in error_text, f"错误提示文本不包含'Epic sadface'，实际文本: {error_text}"
    
    with allure.step("验证页面未跳转"):
        assert login_page.get_current_url() == "https://www.saucedemo.com/", "登录失败后页面不应跳转"
