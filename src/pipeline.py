"""主控：编排 A(筛选) → B(复核) → C(生成) → D(自检) → 落盘 → 邮件

用法：
    python cli.py inputs/cases.csv     # cli.py 解析参数后调本模块的 run()

流程开关见 config.yaml 的 run 段：
    human_gate: 每段跑完暂停，人工确认后再进下一段
    resume:     已存在的中间产物跳过（断点续跑）
"""
import json
from pathlib import Path

from src import llm, writer

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(stage_file: str) -> str:
    """读取某一段的提示词模板"""
    return (PROMPTS_DIR / stage_file).read_text(encoding="utf-8")


def _extract_json_array(text: str) -> list[dict]:
    """从模型输出中提取 JSON 数组（A/B 段提示词末尾的【附加】约束保证其存在）"""
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("模型输出中未找到 JSON 数组，请检查提示词或重试")
    return json.loads(text[start:end + 1])


def run(csv_path: str) -> None:
    """四段流水线入口。csv_path: 手工用例表路径"""
    cfg = llm.load_config()
    run_cfg = cfg["run"]
    output_dir = Path(run_cfg["output_dir"])
    output_dir.mkdir(exist_ok=True)

    # TODO: 1. 用 pandas 读取 csv_path，转成用例列表文本
    # TODO: 2. Stage A：stage_a_select.md + 用例列表 → chat → 存 output/stage_a.md
    #          用 _extract_json_array 取出"适合/部分适合"的用例
    # TODO: 3. Stage B：stage_b_review.md + A 段结果 → chat → 存 output/stage_b.md
    #          过滤出 action 为"直接做/改造后做"的用例
    # TODO: 4. Stage C：逐条用例走 stage_c_generate.md → chat → writer.split_files
    #          → writer.write_files 落盘到 run_cfg["project_dir"]
    # TODO: 5. Stage D：stage_d_selfcheck.md + 生成代码 → chat → 若 RISK=HIGH 则告警
    # TODO: 6. human_gate 为 true 时，每段之间 input("确认继续？(y/n)")
    # TODO: 7. 跑 pytest 后调 mailer.send_report 发结果邮件
    raise NotImplementedError("pipeline 骨架已就位，逐段实现见上方 TODO")
