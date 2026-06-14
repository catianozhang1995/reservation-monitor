import smtplib
from email.mime.text import MIMEText

send_test = True

if send_test:
    print("Starting email test...")

    msg = MIMEText(
        "这是一封测试邮件。\n\n"
        "如果你收到这封邮件，说明 GitHub Actions 和 Gmail 配置正常。"
    )

    msg["Subject"] = "预约监控测试"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.set_debuglevel(1)  # 可选调试
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("Test email sent")
    exit()
