import os
import traceback

import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/vapi")
async def vapi_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    print("VAPI DATA:", data)

    errors = []
    n8n_status = "not_sent"

    if N8N_WEBHOOK_URL:
        try:
            response = requests.post(
                N8N_WEBHOOK_URL,
                json=data,
                timeout=10,
            )
            n8n_status = "sent"
            print("N8N STATUS:", response.status_code)

        except Exception as e:
            n8n_status = "failed"
            errors.append(f"n8n error: {str(e)}")
            print("N8N ERROR:", str(e))
            traceback.print_exc()
    else:
        errors.append("N8N_WEBHOOK_URL is not set")

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "status": "submitted",
            "n8n_status": n8n_status,
            "errors": errors,
            "message": (
                "Reservation request submitted successfully. "
                "Tell the caller: Perfect. Your reservation request has been submitted. "
                "Our team will contact you if needed. We look forward to welcoming you."
            ),
        },
    )
