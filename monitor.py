import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

URL = "https://reservationv5.frontdesksuite.com/us/us/ReserveTime/TimeSelection?pageId=0481fc5c-fd6f-4971-9213-1edbaae1660a&buttonId=3b944ef0-52fa-4b3c-99cd-3618b7693390&culture=da"

available = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(URL, wait_until="networkidle", timeout=60000)

    # 等页面 JS 渲染完成（关键）
    page.wait_for_timeout(5000)

    # 尝试从页面中找可用日期按钮（需要根据实际 DOM）
    # 这里做“通用检测”：找所有可点击日期元素
    elements = page.query_selector_all("button, div, span")

    for el in elements:
        text = el.inner_text().strip() if el.inner_text() else ""
        aria = el.get_attribute("aria-label") or ""

        # 简单规则：包含日期 + 可用标记
        if ("available" in aria.lower()) or ("ledig" in text.lower()):
            available.append(text or aria)

    browser.close()

print("Available slots:", available)

if available:
    msg = MIMEText(
        "发现预约空位：\n\n"
        + "\n".join(available)
        + "\n\n"
        + URL
    )

    msg["Subject"] = "预约空位提醒"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("Email sent")
