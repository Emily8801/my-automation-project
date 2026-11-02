"""全局 fixture：Chrome driver 的创建与销毁 + 登录页 Page Object 注入。

支持无头模式：pytest --headless
"""

import pytest
from selenium import webdriver

from pages.login_page import LoginPage


def pytest_addoption(parser):
    """注册 --headless 命令行参数。"""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="以无头模式运行 Chrome（无显示器 / CI 环境建议开启）",
    )


@pytest.fixture()
def driver(request):
    """创建 Chrome driver，用例结束后无条件 driver.quit() 释放进程。"""
    options = webdriver.ChromeOptions()
    # 容器 / CI 环境下的常规启动参数，本地同样适用
    for arg in ("--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"):
        options.add_argument(arg)

    headless = request.config.getoption("--headless")
    if headless:
        # 无头模式下没有真实显示器，需显式指定窗口大小
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    # Selenium 4.6+ 自带 Selenium Manager，自动匹配并下载 ChromeDriver
    drv = webdriver.Chrome(options=options)
    if not headless:
        drv.maximize_window()

    # 显式等待由 Page Object 内部统一控制，关掉隐式等待避免两者叠加
    drv.implicitly_wait(0)

    yield drv

    # 无论用例成功还是失败，都必须退出浏览器
    drv.quit()


@pytest.fixture()
def login_page(driver):
    """注入登录页 Page Object，并保证每个用例都从登录页开始。"""
    page = LoginPage(driver)
    page.open()
    yield page
