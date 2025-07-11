import json
from typing import List, Dict, Optional

APPOINTMENTS_FILE = "appointments.json"

def load_appointments() -> List[Dict]:
    # Loads all appts from the appointments.json file & returns a list of all appt dictionaries
    try:
        with open(APPOINTMENTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_appointments(appointments: List[Dict]) -> None:
    # Saves the provided list of appointments back to appointments.json.
    with open(APPOINTMENTS_FILE, "w") as file:
        json.dump(appointments, file, indent=2)

def get_available_slots() -> List[Dict]:
    # Returns a list of unbooked appointment slots.
    appointments = load_appointments()
    return [appt for appt in appointments if not appt.get("booked", False)]

def book_slot(slot_id: int, patient_info: Dict) -> Optional[Dict]:
    """
    Marks the appointment with the given slot_id as booked,
    attaches patient_info to it, saves the file,
    and returns the updated appointment dict if successful.
    Returns None if the slot was not found or already booked.
    """
    appointments = load_appointments()
    for appt in appointments:
        if appt.get("id") == slot_id:
            if appt.get("booked", False):
                return None
            appt["booked"] = True
            appt["patient_info"] = patient_info
            save_appointments(appointments)
            return appt
    return None

def get_last_word(s: str) -> str:
    return s.strip().split()[-1].lower() if s else ""

def get_best_appointments(city: str, referral: str) -> List[Dict]:
    """
    Returns up to 5 best appointment slots based on:
    - Referral doctor priority
    - Matching city
    """
    appointments = get_available_slots()
    requested_city = city.lower() if city else ""
    referral_doctor = get_last_word(referral)

    scored_slots = []

    for slot in appointments:
        if slot.get("booked"):
            continue

        score = 0
        slot_city = slot["location"].split(",")[0].strip().lower()
        doctor_last_name = get_last_word(slot["doctor"])

        has_referral = referral_doctor and (referral_doctor in doctor_last_name)
        if has_referral:
            score += 100  # Prioritize referral

        if requested_city and requested_city == slot_city:
            score += 1

        scored_slots.append((score, slot))

    best_slots = [slot for score, slot in sorted(scored_slots, key=lambda x: x[0], reverse=True) if score > 0][:5]

    return best_slots
