import pytest

from config.login_data import DDP_LOGIN_CASES, DDP_LOGIN_IDS


@pytest.fixture(params=DDP_LOGIN_CASES, ids=DDP_LOGIN_IDS)
def login_test_data(request):
    """参数化测试数据源（数据集中在 config/login_data/ 维护）"""
    return request.param
