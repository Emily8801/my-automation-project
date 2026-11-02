# config/login_data.py
# Swag Labs 登录场景测试数据（公开演示站账号，非敏感）

DDP_LOGIN_CASES = [
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

DDP_LOGIN_IDS = ["正常登录", "被锁定账号", "错误账号密码", "用户名为空", "密码为空"]
