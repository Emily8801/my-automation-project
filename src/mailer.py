"""结果邮件：解析 Allure 结果 → 拼 HTML → SMTP 发送

配置来源：config.yaml 的 mail 段；授权码从环境变量 SMTP_AUTH_CODE 读取。
"""
import os
import smtplib
from email.mime.text import MIMEText

from src.llm import load_config


def send_report(subject: str, html_body: str) -> None:
    """发送 HTML 格式的结果邮件（收件人取 mail.recipients.always）"""
    mail_cfg = load_config()["mail"]
    if not mail_cfg.get("enabled"):
        return

    auth_code = os.getenv("SMTP_AUTH_CODE")
    if not auth_code:
        raise RuntimeError("未设置环境变量 SMTP_AUTH_CODE（SMTP 授权码，非登录密码）")

    smtp_cfg = mail_cfg["smtp"]
    recipients = mail_cfg["recipients"]["always"]

    msg = MIMEText(html_body, "html", "utf-8")
    msg["From"] = smtp_cfg["user"]
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    with smtplib.SMTP_SSL(smtp_cfg["host"], smtp_cfg["port"]) as server:
        server.login(smtp_cfg["user"], auth_code)
        server.sendmail(smtp_cfg["user"], recipients, msg.as_string())


def build_html_from_allure(allure_results_dir: str) -> str:
    """解析 reports/allure-results 下的 json，拼出通过率统计 HTML

    TODO: 遍历 *-result.json，统计 passed/failed/broken，按模板拼 HTML 表格。
    """
    raise NotImplementedError
