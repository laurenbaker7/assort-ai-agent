# Assort Health Voice Agent

A simple AI voice agent that collects patient intake details over the phone, offers appointment times, and sends confirmation emails. Built using Python, Twilio, and a JSON file to track bookings.

---

## Features

- Collects patient name, DOB, insurance, referral, chief complaint, address (with validation), and contact info
- Offers fake providers and times for selection
- Tracks booked appointments so slots aren’t double-booked during testing
- Sends confirmation emails to the Assort team after the call

---

## Tech Stack

- Python
- Twilio (calls)
- LiveKit Agent
- TTS/STT (e.g., ElevenLabs, AssemblyAI, Deepgram)
- JSON file for appointment tracking
- SMTP or Mailgun/SendGrid for email

---

## Setup

1. **Clone the repo:**
```bash
git clone https://github.com/laurenbaker7/assort-ai-agent.git
cd assort-ai-agent
```

2. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

3. **Add enviornment variables** in a `.env` file for your API keys and email/Twilio credentials.

4. **Run locally:**
```bash
uvicorn agent:app --reload
```

5. Use ngrok to expose your local server for Twilio during testing.

---

## Testing
- Call the Twilio number provided
- The agent will guide you through the intake process and confirm an appointment
- A confirmation email will be sent to the Assort team after the call

---

## File structure
- **`agent.py`:**
    - Manages the step-by-step collection of:
        - Name, DOB, insurance, referral, complaint, address, contact
    - Uses LiveKit with TTS, LLM, and STT to complete the call
    - Calls `address_validator.py` when needed
    - Calls `appointments_manager.py` to offer/book slots
- **`appointments_manager.py`:**
    - Loads `appointments.json` on startup
    - Provides:
        - `get_available_slots()`
        - `book_slot(slot_id, patient_info)`
        - `save_appointments()`
        - `get_best_appointments(city, referral)`
- **`email_sender.py`:**
    - Sends a formatted confirmation email with:
        - Patient info
        - Appointment details
        - Fake doctor and time
- **`address_validator.py`:**
    - Calls an address validation API
    - Returns valid/invalid and prompts reprompt logic if invalid
- **`appointments.json`:**
    - Preloaded with fake appointment slots
    - Updated on booking to prevent double booking
- **`requirements.txt`:**
    - Contains packages:
        - `fastapi`, `uvicorn`
        - `twilio`
        - `requests`
        - `python-dotenv`
        - `pydantic` (optional for data validation)
- **`.env`:**
    - Holds sensitive keys:
        - Twilio SID/auth
        - Email credentials
        - API keys
        - Phone number for quick testing