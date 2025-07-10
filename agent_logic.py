from typing import Dict, Optional
import appointments_manager
import email_sender
from address_validator import validate_address

def collect_patient_info() -> Dict:
    # Collects patient intake information with address validation
    
    print("Collecting patient intake information...")
    
    name = input("Patient name: ")
    dob = input("Date of birth (MM/DD/YYYY): ")
    phone = input("Phone number: ")
    email = input("Email address (optional, press Enter to skip): ")
    
    # Address with validation loop
    while True:
        address = input("Address: ")
        validation_result = validate_address(address)
        if validation_result["valid"]:
            address = validation_result["formatted_address"]
            print(f"Address validated: {address}")
            break
        else:
            print(f"Invalid address: {validation_result['message']}. Please try again.")
    
    reason_for_visit = input("Reason for visit: ")
    insurance_payer = input("Insurance payer name: ")
    insurance_id = input("Insurance ID: ")
    referral = input("Referral physician name (optional, press Enter to skip): ")
    
    patient_info = {
        "name": name,
        "dob": dob,
        "phone": phone,
        "email": email,
        "address": address,
        "reason_for_visit": reason_for_visit,
        "insurance_payer": insurance_payer,
        "insurance_id": insurance_id,
        "referral": referral
    }
    
    return patient_info
    

def offer_and_book_appointment(patient_info: Dict) -> Optional[Dict]:
    # Offers available appointments, books selected appointment, sends confirmation email
    
    available_appts = appointments_manager.get_available_slots()
    if not available_appts:
        print("No available appointments at this time. Please try again later.")
        return None
    
    print(f"\nThere are {len(available_appts)} appointments available. Here is the information about each of those appointments:")
    for appt in available_appts:
        print(f"ID: {appt['id']}")
        print(f"Doctor: {appt['doctor']}")
        print(f"Time: {appt['time']}")
        print(f"Location: {appt['location']}")
        print("-" * 30)

    while True:
        try:
            selected_id = int(input("Please enter the ID of the appointment you would like to book: "))
            booked_appt = appointments_manager.book_slot(selected_id, patient_info)
            if booked_appt:
                print(f"\nAppointment booked successfully! Here is the information about your appointment:")
                print(f"Doctor: {booked_appt['doctor']}")
                print(f"Time: {booked_appt['time']}")
                print(f"Location: {booked_appt['location']}")
                email_sender.send_confirmation_email(patient_info, booked_appt)
                return booked_appt
            else:
                print("\nFailed to book appointment. Appointment ID not found or already booked. Please try again.")
        except ValueError:
            print("\nInvalid input. Please enter a valid appointment ID.")


"""if __name__ == "__main__":
    patient_info = collect_patient_info()
    offer_and_book_appointment(patient_info)"""