from importlib.metadata import entry_points

import os

from selenium import webdriver
from config.settings import BROWSER
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions




def get_driver(browser: str = "chrome"):
    browser_map = {
        "chrome": (webdriver.Chrome, webdriver.ChromeOptions),
        "firefox": (webdriver.Firefox, webdriver.FirefoxOptions),
        "edge": (webdriver.Edge, webdriver.EdgeOptions),
    }

    browser_lower = browser.lower()
    entry = browser_map.get(browser_lower)
    if not entry:
        raise ValueError(f"不支持的浏览器:{browser},仅支持:{list(browser_map.keys())}")


    driver_class, options_class = entry       # ← 变量是"容器"，装什么类型由数据决定
    options = options_class()                 # ← 调用方式是"统一的"，但实际执行的构造函数不同

    if browser_lower == "chrome":
        for arg in ("--disable-gpu","--no-sandbox","--disable-dev-shm-usage"):
            options.add_argument(arg)
        # CI 云端没有显示器，自动切无头模式（GitHub Actions 会注入 CI=true；本地想无头可设 HEADLESS=1）
        if os.getenv("CI") or os.getenv("HEADLESS"):
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")

    driver = driver_class(options=options)
    driver.maximize_window()
    return driver
