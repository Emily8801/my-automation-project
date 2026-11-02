import allure
import pytest


def test_login(login_page, login_test_data, request):
    """通过 fixture 获取参数化数据，进行登录测试"""

    # Allure 报告里的用例名显示为中文场景名(如"正常登录"), 而非 test_login[...] 参数ID
    allure.dynamic.title(request.node.callspec.id)

    username = login_test_data["username"]
    password = login_test_data["password"]
    expect_success = login_test_data["expect_success"]
    expected_error = login_test_data["expected_error"]

    # 1. 提交账号密码
    login_page.submit_login(username, password)

    if expect_success:
        # 成功场景断言：先等元素可见(显式等待兜底页面跳转完成)，再断言URL，避免竞态
        assert login_page.is_inventory_container_visible()
        assert "inventory" in login_page.get_current_url()
        return

    # 2. 失败场景断言一：URL未跳转
    assert "inventory" not in login_page.get_current_url()

    # 3. 失败场景断言二：错误提示匹配（增加安全保护，防止拿不到报错导致脚本报错）
    if expected_error:
        actual_error = login_page.get_error_message()
        assert expected_error in actual_error

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))