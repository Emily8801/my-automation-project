import pytest
from selenium import webdriver
from pages.login_page import LoginPage
import allure

@allure.feature("登录")
@allure.title("错误密码登录失败提示")
@pytest.mark.parametrize("username, password", [("valid_user", "wrong_password")])
def test_failed_login_with_wrong_password(username, password):
    driver = webdriver.Chrome()
    login_page = LoginPage(driver)
    
    try:
        with allure.step("打开登录页"):
            login_page.open()
            assert "login" in driver.current_url, "未跳转到登录页"
        
        with allure.step("输入正确账号和错误密码"):
            login_page.enter_username(username)
            login_page.enter_password(password)
        
        with allure.step("点击登录按钮"):
            login_page.click_login()
        
        with allure.step("验证错误提示显示"):
            assert login_page.is_error_message_displayed(), "错误提示未显示"
            error_text = login_page.get_error_message()
            assert "账号或密码错误" in error_text, f"错误提示文本不正确: {error_text}"
        
        with allure.step("验证未跳转"):
            assert "login" in driver.current_url, "登录后意外跳转"
    
    finally:
        driver.quit()
