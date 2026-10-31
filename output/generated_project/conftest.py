"""生成工程基础设施：driver fixture + CASE_META（由 pipeline 统一注入，非模型生成）"""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CASE_META = {
    "test_login_success": {"id": "TC-001", "priority": "P0", "module": "登录"},
    "test_login_with_wrong_password": {"id": "TC-002", "priority": "P1", "module": "登录"},
    "test_add_to_cart": {"id": "TC-003", "priority": "P1", "module": "购物车"},
}


@pytest.fixture(scope="session")
def driver():
    """浏览器生命周期：检测到 CI 或 HEADLESS 环境变量时自动切无头模式"""
    options = Options()
    if os.environ.get("CI") or os.environ.get("HEADLESS"):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    d = webdriver.Chrome(options=options)
    yield d
    d.quit()
