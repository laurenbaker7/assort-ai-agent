from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
from address_validator import validate_address
from appointments_manager import get_available_slots, book_slot, get_best_appointments
from email_sender import send_confirmation_email
import os
import json

load_dotenv()

app = FastAPI()

@app.post("/webhook")
async def receive_intake(request: Request):
    data = await request.json()
    print("Webhook received data:\n", json.dumps(data, indent=2))

    # Check if this is the correct event containing patient data
    event_type = data.get("event")
    if event_type != "agent_job_completed":
        print(f"Ignoring event type: {event_type}")
        return JSONResponse(status_code=200, content={"status": "ignored", "event": event_type})

    try:
        # Extract patient info
        patient_info = {
            "name": data.get("name"),
            "dob": data.get("dob"),
            "phone": data.get("phone"),
            "email": data.get("email", ""),
            "address": data.get("address", ""),
            "reason_for_visit": data.get("reason_for_visit", ""),
            "insurance_payer": data.get("insurance_payer", ""),
            "insurance_id": data.get("insurance_id", ""),
            "referral": data.get("referral", "No referral provided")
        }

        # Validate address
        address_validation_result = validate_address(patient_info["address"])
        if not address_validation_result["valid"]:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Invalid address, cannot proceed."}
            )
        patient_info["address"] = address_validation_result["formatted_address"]

        # Book appointment (currently: first available slot)
        available_slots = get_available_slots()
        if not available_slots:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No available slots found."}
            )
        slot = available_slots[0]
        booked_appt = book_slot(slot["id"], patient_info)

        if not booked_appt:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Failed to book appointment."}
            )
        
        # Send confirmation email
        send_confirmation_email(patient_info, booked_appt)

        return {"status": "success", "appointment": booked_appt}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/get_best_appointments")
async def get_best_appointments(request: Request):
    data = await request.json()
    print("API received data:\n", json.dumps(data, indent=2))

    requested_city = data.get("city", "").lower()
    referral_doctor = data.get("referral", "").lower()

    best_slots = get_best_appointments(requested_city, referral_doctor)

    if not best_slots:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "No suitable appointments found based on your preferences."}
        )

    return {"status": "success", "best_appointments": best_slots}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))