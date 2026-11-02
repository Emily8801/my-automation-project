from datetime import datetime
from pathlib import Path

import pytest

from common.logger import get_logger

# 统一锚定项目根目录，避免从不同工作目录启动时路径漂移
PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"

logger = get_logger("fixture")


def _get_driver(item):
    """兼容两种用例风格获取 driver

    - pytest 风格:driver 由 fixture 注入，存在于 item.funcargs
    - unittest 风格:driver 挂在 TestCase 实例的 self.driver 上，通过 item.instance 获取
    """
    try:
        driver = item.funcargs.get("driver")
    except AttributeError:
        driver = None
    if driver is None:
        driver = getattr(getattr(item, "instance", None), "driver", None)
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图并记录日志"""
    outcome = yield
    report = outcome.get_result()

    # 仅在执行阶段失败时触发（排除 setup/teardown 失败）
    if report.when != "call" or not report.failed:
        return

    # 🟠 修复：原代码只从 item.funcargs 取 driver，但现有用例全部是 unittest.TestCase，
    #    driver 在 self.driver 上，funcargs 里没有 → 截图永远不会触发。
    driver = _get_driver(item)
    if driver is None:
        logger.warning(f"用例 {item.name} 执行失败，但未获取到 driver,跳过截图")
        return

    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        screenshot_path = SCREENSHOT_DIR / f"{item.name}_{timestamp}.png"
        driver.save_screenshot(str(screenshot_path))
        logger.error(f"📸 测试失败截图已保存:{screenshot_path}")
    except Exception as e:
        # 截图失败不能影响测试结果的收集
        logger.error(f"❌ 失败截图保存失败: {e}")

