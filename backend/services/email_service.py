import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_welcome_email(to_email: str):
    subject = "Welcome to TruthShield AI 🚀"

    body = f"""
Hi, {to_email.split('@')[0]}!

You have successfully registered in TruthShield AI 🧠

Now you can:
- Detect fake news
- Analyze claims
- Use AI-powered fact checking

Thank you for joining!

— TruthShield Team
""".format(to_email)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully")
    except Exception as e:
        print("❌ Email failed:", e)