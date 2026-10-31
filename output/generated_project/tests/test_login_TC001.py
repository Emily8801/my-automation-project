import allure
import pytest
from pages.login_page import LoginPage


@allure.feature("登录")
@allure.title("正确账号密码登录成功")
@pytest.mark.parametrize("username,password", [("testuser", "testpass")])
def test_login_success(driver, username, password):
    login_page = LoginPage(driver)
    
    with allure.step("打开登录页"):
        login_page.open()
    
    with allure.step("输入正确账号密码"):
        login_page.input_username(username)
        login_page.input_password(password)
    
    with allure.step("点击登录按钮"):
        login_page.click_login()
    
    with allure.step("验证跳转到主页并显示用户头像"):
        login_page.wait_for_home_page()
        avatar = login_page.get_user_avatar()
        assert avatar.is_displayed(), "用户头像未显示"
