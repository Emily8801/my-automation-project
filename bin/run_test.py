import os
import sys
import pytest
from setup_env import setup

if __name__ == "__main__":
    setup()
    # 切换到项目根目录
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    # 让项目根目录也能被导入
    if root not in sys.path:
        sys.path.insert(0, root)


    # 默认运行 tests 目录下的用例，并生成 HTML 报告
    exit_code = pytest.main([
        "testcase",
        "-v",
        "--html=report/report.html",
        "--self-contained-html"
    ]+sys.argv[1:])

    # 跑完自动发送 AutoTest 同款报告邮件（读 reports/allure-results，配置在 config.yaml）
    # 注意：只有用例产出过 allure-results 才会发；邮件失败不影响测试结果
    sys.path.insert(0, os.path.join(root, "src"))
    try:
        from mailer import send_report_mail
        send_report_mail()
    except Exception as e:
        print(f"⚠️ 结果邮件发送失败（不影响本次测试结果）: {e}")

    sys.exit(exit_code)
