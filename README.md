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
- TTS/STT (e.g., ElevenLabs, AssemblyAI, Deepgram)
- JSON file for appointment tracking
- SMTP or Mailgun/SendGrid for email

---

## Setup

1. **Clone the repo:**
```bash
git clone https://github.com/your-username/assort-voice-agent.git
cd assort-voice-agent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Add enviornment variables** in a `.env` file for your API keys and email/Twilio credentials.

4. **Run locally:**
```bash
uvicorn main:app --reload
```

5. Use ngrok to expose your local server for Twilio during testing.


## Testing
- Call the Twilio number provided
- The agent will guide you through the intake process and confirm an appointment
- A confirmation email will be sent to the Assort team after the call