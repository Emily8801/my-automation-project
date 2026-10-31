"""模型输出落盘：按 Stage C 提示词约定的 # FILE: 协议拆分并写入目标目录"""
import os
import re

# 匹配 "# FILE: 相对路径" 标题行
FILE_HEADER = re.compile(r"^#\s*FILE:\s*(\S+)\s*$", re.MULTILINE)
# 匹配 ```python ... ``` 代码块
CODE_BLOCK = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)


def split_files(text):
    """把模型输出拆成 {相对路径: 文件内容}。每个 # FILE: 标题后取第一个 python 代码块"""
    files = {}
    headers = list(FILE_HEADER.finditer(text))
    for i, header in enumerate(headers):
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = CODE_BLOCK.search(text, header.end(), end)
        if block:
            files[header.group(1)] = block.group(1).rstrip() + "\n"
    return files


def write_project(files, output_dir):
    """把拆分出的文件写入 output_dir"""
    for rel, content in files.items():
        path = os.path.join(output_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"已落盘 {len(files)} 个文件 → {output_dir}")


# 固定 conftest 模板：浏览器生命周期属框架基础设施，不让模型生成（防止幻觉代码）
CONFTEST_TEMPLATE = '''"""生成工程基础设施：driver fixture + CASE_META（由 pipeline 统一注入，非模型生成）"""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CASE_META = {
__CASE_META__
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
'''


def write_conftest(output_dir, metas):
    """注入固定 conftest.py：driver fixture + CASE_META（覆盖模型可能违规生成的版本）

    metas: [(case_id, func_name, priority, module), ...]
    """
    lines = "".join(
        f'    "{fn}": {{"id": "{cid}", "priority": "{pr}", "module": "{mod}"}},\n'
        for cid, fn, pr, mod in metas
    )
    content = CONFTEST_TEMPLATE.replace("__CASE_META__", lines.rstrip("\n"))
    with open(os.path.join(output_dir, "conftest.py"), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已注入固定 conftest.py（{len(metas)} 条 CASE_META）")
