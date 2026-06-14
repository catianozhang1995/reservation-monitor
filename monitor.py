from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

BASE_URL = "https://reservationv5.frontdesksuite.com/us/us/Home/Index?pageId=6326ea69-cea3-4179-a81c-5ebb22bbdb00&culture=en&uiculture=en"

print("=" * 60)
print(f"Started: {datetime.utcnow()} UTC")

results = []

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

    page.get_by_text("Næstved").click()
    page.wait_for_timeout(2000)

    page.get_by_text("1 person").click()
    page.wait_for_timeout(5000)

    print("Calendar loaded")

    # 找所有日期按钮（通常是数字）
    day_buttons = page.query_selector_all("button")

    print(f"Found {len(day_buttons)} day buttons")

    # 逐个点击日期
    for i, btn in enumerate(day_buttons):
        try:
            text = (btn.inner_text() or "").strip()

            # 只处理数字日期（过滤图例/按钮）
            if not text.isdigit():
                continue

            print(f"Checking day: {text}")

            btn.click()
            page.wait_for_timeout(1500)

            # 检查是否出现 slot（关键）
            slots = page.query_selector_all(
                ".slot, button.available, div.available, [class*='slot'], [class*='available']"
            )

            if len(slots) > 0:
                print(f"FOUND SLOT on day {text}")
                results.append(text)

        except Exception as e:
            print(f"Error on day {text if 'text' in locals() else i}: {e}")
            continue

    browser.close()

print("=" * 60)
print(f"Total available days: {len(results)}")

for r in results:
    print(" ->", r)

# 发送邮件（只有真正有结果才发）
if results:
    print("Sending email...")

    msg = MIMEText(
        "发现可预约日期（未来23天）：\n\n"
        + "\n".join(results)
        + "\n\n"
        + BASE_URL
    )

    msg["Subject"] = "预约系统：发现可用slot"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("Email sent")

else:
    print("No slots found")

print("Finished")
print("=" * 60)
