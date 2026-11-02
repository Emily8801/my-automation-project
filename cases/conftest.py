import pytest

from config.login_data import LOGIN_CASES, LOGIN_IDS
from pages.login_page import LoginPage


@pytest.fixture(params=LOGIN_CASES, ids=LOGIN_IDS)
def login_test_data(request):
    """参数化测试数据源（数据集中在 config/login_data.py 维护）"""
    return request.param


@pytest.fixture()
def login_page(driver):
    """覆盖根目录同名 fixture: cases/ 下用例的显式等待超时放宽至 20 秒。

    pytest fixture 遮蔽规则：子目录 conftest 定义的同名 fixture 优先于根目录，
    仅对 cases/ 目录下的用例生效，不影响其他目录。
    """
    page = LoginPage(driver, timeout=20)
    page.open()
    yield page
