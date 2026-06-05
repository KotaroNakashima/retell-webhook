import os
import smtplib
from email.mime.text import MIMEText

from fastapi import FastAPI, Request
from twilio.rest import Client

app = FastAPI()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "kiimigu4@gmail.com")


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/vapi")
async def vapi_webhook(request: Request):
    data = await request.json()

    intent = data.get("intent", "unknown")
    summary = data.get("summary", "")
    caller_number = data.get("caller_number")

    if not caller_number:
        return {
            "success": False,
            "error": "Missing caller_number",
            "received": data,
        }

    sms_body = """Thank you for contacting Sakura Omakase NYC.

Reserve your table here:
https://www.opentable.com/xxxx

We look forward to welcoming you."""

    try:
        sms_sid = None

        if intent == "reservation":
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            sms = client.messages.create(
                body=sms_body,
                from_=TWILIO_PHONE_NUMBER,
                to=caller_number,
            )
            sms_sid = sms.sid

        email_subject = f"Sakura Omakase NYC Inquiry: {intent}"

        email_body = f"""
New guest request received.

Intent:
{intent}

Summary:
{summary}

Caller Number:
{caller_number}
"""

        msg = MIMEText(email_body)
        msg["Subject"] = email_subject
        msg["From"] = GMAIL_USER
        msg["To"] = OWNER_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return {
            "success": True,
            "intent": intent,
            "sms_sent": intent == "reservation",
            "sms_sid": sms_sid,
            "owner_notified": True,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
