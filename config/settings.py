import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# 从环境变量读取，支持 CI/CD 动态注入
#    现在与 BasePage.open 的 BASE_URL.rstrip("/") 约定保持一致
BASE_URL = os.getenv("BASE_URL", "https://cnuatportal.ecvision.cn/coachportal").rstrip("/")


#    （密码要求走环境变量、账号却硬编码，规则不一致）。现在账号与密码都只从环境变量读取
USERNAME = os.getenv("TEST_USER", "")
PASSWORD = os.getenv("TEST_PASS", "")


_missing = [
    name for name, value in (("TEST_USER", USERNAME), ("TEST_PASS", PASSWORD)) if not value
]
if _missing:
    raise RuntimeError(
        "缺少环境变量：" + "、".join(_missing)
        + f"。请在 {PROJECT_ROOT / '.env'} 或 CI/CD 中配置，禁止在代码中硬编码账号密码"
    )

# 126 邮箱登录相关配置：与门户账号独立，未配置时相应用例会跳过
MAIL_URL = os.getenv("MAIL_URL", "https://mail.126.com").rstrip("/")
MAIL_USER = os.getenv("MAIL_USER", "").strip()
MAIL_PASS = os.getenv("MAIL_PASS", "")

BROWSER = os.getenv("BROWSER", "chrome").strip().lower()

try:
    WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", "10"))
except ValueError:
    WAIT_TIMEOUT = 10
