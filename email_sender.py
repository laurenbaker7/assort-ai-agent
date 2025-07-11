import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Load email environment variables
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

ASSORT_EMAILS = ["laurenbaker@berkeley.edu"]

def send_confirmation_email(patient_info: Dict, appointment_info: Dict) -> None:
    # Sends a confirmation email to the Assort team with patient and appointment details.

    subject = f"New Appointment Booking: {appointment_info.get('doctor')} on {appointment_info.get('time')}"
    sender_email = EMAIL_HOST_USER
    recipients = ASSORT_EMAILS
    
    # HTML body with bolded headings and clear formatting
    html_body = f"""
    <html>
    <body>
    <p><strong>A new appointment has been booked.</strong></p>

    <p><strong>Patient Information:</strong><br>
    Name: {patient_info.get('name')}<br>
    Date of Birth: {patient_info.get('dob')}<br>
    Phone: {patient_info.get('phone')}<br>
    Email: {patient_info.get('email') or 'N/A'}<br>
    Address: {patient_info.get('address') or 'N/A'}<br>
    Reason for Visit: {patient_info.get('reason_for_visit') or 'N/A'}
    </p>

    <p><strong>Appointment Details:</strong><br>
    Doctor: {appointment_info.get('doctor')}<br>
    Date & Time: {appointment_info.get('time')}<br>
    Location: {appointment_info.get('location')}
    </p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))
    
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(sender_email, recipients, msg.as_string())
        print("Confirmation email sent successfully.")
    except Exception as e:
        print("Failed to send confirmation email:", e)