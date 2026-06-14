import requests
import re
import json
import smtplib
from email.mime.text import MIMEText
import os

URL = "https://reservationv5.frontdesksuite.com/us/us/ReserveTime/TimeSelection?pageId=0481fc5c-fd6f-4971-9213-1edbaae1660a&buttonId=3b944ef0-52fa-4b3c-99cd-3618b7693390&culture=da"

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

html = requests.get(URL, timeout=30).text

match = re.search(
    r"var reservationDates\s*=\s*(\{.*?\});",
    html,
    re.S
)

available = []

if match:

    data = json.loads(match.group(1))

    for date_key, locations in data.items():

        for location in locations:

            day = location.get("day", {})

            if day.get("isAnyTimePresent"):
                available.append(date_key)

if available:

    msg = MIMEText(
        "发现新的预约时间：\n\n"
        + "\n".join(available)
        + "\n\n"
        + URL
    )

    msg["Subject"] = "预约空位提醒"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(
            EMAIL_USER,
            EMAIL_PASSWORD
        )

        smtp.send_message(msg)
