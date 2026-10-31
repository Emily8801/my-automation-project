# 测试用例 → 自动化脚本 生成器（含 Allure + GitHub Actions + 邮件）

把"需求 → 功能用例 → 自动化脚本 → CI 跑测 → Allure 报告 → 邮件推送"串成一条可追溯流水线。

## 一、四段链路

需求文档 → `inputs/cases.csv`(带防翻车列) → Stage A 价值筛 → Stage B 技术复核 → Stage C 分文件脚本(带Allure标签) → writer 落盘 → Git → GitHub Actions 跑测+出 Allure+部署 Pages → 解析结果拼 HTML 摘要 → 每次跑完按收件人路由发邮箱 → (可选)失败自愈开 PR。

## 二、目录结构

```
case2auto/
├── config.yaml            # 模型 / 运行 / Selenium / 邮件 配置
├── requirements.txt
├── cli.py                 # 命令行入口
├── prompts/               # 四段提示词（团队调优只改这里，下次跑生效）
│   ├── stage_a_select.md
│   ├── stage_b_review.md
│   ├── stage_c_generate.md
│   └── stage_d_selfcheck.md
├── src/
│   ├── llm_client.py      # 大模型调用封装
│   ├── loader.py          # 用例表解析
│   ├── orchestrator.py    # 四段编排核心（含断点续跑 + 人工关卡 + 质量门禁）
│   ├── writer.py          # 按 # FILE: 协议拆分落盘
│   └── mailer.py          # 解析 Allure 结果 → 拼 HTML 摘要 → SMTP 发送
├── inputs/cases.csv       # 标准用例模板
├── .github/workflows/     # ci.yml（跑测+Allure+Pages+邮件）、selfheal.yml
└── .gitignore
```

## 三、本地跑通

```bash
pip install -r requirements.txt
export LLM_API_KEY=你的模型key
python cli.py inputs/cases.csv            # A→B→C→D 逐条生成，human_gate 每段暂停
```

## 四、本地验证报告+邮件

```bash
pytest output/generated_project/tests --alluredir=reports/allure-results --clean-alluredir
allure generate reports/allure-results -o reports/allure-report --clean
SMTP_AUTH_CODE=你的授权码 python src/mailer.py     # 看收件箱
```

## 五、接入 GitHub

```bash
git init && git add . && git commit -m "feat: case2auto 生成器+Allure+CI+邮件"
git branch -M main
git remote add origin git@github.com:<你的名>/case2auto.git
git push -u origin main
# 仓库 Settings → Pages → Source 选 GitHub Actions
```

## 六、SMTP 授权码（最易踩坑）

password 不能填登录密码，必须填授权码，并存为仓库 Secrets（Settings → Secrets and variables → Actions）：

| 邮箱                                                                         | host:port          | 拿授权码方式              |
| -------------------------------------------------------------------------- | ------------------ | ------------------- |
| QQ                                                                         | smtp.qq.com:465    | 设置→账户→开启SMTP→生成授权码  |
| 163                                                                        | smtp.163.com:465   | 设置→POP3/SMTP→开启→授权码 |
| Gmail                                                                      | smtp.gmail.com:587 | 开两步验证→应用专用密码        |
| GitHub Secrets 命名 `SMTP_AUTH_CODE`，与 ci.yml 中 `secrets.SMTP_AUTH_CODE` 对应。 | <br />             | <br />              |

## 七、关于"跑一次发一次，成败都发"

- `ci.yml` 把"Run tests"设为 `continue-on-error: true`，邮件步骤在其后，保证无论成败都执行。
- `mailer.py` 默认对 `recipients.always` 每次必发。若不想按严重程度加发，删掉 `on_failure`/`on_p0_failure` 只留 `always` 即可。

## 八、落地建议

1. 先拿 TC-LOGIN-001 单条跑通（human\_gate=true），盯四段产物+拆分出的 .py 确认质量再批量。
2. prompts/\*.md 是核心资产，把团队踩过的坑持续写进去，生成器越用越准。
3. 别追求全自动：human\_gate 与 needs\_human/ 就是把 80% 体力活自动化、20% 关键判断留给人。

