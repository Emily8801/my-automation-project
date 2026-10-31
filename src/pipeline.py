"""
主控编排：A(价值筛) → B(技术复核) → C(单条生成脚本) → 落盘 + 写入 CASE_META
用法：python src/pipeline.py
"""
import csv
import json
import os
import re
import yaml

from llm import chat
from writer import split_files, write_project, append_case_meta


def load_prompt(name: str) -> str:
    """从 prompts/ 目录读取提示词模板"""
    cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    path = os.path.join(cfg["paths"]["prompts"], name)
    return open(path, encoding="utf-8").read()


def load_cases() -> list[dict]:
    """读取 inputs/cases.csv 用例台账"""
    cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    with open(cfg["paths"]["inputs"], encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_json(text: str) -> list[dict]:
    """从模型返回文本中提取 JSON 数组（兼容 markdown 代码块包裹）"""
    # 优先匹配 ```json ... ``` 代码块里的数组
    code_block = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.S)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass
    # 回退：直接匹配最外层 []（贪婪到最后一个 ]）
    m = re.search(r"\[.*\]", text, re.S)
    return json.loads(m.group(0)) if m else []


def run():
    cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    out_dir = cfg["paths"]["output"]
    cases = load_cases()
    print(f"📋 加载 {len(cases)} 条用例")

    # ========== Stage A：价值筛 ==========
    print("\n🔍 Stage A：价值筛选...")
    a_prompt = load_prompt("stage_a_select.md") + \
        "\n\n【用例列表】\n" + json.dumps(cases, ensure_ascii=False)
    a_result = parse_json(chat(a_prompt))
    # 提示词约定字段为 verdict："适合/不适合/部分适合"，部分适合也进入复核
    suitable_ids = {x["case_id"] for x in a_result
                    if x.get("verdict") in ("适合", "部分适合")}
    print(f"   ✅ 适合/部分适合：{len(suitable_ids)} 条 | ❌ 不适合：{len(cases) - len(suitable_ids)} 条")

    # ========== Stage B：技术复核 ==========
    b_cases = [c for c in cases if c["case_id"] in suitable_ids]
    if not b_cases:
        print("⚠️ 没有适合自动化的用例，流程结束。")
        return

    print("\n🔧 Stage B：技术复核...")
    b_prompt = load_prompt("stage_b_review.md") + \
        "\n\n【待复核用例】\n" + json.dumps(b_cases, ensure_ascii=False)
    reviews = {x["case_id"]: x for x in parse_json(chat(b_prompt))}
    # 按提示词约定的 action 字段过滤："直接做/改造后做"才生成，"放弃自动化"跳过
    todo_cases = [c for c in b_cases
                  if reviews.get(c["case_id"], {}).get("action") != "放弃自动化"]
    print(f"   ✅ 复核完成：{len(todo_cases)} 条进入生成，{len(b_cases) - len(todo_cases)} 条建议放弃")

    # ========== Stage C：逐条生成脚本 ==========
    print("\n⚙️ Stage C：逐条生成脚本...")
    for i, c in enumerate(todo_cases, 1):
        rid = c["case_id"]
        print(f"   [{i}/{len(todo_cases)}] 生成 {rid} ...")
        prompt = (
            load_prompt("stage_c_generate.md")
            + "\n\n【待转换用例】\n" + json.dumps(c, ensure_ascii=False)
            + "\n\n【阶段B已确认的技术方案/定位建议】\n"
            + json.dumps(reviews.get(rid, {}), ensure_ascii=False)
        )
        raw = chat(prompt)
        files = split_files(raw)
        if not files:
            print(f"   ⚠️ {rid} 未解析出文件块，跳过")
            continue
        write_project(files, out_dir)
        # 把 test_ 函数名 ↔ 用例编号映射写入 conftest.CASE_META
        for rel, content in files.items():
            if rel.startswith("tests/") and content:
                fn_match = re.search(r"def (test_\w+)", content)
                if fn_match:
                    append_case_meta(
                        out_dir,
                        rid,
                        fn_match.group(1),
                        priority=c.get("priority", "P2"),
                        module=c.get("module", ""),
                    )

    print(f"\n✅ 全部生成完成！产物目录：{out_dir}")
    print("📌 下一步：git add . && git commit && git push → CI 自动跑测+出报告+发邮件")


if __name__ == "__main__":
    run()
