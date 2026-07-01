import os
import traceback

import resend
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "kiimigu4@gmail.com")

resend.api_key = RESEND_API_KEY


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/retell")
async def retell_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    print("RETELL DATA:", data)

    # Retellの実際のJSON構造がまだ未確定なので、複数パターンに対応
    extracted_data = (
        data.get("call_analysis", {}).get("custom_analysis_data")
        or data.get("call", {}).get("call_analysis", {}).get("custom_analysis_data")
        or data.get("custom_analysis_data")
        or data.get("post_call_data")
        or {}
    )

    customer_name = (
        extracted_data.get("customer_name")
        or data.get("customer_name")
        or ""
    )

    reservation_date = (
        extracted_data.get("reservation_date")
        or data.get("reservation_date")
        or ""
    )

    reservation_time = (
        extracted_data.get("reservation_time")
        or data.get("reservation_time")
        or ""
    )

    party_size = (
        extracted_data.get("party_size")
        or data.get("party_size")
        or ""
    )

    call_summary = (
        extracted_data.get("call_summary")
        or data.get("call_summary")
        or data.get("summary")
        or ""
    )

    caller_number = (
        data.get("from_number")
        or data.get("caller_number")
        or data.get("call", {}).get("from_number")
        or data.get("call", {}).get("from")
        or ""
    )

    email_status = "not_sent"
    errors = []

    try:
        resend.Emails.send({
            "from": "Sakura Omakase <onboarding@resend.dev>",
            "to": [OWNER_EMAIL],
            "subject": "Sakura Omakase NYC - Reservation Request",
            "text": f"""
New reservation request

Name: {customer_name}
Party Size: {party_size}
Date: {reservation_date}
Time: {reservation_time}
Phone: {caller_number}

Call Summary:
{call_summary}
""",
        })

        email_status = "sent"
        print("EMAIL STATUS: sent")

    except Exception as e:
        email_status = "failed"
        errors.append(f"Email error: {str(e)}")
        print("EMAIL ERROR:", str(e))
        traceback.print_exc()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "status": "received",
            "message": "Retell webhook received successfully.",
            "email_status": email_status,
            "errors": errors,
        },
    )
