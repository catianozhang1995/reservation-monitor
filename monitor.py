from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

BASE_URL = "https://reservationv5.frontdesksuite.com/us/us/Home/Index?pageId=6326ea69-cea3-4179-a81c-5ebb22bbdb00&culture=en&uiculture=en"

print("=" * 60)
print(f"Started: {datetime.utcnow()} UTC")

results = []
max_days = 27

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 打开主页
    print("Opening home page...")
    page.goto(BASE_URL, wait_until="networkidle")
    page.wait_for_timeout(3000)

    # 按流程进入预约
    page.get_by_text("Biometrics for residence permit/residence card").click()
    page.wait_for_timeout(2000)

    page.get_by_text("Book appointment").click()
    page.wait_for_timeout(2000)

    page.get_by_text("Aarhus").click()
    page.wait_for_timeout(2000)

    page.get_by_text("1 person").click()
    page.wait_for_timeout(5000)

    page.screenshot(path="calendar.png", full_page=True)

    print("Calendar loaded")

    checked_days = 0

    while checked_days < max_days:

        print(f"Scanning month... checked so far: {checked_days}")

        day_buttons = page.query_selector_all("button")

        found_days_this_month = 0

        for btn in day_buttons:

            if checked_days >= max_days:
                break

            try:
                text = (btn.inner_text() or "").strip()

                # 只处理日期数字
                if not text.isdigit():
                    continue

                print(f"Clicking day: {text}")

                btn.click()
                page.wait_for_timeout(1500)

                # 检查 slot（核心判断）
                slots = page.query_selector_all(
                    ".slot, button.available, div.available, [class*='slot'], [class*='available']"
                )

                if len(slots) > 0:
                    print(f"FOUND SLOT on {text}")
                    results.append(text)

                checked_days += 1
                found_days_this_month += 1

            except Exception as e:
                continue

        # 如果这一月没找到任何“日期按钮”，说明可能需要翻月
        if found_days_this_month == 0:
            print("No more days in this month, switching month...")

            try:
                # 👉 常见 next month 按钮（可能需要你微调文本）
                next_btn = page.locator("button[aria-label*='Next'], text=>, text=Next month")
                next_btn.click()

                page.wait_for_timeout(3000)

            except Exception as e:
                print("Cannot find next month button, stopping.")
                break

    browser.close()

print("=" * 60)
print(f"Total available days: {len(results)}")

for r in results:
    print(" ->", r)

# 发送邮件（只有真正有结果才发）
if results:
    print("Sending email with screenshot...")

    msg = MIMEMultipart()
    msg["Subject"] = "预约系统：发现可用slot"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    # 邮件正文
    body = MIMEText(
        "发现可预约日期（跨月27天扫描）：\n\n"
        + "\n".join(results)
        + "\n\n"
        + BASE_URL
    )
    msg.attach(body)

    # 读取截图
    with open("calendar.png", "rb") as f:
        img = MIMEBase("application", "octet-stream")
        img.set_payload(f.read())

    encoders.encode_base64(img)
    img.add_header(
        "Content-Disposition",
        "attachment",
        filename="calendar.png"
    )

    msg.attach(img)

    # 发送邮件
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("Email sent with screenshot")

else:
    print("No slots found")

print("Finished")
print("=" * 60)
