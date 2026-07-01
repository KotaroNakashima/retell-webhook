import os

import resend
from fastapi import FastAPI, Request
from twilio.rest import Client

app = FastAPI()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "kiimigu4@gmail.com")

resend.api_key = RESEND_API_KEY


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/vapi")
async def vapi_webhook(request: Request):
    data = await request.json()

    intent = data.get("intent", "unknown")
    summary = data.get("summary", "")

    caller_number = (
        data.get("caller_number")
        or data.get("customer", {}).get("number")
        or data.get("phoneNumber")
        or data.get("from")
    )

    name = data.get("name", "")
    party_size = data.get("party_size", "")
    reservation_date = data.get("reservation_date", "")
    reservation_time = data.get("reservation_time", "")
    allergies = data.get("allergies", "")
    special_request = data.get("special_request", "")

    sms_sid = None

    try:
        if intent == "reservation" and caller_number:
            sms_body = """Thank you for contacting Sakura Omakase NYC.

Your reservation request has been received.

Reserve or manage your booking here:
https://www.opentable.com/xxxx

We look forward to welcoming you."""

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

Guest Name:
{name}

Party Size:
{party_size}

Reservation Date:
{reservation_date}

Reservation Time:
{reservation_time}

Allergies:
{allergies}

Special Request:
{special_request}

Caller Number:
{caller_number}
"""

        resend.Emails.send({
            "from": "Sakura Omakase <onboarding@resend.dev>",
            "to": [OWNER_EMAIL],
            "subject": email_subject,
            "text": email_body,
        })

        return {
            "success": True,
            "message": "Reservation request submitted successfully.",
            "intent": intent,
            "sms_sent": bool(sms_sid),
            "sms_sid": sms_sid,
            "owner_notified": True,
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "success": False,
            "message": "Failed to submit reservation request.",
            "error": str(e),
        }
