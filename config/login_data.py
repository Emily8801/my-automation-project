# config/login_data.py
# Swag Labs 登录场景测试数据（公开演示站账号，非敏感）

LOGIN_CASES = [
    {
        "username": "standard_user",
        "password": "secret_sauce",
        "expect_success": True,
        "expected_error": None,
    },
    {
        "username": "locked_out_user",
        "password": "secret_sauce",
        "expect_success": False,
        "expected_error": "Sorry, this user has been locked out",
    },
    {
        "username": "wrong_user",
        "password": "wrong_pass",
        "expect_success": False,
        "expected_error": "Username and password do not match",
    },
    {
        "username": "",
        "password": "secret_sauce",
        "expect_success": False,
        "expected_error": "Username is required",
    },
    {
        "username": "standard_user",
        "password": "",
        "expect_success": False,
        "expected_error": "Password is required",
    },
]

LOGIN_IDS = ["valid_login", "locked_out_user", "invalid_credentials", "empty_username", "empty_password"]
