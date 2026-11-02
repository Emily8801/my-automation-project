"""
主控编排: A(价值筛) -> B(技术复核) -> C(单条生成脚本) -> 落盘 + 写入 CASE_META
用法: python src/pipeline.py
"""
import csv
import json
import os
import re
import yaml

from llm import chat
from writer import split_files, write_project, write_conftest


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
    """从模型返回文本中提取 JSON 数组(兼容 markdown 代码块包裹)"""
    # 优先匹配 ```json ... ``` 代码块里的数组
    code_block = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.S)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass
    # 回退: 直接匹配最外层 [](贪婪到最后一个 ])
    m = re.search(r"\[.*\]", text, re.S)
    return json.loads(m.group(0)) if m else []


VERDICT_COL = "stage_a_verdict"    # Stage A 判决写回列: 判决(规则)+建议
APPROVAL_COL = "approve_generate"  # 人工放行列: 填"是"才进入生成


def write_verdicts_to_csv(csv_path: str, a_result: list[dict]):
    """把 Stage A 判决写回用例台账, 供人工审核后圈定生成范围"""
    with open(csv_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return
    fields = list(rows[0].keys())
    for col in (VERDICT_COL, APPROVAL_COL):
        if col not in fields:
            fields.append(col)
    verdicts = {x["case_id"]: x for x in a_result}
    for r in rows:
        v = verdicts.get(r.get("case_id", ""))
        if v:
            text = f"{v.get('verdict', '?')}({v.get('rule', '-')})"
            if v.get("suggestion"):
                text += f" {v['suggestion']}"
            r[VERDICT_COL] = text
        r.setdefault(APPROVAL_COL, "")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def run():
    cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    out_dir = cfg["paths"]["output"]
    cases = load_cases()
    print(f"📋 加载 {len(cases)} 条用例")

    # ========== Stage A: 价值筛 ==========
    print("\n🔍 Stage A: 价值筛选...")
    a_prompt = load_prompt("stage_a_select.md") + \
        "\n\n[用例列表]\n" + json.dumps(cases, ensure_ascii=False)
    a_result = parse_json(chat(a_prompt))
    # 提示词约定字段为 verdict: "适合/不适合/部分适合", 部分适合也进入复核
    suitable_ids = {x["case_id"] for x in a_result
                    if x.get("verdict") in ("适合", "部分适合")}
    print(f"   ✅ 适合/部分适合: {len(suitable_ids)} 条 | ❌ 不适合: {len(cases) - len(suitable_ids)} 条")
    # 逐条判决明细: 让每条用例"为什么适合/不适合"看得见
    print("   📝 Stage A 判决明细:")
    for x in a_result:
        print(f"      {x.get('case_id','?')}: {x.get('verdict','?')} "
              f"(规则{x.get('rule','-')}) {x.get('suggestion','')}", flush=True)
    # 判决结果存盘: 审核依据 + 断点排查
    out_mid = cfg.get("run", {}).get("output_dir", "output")
    os.makedirs(out_mid, exist_ok=True)
    with open(os.path.join(out_mid, "stage_a_result.json"), "w", encoding="utf-8") as f:
        json.dump(a_result, f, ensure_ascii=False, indent=2)

    # 判决写回台账: 每条用例"合适/不合适+理由"人工可见
    write_verdicts_to_csv(cfg["paths"]["inputs"], a_result)

    # human_gate: 仅人工在 approve_generate 列标"是"的用例才进入 Stage B/C/D
    if cfg.get("run", {}).get("human_gate"):
        approved = {c["case_id"] for c in load_cases()
                    if c.get(APPROVAL_COL, "").strip() == "是"}
        pending = suitable_ids - approved
        if pending:
            print(f"   ⏸️ 人工门禁: {len(pending)} 条判决通过但未放行, 跳过 "
                  f"({', '.join(sorted(pending))})")
        suitable_ids &= approved
        if not suitable_ids:
            print("⏸️ 判决已写回 inputs/cases.csv. 请审核 stage_a_verdict 列, "
                  "对要生成的用例在 approve_generate 列填'是', 然后重跑 pipeline")
            return

    # ========== Stage B: 技术复核 ==========
    b_cases = [c for c in cases if c["case_id"] in suitable_ids]
    if not b_cases:
        print("⚠️ 没有适合自动化的用例, 流程结束.")
        return

    print("\n🔧 Stage B: 技术复核...")
    b_prompt = load_prompt("stage_b_review.md") + \
        "\n\n[待复核用例]\n" + json.dumps(b_cases, ensure_ascii=False)
    reviews = {x["case_id"]: x for x in parse_json(chat(b_prompt))}
    # 按提示词约定的 action 字段过滤: "直接做/改造后做"才生成, "放弃自动化"跳过
    todo_cases = [c for c in b_cases
                  if reviews.get(c["case_id"], {}).get("action") != "放弃自动化"]
    print(f"   ✅ 复核完成: {len(todo_cases)} 条进入生成, {len(b_cases) - len(todo_cases)} 条建议放弃")
    print("   📝 Stage B 复核明细:")
    for x in reviews.values():
        print(f"      {x.get('case_id','?')}: {x.get('action','?')} "
              f"| 风险: {x.get('risk','-')} | {x.get('solution','')}", flush=True)
    with open(os.path.join(out_mid, "stage_b_result.json"), "w", encoding="utf-8") as f:
        json.dump(list(reviews.values()), f, ensure_ascii=False, indent=2)

    # ========== Stage C: 逐条生成脚本 + Stage D: 生成质量自检 ==========
    print("\n⚙️ Stage C: 逐条生成脚本...")
    metas = []  # (case_id, func_name, priority, module), 循环结束后统一写入
    d_reports = []  # Stage D 自检报告, 循环结束后统一存盘
    for i, c in enumerate(todo_cases, 1):
        rid = c["case_id"]
        print(f"   [{i}/{len(todo_cases)}] 生成 {rid} ...")
        prompt = (
            load_prompt("stage_c_generate.md")
            + "\n\n[待转换用例]\n" + json.dumps(c, ensure_ascii=False)
            + "\n\n[阶段B已确认的技术方案/定位建议]\n"
            + json.dumps(reviews.get(rid, {}), ensure_ascii=False)
        )
        # 注入已存在的页面对象: 共享 page 文件被多条用例逐条覆盖生成,
        # 模型看不到前序版本就会只写本条用到的方法, 导致既有方法丢失(TC-101 教训)
        pages_dir = os.path.join(out_dir, "pages")
        if os.path.isdir(pages_dir):
            existing = []
            for fn in sorted(os.listdir(pages_dir)):
                if fn.endswith(".py") and not fn.startswith("__"):
                    with open(os.path.join(pages_dir, fn), encoding="utf-8") as f:
                        existing.append(f"# FILE: pages/{fn}\n{f.read()}")
            if existing:
                prompt += "\n\n[已存在的页面对象]\n" + "\n\n".join(existing)
        raw = chat(prompt)
        files = split_files(raw)
        if not files:
            print(f"   ⚠️ {rid} 未解析出文件块, 跳过")
            continue
        write_project(files, out_dir)
        for rel in files:
            print(f"      📄 {rel}", flush=True)
        # Stage D: 反例猎手自检(查 sleep/脆定位器/宽松断言/不可独立重跑), RISK=HIGH 则提醒人工介入
        code_pack = "\n\n".join(f"# FILE: {rel}\n{content}" for rel, content in files.items())
        d_resp = chat(load_prompt("stage_d_selfcheck.md") + "\n\n" + code_pack)
        # 以 JSON 问题清单为准判定高危(模型常把 "RISK=HIGH" 当标题写"无高危问题", 纯字符串匹配会误报)
        d_issues = parse_json(d_resp)
        d_high = any(str(x.get("risk", "")).upper() == "HIGH" for x in d_issues) \
            if d_issues else "RISK=HIGH" in d_resp and "无高危" not in d_resp
        print(f"      🕵️ Stage D 自检: {'⚠️ 发现高风险项, 建议人工复核(output/stage_d_result.md)' if d_high else '通过'}", flush=True)
        d_reports.append(f"## {rid}\n\n{d_resp}")
        # 收集 test_ 函数名 <-> 用例编号映射(此时不写, 避免被后续用例的 conftest.py 覆盖)
        for rel, content in files.items():
            if rel.startswith("tests/") and content:
                fn_match = re.search(r"def (test_\w+)", content)
                if fn_match:
                    metas.append((rid, fn_match.group(1),
                                  c.get("priority", "P2"), c.get("module", "")))

    # 全部生成完成后注入固定 conftest(driver fixture + CASE_META)
    # 浏览器生命周期属于框架基础设施, 交给模型生成不可靠(曾出现 pytest.config 幻觉代码),
    # 因此由 pipeline 统一写入, 模型只允许产出 pages/ 与 tests/
    write_conftest(out_dir, metas)

    # Stage D 自检报告统一存盘
    if d_reports:
        with open(os.path.join(out_mid, "stage_d_result.md"), "w", encoding="utf-8") as f:
            f.write("\n\n".join(d_reports))

    print(f"\n✅ 全部生成完成! 产物目录: {out_dir}")
    print("📌 下一步: git add . && git commit && git push -> CI 自动跑测+出报告+发邮件")


if __name__ == "__main__":
    run()
