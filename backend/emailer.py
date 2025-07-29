import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")       # e.g., your Gmail
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") # e.g., Gmail App Password (not regular pwd)

def send_confirmation_email(receiver_email, permit_count):
    try:
        subject = "✅ NYC Permit Dashboard - Data Ready"
        body = f"""
        Hi,

        Your request was processed successfully.

          {permit_count} permits were inserted into the dashboard.

        You can now log in to view your data at:
        👉 https://your-dashboard-url.streamlit.app

        Regards,  
        NYC Permit Dashboard Team
        """

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"📧 Confirmation sent to {receiver_email}")
    except Exception as e:
        print(f"⚠️ Email error: {e}")

