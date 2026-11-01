import os, json, glob, smtplib, zipfile, ssl, yaml
from dotenv import load_dotenv
load_dotenv()  # 让 .env 里的 SMTP_AUTH_CODE 生效
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr
ICON = {"passed": "✅", "failed": "❌", "broken": "💥", "skipped": "⏭️", "unknown": "❓"}
def _cfg(p="config.yaml"): return yaml.safe_load(open(p, encoding="utf-8"))["mail"]
def _parse(d="reports/allure-results"):
    cases, passed, failed = [], 0, 0
    for f in glob.glob(os.path.join(d, "*-result.json")):
        x = json.load(open(f, encoding="utf-8"))
        st = x.get("status", "unknown")
        story = next((l.get("value") for l in x.get("labels", []) if l.get("name") == "story"), "")
        sev   = next((l.get("value") for l in x.get("labels", []) if l.get("name") == "severity"), "normal")
        if st == "passed": passed += 1
        if st in ("failed", "broken"): failed += 1
        cases.append({"name": x.get("name", ""), "status": st, "story": story, "sev": sev,
                      "msg": x.get("statusDetails", {}).get("message", "")[:200]})
    total = len(cases)
    return cases, {"total": total, "passed": passed, "failed": failed,
                   "rate": (passed / total * 100) if total else 0}
def _html(cases, s, url):
    ok = s["failed"] == 0
    color = "#28a745" if ok else "#dc3545"
    title = "✅ 自动化测试全部通过" if ok else f"❌ 有 {s['failed']} 条用例失败"
    rows = "".join(
        f"<tr><td>{ICON.get(c['status'],'❓')}</td><td>{c['story']}</td><td>{c['name']}</td>"
        f"<td>{c['status']}</td><td style='color:#888'>{c['msg'][:120].replace(chr(10),' ')}</td></tr>"
        for c in sorted(cases, key=lambda x: x["status"] != "failed"))
    return f"""<div style='font-family:Segoe UI,Arial,sans-serif;max-width:760px;margin:auto'>
      <div style='background:{color};color:#fff;padding:16px 20px;border-radius:8px 8px 0 0'>
        <h2 style='margin:0'>{title}</h2>
        <p style='margin:6px 0 0'>通过率 {s['rate']:.1f}%(通过 {s['passed']} / 共 {s['total']})</p></div>
      <div style='border:1px solid #eee;border-top:0;padding:16px 20px;border-radius:0 0 8px 8px'>
        <p>👉 <a href='{url}'>查看完整 Allure 报告</a></p>
        <table width='100%' cellpadding='6' style='border-collapse:collapse;font-size:13px'>
          <tr style='background:#f6f8fa'><th>状态</th><th>编号</th><th>标题</th><th>结果</th><th>信息</th></tr>
          {rows}</table>
        <p style='color:#999;font-size:12px'>本邮件由 case2auto CI 自动生成. </p></div></div>"""
def _zip(src="reports/allure-report", dst="reports/allure-report.zip"):
    if not os.path.isdir(src): return None
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(src):
            for fn in fs:
                p = os.path.join(r, fn); z.write(p, os.path.relpath(p, src))
    return dst
def send_report_mail(cfg_path="config.yaml"):
    cfg = _cfg(cfg_path)
    if not cfg.get("enabled"):
        print("邮件已关闭, 跳过. "); return
    m = cfg["smtp"]; pw = os.path.expandvars(m["password"])
    cases, s = _parse()
    if s["total"] == 0:
        print("无测试结果, 跳过. "); return
    # 收件人路由(always 每次必发 ->  成败都发)
    rec = list(cfg["recipients"]["always"])
    if s["failed"] > 0:
        rec += cfg["recipients"].get("on_failure", [])
        if any(c["sev"] in ("blocker", "critical") and c["status"] == "failed" for c in cases):
            rec += cfg["recipients"].get("on_p0_failure", [])
    rec = list(dict.fromkeys(rec))
    ok = s["failed"] == 0
    msg = MIMEMultipart("related")
    msg["Subject"] = Header(f"[AutoTest] {'✅通过' if ok else '❌失败'} 通过率{s['rate']:.0f}%", "utf-8")
    msg["From"] = formataddr(("自动化测试助手", m["user"]))
    msg["To"] = ", ".join(rec)
    msg.attach(MIMEText(_html(cases, s, cfg["pages_url"]), "html", "utf-8"))
    if cfg.get("attach_report"):
        zp = _zip()
        if zp:
            part = MIMEApplication(open(zp, "rb").read(), Name="allure-report.zip")
            part["Content-Disposition"] = 'attachment; filename="allure-report.zip"'
            msg.attach(part)
    if m.get("ssl") or m["port"] == 465:
        sv = smtplib.SMTP_SSL(m["host"], m["port"], context=ssl.create_default_context())
    else:
        sv = smtplib.SMTP(m["host"], m["port"]); sv.starttls(context=ssl.create_default_context())
    sv.login(m["user"], pw); sv.sendmail(m["user"], rec, msg.as_string()); sv.quit()
    print(f"📧 已发送给 {len(rec)} 人: {rec}")
if __name__ == "__main__":
    send_report_mail()