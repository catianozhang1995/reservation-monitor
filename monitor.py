from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

URL = "https://reservationv5.frontdesksuite.com/us/us/ReserveTime/TimeSelection?pageId=0481fc5c-fd6f-4971-9213-1edbaae1660a&buttonId=3b944ef0-52fa-4b3c-99cd-3618b7693390&culture=da"

print("=" * 50)
print(f"Started: {datetime.utcnow()} UTC")
print("Opening reservation page...")

available = []

with sync_playwright() as p:
browser = p.chromium.launch(headless=True)

page = browser.new_page()

page.goto(
    URL,
    wait_until="networkidle",
    timeout=60000
)

print("Page loaded")

page.wait_for_timeout(5000)

page.screenshot(path="debug.png", full_page=True)

elements = page.query_selector_all("button, div, span")

print(f"Found {len(elements)} elements")

for el in elements:
    try:
        text = (el.inner_text() or "").strip()
        aria = el.get_attribute("aria-label") or ""

        combined = f"{text} {aria}".lower()

        if (
            "ledig" in combined
            or "available" in combined
            or "appointment" in combined
        ):
            available.append(text or aria)

    except Exception:
        pass

browser.close()

print(f"Matches found: {len(available)}")

for slot in available:
print(f"  -> {slot}")

if available:
print("Appointment found. Sending email...")

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

print("Email sent successfully")

else:
print("No appointment available")

print("Finished")
print("=" * 50)
