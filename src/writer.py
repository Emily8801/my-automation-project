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


def append_case_meta(output_dir, case_id, func_name, priority="P2", module=""):
    """把用例编号↔函数映射写入 conftest 的 CASE_META（供Allure标签）"""
    p = os.path.join(output_dir, "conftest.py")
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            f.write("import pytest, allure\nCASE_META = {}\n")
    with open(p, encoding="utf-8") as f:
        txt = f.read()
    if func_name in txt:
        return
    line = f'    "{func_name}": {{"id": "{case_id}", "priority": "{priority}", "module": "{module}"}},\n'
    if "CASE_META = {" in txt:
        txt = txt.replace("CASE_META = {", "CASE_META = {\n" + line, 1)
    else:
        # 模型生成的 conftest 没有 CASE_META 标记 → 在文件末尾补一个
        if not txt.endswith("\n"):
            txt += "\n"
        txt += "\nCASE_META = {\n" + line + "}\n"
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt)
