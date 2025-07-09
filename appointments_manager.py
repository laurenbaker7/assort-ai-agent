import json
from typing import List, Dict, Optional
from pprint import pprint

APPOINTMENTS_FILE = "appointments.json"

def load_appointments() -> List[Dict]:
    """
    Loads all appointments from the appointments.json file.
    Returns a list of appointment dictionaries.
    """
    try:
        with open(APPOINTMENTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_appointments(appointments: List[Dict]) -> None:
    """
    Saves the provided list of appointments back to appointments.json.
    """
    with open(APPOINTMENTS_FILE, "w") as file:
        json.dump(appointments, file, indent=2)

def get_available_slots() -> List[Dict]:
    """
    Returns a list of unbooked appointment slots.
    """
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

"""if __name__ == "__main__":
    available = get_available_slots()
    print("Available slots before booking, (" + str(len(available)) + " slots):")
    pprint(available)

    # Test booking slot ID 1 with sample patient info
    booked = book_slot(1, {
        "name": "Test Patient",
        "dob": "01/01/1990",
        "phone": "555-555-5555"
    })
    print("\nBooked slot:")
    pprint(booked)

    available_after = get_available_slots()
    print("\nAvailable slots after booking, (" + str(len(available_after)) + " slots):")
    pprint(available_after)"""
