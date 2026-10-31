"""（可选）失败自愈：把失败日志回传模型，产出修复建议或修复代码

思路：pytest 失败 → 收集报错堆栈 + 相关源文件 → 连同 stage_d 提示词发给模型
→ 模型给出修复代码 → 人工确认后落盘（修复不入库直接生效，必须人审）。
"""
from src import llm


def heal(test_file: str, error_log: str) -> str:
    """传入失败的用例文件路径与报错日志，返回模型的修复建议文本

    TODO: 1. 读取 test_file 源码；2. 拼装 stage_d_selfcheck.md + 源码 + 日志；
    3. 调 llm.chat；4. 输出给人工确认（是否落盘由 pipeline 决定）。
    """
    raise NotImplementedError
