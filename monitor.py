from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

BASE_URL = "https://reservationv5.frontdesksuite.com/us/us/Home/Index?pageId=6326ea69-cea3-4179-a81c-5ebb22bbdb00&culture=en&uiculture=en"

print("=" * 50)
print(f"Started: {datetime.utcnow()} UTC")

available = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Opening home page...")
    page.goto(BASE_URL, wait_until="networkidle")

    page.wait_for_timeout(3000)

    # 1. Biometrics
    page.get_by_text("Biometrics for residence permit/residence card").click()
    print("Clicked Biometrics")

    page.wait_for_timeout(2000)

    # 2. Book appointment
    page.get_by_text("Book appointment").click()
    print("Clicked Book appointment")

    page.wait_for_timeout(2000)

    # 3. Næstved
    page.get_by_text("Næstved").click()
    print("Clicked Næstved")

    page.wait_for_timeout(2000)

    # 4. 1 person
    page.get_by_text("1 person").click()
    print("Clicked 1 person")

    page.wait_for_timeout(5000)

    page.screenshot(path="calendar.png", full_page=True)

    print("Calendar loaded")

    # 5. 找绿色日期（关键逻辑）
    # 通常绿色会在 class 或 style 里体现
    elements = page.query_selector_all("button, div, span")

    for el in elements:
        try:
            text = (el.inner_text() or "").strip()
            cls = (el.get_attribute("class") or "").lower()
            style = (el.get_attribute("style") or "").lower()

            combined = f"{text} {cls} {style}".lower()

            # 绿色通常代表可点击
            if (
                "green" in combined
                or "available" in combined
                or "ledig" in combined
            ):
                if text:
                    available.append(text)

        except:
            pass

    browser.close()

print(f"Found {len(available)} available items")

for a in available:
    print(" ->", a)

if available:
    print("Sending email...")

    msg = MIMEText(
        "发现可预约日期：\n\n"
        + "\n".join(available)
        + "\n\n"
        + BASE_URL
    )

    msg["Subject"] = "预约空位提醒"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("Email sent")

else:
    print("No availability found")

print("Finished")
print("=" * 50)
