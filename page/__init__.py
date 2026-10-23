# page/__init__.py
# 🟡 规范：原写法 `from.base_page import` 虽然能被解析，但缺少空格不符合 PEP8，且可读性差
from .base_page import BasePage
from .login_page import LoginPage

# 🟡 说明：这里只导出 BasePage / LoginPage；其余页面对象（MastersPage、SearchDdpPage、
#    ViewManagementPage、CopyPMPage、PMCreatePage）未纳入 __all__，`from page import *` 拿不到它们。
#    本次不做改动，避免与 page.JD_home_page -> page.JD_product_page 形成循环导入。
__all__ = ["BasePage", "LoginPage"]
