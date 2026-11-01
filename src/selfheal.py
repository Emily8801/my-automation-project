"""
失败自愈模块: 解析 Allure 失败结果 ->  回传 LLM 生成修复补丁 ->  自动创建 PR
用法: python src/selfheal.py
依赖: 环境变量 LLM_API_KEY；开 PR 还需 GITHUB_TOKEN, GITHUB_REPOSITORY
"""
import glob
import json
import os
import re
import subprocess
from pathlib import Path

import requests
from llm import chat

ALLURE_RESULTS = "reports/allure-results"
SEARCH_DIRS = ("output/generated_project/tests", "testcase", "tests")
PATCH_DIR = Path("output/selfheal")

SELFHEAL_PROMPT = """\
角色: 资深 SDET. 以下自动化用例执行失败, 请分析根因并给出修复后的完整文件内容. 

[失败信息]
- 用例名称: {name}
- 错误类型: {error_type}
- 错误信息: {message}
- 堆栈摘要: {trace}

[原始脚本]
```python
{source}
```

[修复要求]
1. 只修复稳定性问题(定位器失效, 等待不足, iframe/窗口切换缺失), 不得改变用例的业务意图
2. 禁止 time.sleep, 一律 WebDriverWait + expected_conditions
3. 只输出修复后的完整文件, 用一个 ```python 代码块包裹, 不要任何解释
4. 若判断无法自动修复(需求变更/验证码拦截/环境问题), 只输出一行: CANNOT_FIX: 原因
"""

CODE_BLOCK = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)


def find_failed_cases(results_dir=ALLURE_RESULTS):
    """解析 allure-results 下的 *-result.json, 返回失败/崩溃用例列表"""
    failed = []
    for path in glob.glob(os.path.join(results_dir, "*-result.json")):
        with open(path, encoding="utf-8") as f:
            result = json.load(f)
        if result.get("status") not in ("failed", "broken"):
            continue
        details = result.get("statusDetails") or {}
        message = details.get("message", "")
        failed.append({
            "name": result.get("name", ""),
            "error_type": message.split(":", 1)[0] if message else result["status"],
            "message": message[:500],
            "trace": (details.get("trace") or "")[:1500],
        })
    return failed


def find_source(test_name):
    """在候选目录里找包含该测试函数的源码文件, 返回 (路径, 源码)"""
    for root in SEARCH_DIRS:
        for path in glob.glob(os.path.join(root, "**", "*.py"), recursive=True):
            source = Path(path).read_text(encoding="utf-8")
            if f"def {test_name}" in source:
                return Path(path), source
    return None, ""


def heal_case(case):
    """对单个失败用例走一遍自愈: 找源码 ->  拼提示词 ->  调模型 ->  提取修复代码"""
    path, source = find_source(case["name"])
    if not path:
        return {"status": "no_source", "case": case}

    prompt = SELFHEAL_PROMPT.format(**case, source=source)
    reply = chat(prompt)

    if "CANNOT_FIX" in reply:
        return {"status": "cannot_fix", "case": case, "reason": reply.strip()}
    block = CODE_BLOCK.search(reply)
    if not block:
        return {"status": "no_code", "case": case}
    return {"status": "fixed", "case": case, "path": path, "code": block.group(1)}


def save_patches(patches):
    """修复代码先落盘到 output/selfheal/ 供人工审阅, 不直接覆盖原文件"""
    PATCH_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for p in patches:
        target = PATCH_DIR / p["path"].name
        target.write_text(p["code"], encoding="utf-8")
        saved.append((p["path"], target))
    return saved


def create_pr(patches):
    """应用补丁到原文件并开 PR(需要 GITHUB_TOKEN / GITHUB_REPOSITORY)"""
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")  # 形如 Emily8801/my-automation-project
    if not token or not repo:
        print("未配置 GITHUB_TOKEN/GITHUB_REPOSITORY, 跳过开 PR, 补丁在 output/selfheal/ 人工处理")
        return

    for p in patches:
        p["path"].write_text(p["code"], encoding="utf-8")

    branch = f"selfheal/{os.getenv('GITHUB_RUN_ID', 'local')}"
    subprocess.run(["git", "checkout", "-b", branch], check=True)
    subprocess.run(["git", "add"] + [str(p["path"]) for p in patches], check=True)
    subprocess.run(["git", "commit", "-m", "fix: selfheal 自动修复失败用例"], check=True)
    subprocess.run(["git", "push", "origin", branch], check=True)

    resp = requests.post(
        f"https://api.github.com/repos/{repo}/pulls",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "selfheal 自动修复", "head": branch, "base": "main",
              "body": "失败用例的自动修复补丁, 请人工 review 后合并"},
        timeout=30,
    )
    resp.raise_for_status()
    print(f"PR 已创建: {resp.json()['html_url']}")


def main():
    failed = find_failed_cases()
    if not failed:
        print("无失败用例, 无需自愈")
        return
    print(f"发现 {len(failed)} 个失败用例, 开始自愈")

    fixed = [r for r in (heal_case(c) for c in failed) if r["status"] == "fixed"]
    if fixed:
        saved = save_patches(fixed)
        for origin, patch in saved:
            print(f"补丁已保存: {patch}(原文件: {origin})")
        create_pr(fixed)
    else:
        print("没有可自动修复的用例")


if __name__ == "__main__":
    main()
