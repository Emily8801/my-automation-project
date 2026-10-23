import os
from pathlib import Path

from dotenv import load_dotenv

# 🔴 修复：原 load_dotenv() 不带路径，会按"当前工作目录"向上查找 .env。
#    从 bin/run_test.py、IDE、CI 等不同目录启动时会静默读不到 .env，
#    导致 PASSWORD 为空 → 本模块 import 时直接抛异常 → 所有 page/testcase 连带导入失败。
#    改为锚定项目根目录（settings.py 的上一级目录的上一级）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# 从环境变量读取，支持 CI/CD 动态注入
# 🟡 修复：统一去掉末尾斜杠。原默认值末尾带 "/"，调用方再拼 "/coachportal" 会出现双斜杠；
#    现在与 BasePage.open 的 BASE_URL.rstrip("/") 约定保持一致
BASE_URL = os.getenv("BASE_URL", "https://cnuatportal.ecvision.cn/coachportal").rstrip("/")

# 🔴 修复：原代码给 TEST_USER 硬编码了真实企业邮箱作为默认值，违反"禁止在代码中 hard code"的原则
#    （密码要求走环境变量、账号却硬编码，规则不一致）。现在账号与密码都只从环境变量读取
USERNAME = os.getenv("TEST_USER", "")
PASSWORD = os.getenv("TEST_PASS", "")

# 🟠 说明：这里保留"导入即校验"的 fail-fast，保证没有凭据时不跑用例；
#    代价是 pytest --collect-only / IDE 索引在缺少环境变量时也会报错。
#    若希望无凭据时也能正常收集用例，可改为提供 validate_credentials()，在登录前置里再调用。
_missing = [
    name for name, value in (("TEST_USER", USERNAME), ("TEST_PASS", PASSWORD)) if not value
]
if _missing:
    raise RuntimeError(
        "缺少环境变量：" + "、".join(_missing)
        + f"。请在 {PROJECT_ROOT / '.env'} 或 CI/CD 中配置，禁止在代码中硬编码账号密码"
    )

# 🟡 BROWSER 统一转小写，避免配置成 "Chrome" 时与 driver_factory 的映射不一致
BROWSER = os.getenv("BROWSER", "chrome").strip().lower()

# 🟠 修复：int() 遇到非数字（如 WAIT_TIMEOUT=abc）会直接 ValueError 导致启动失败，这里做容错
try:
    WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", "10"))
except ValueError:
    WAIT_TIMEOUT = 10

# 🟠 修复：原 WAIT_TIMEOUT 全项目无人使用（BasePage 硬编码 default_timeout = 10），
#    属于"死配置"。现已在 page/base_page.py 中导入并作为 self.default_timeout 使用，
#    让 .env 里的 WAIT_TIMEOUT 真正生效。
