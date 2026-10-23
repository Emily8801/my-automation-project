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
    sys.exit(exit_code)
