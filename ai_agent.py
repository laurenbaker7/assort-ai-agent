import json
import logging
from dataclasses import dataclass
from typing import Optional, Annotated

from dotenv import load_dotenv
from pydantic import Field

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import deepgram, openai, cartesia, silero, noise_cancellation
from appointments_manager import book_slot
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from helper_functions import get_ordinal
from datetime import datetime
from email_sender import send_confirmation_email
from address_validator import validate_address
from appointments_manager import get_best_appointments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("appointment-booking-agent")

load_dotenv()

@dataclass
class UserData:
    ctx: Optional[JobContext] = None
    name: Optional[str] = None
    dob: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    reason_for_visit: Optional[str] = None
    insurance_name: Optional[str] = None
    insurance_id: Optional[str] = None
    referral: Optional[str] = None
    appointment_id: Optional[str] = None
    confirmed: bool = False

RunContext_T = RunContext[UserData]

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=(
            "You are a clear, friendly voice assistant for Assort Health. "
            "Your task is to COLLECT ONLY the following patient information in this EXACT ORDER by explicitly calling the corresponding function for each step: "
            "1) Full Name (call `update_name`), "
            "2) Date of Birth (call `update_date_of_birth`), "
            "3) Phone Number (call `update_phone`), "
            "4) Email Address if any (call `update_email`), "
            "5) Home Address (call `update_address`), "
            "6) Reason for Visit (call `update_insurance_provider`), "
            "7) Insurance Provider (call `update_insurance_name`), "
            "8) Insurance ID Number (call `update_insurance_id`), "
            "9) Referral Physician if any (call `update_referral`), "
            "10) Appointment ID (call `update_appointment_id`). "
            "After receiving and confirming each, move to the next in the list. "
            "Do not skip or reorder. Do not ask for or collect any other information. "
            "After collecting the Appointment ID, thank the user and end the session. "
            "It is VERY IMPORTANT that when you receive the list of appointments from `update_referral`, you READ THEM OUT LOUD exactly as returned before asking the user to select the appointment ID. "
            "If the user says 'skip' or 'none' for optional fields like email or referral, proceed to the next required step without asking again. "
        ))

    async def on_enter(self):
        await self.session.say("Hello, thank you for calling Assort Health. I will help you book an appointment now. May I have your full name?")

    @function_tool()
    async def update_name(self, name: Annotated[str, Field(description="The caller's full name")], context: RunContext_T) -> str:
        context.userdata.name = name
        return f"Thanks {name}. Can I get your date of birth?"

    @function_tool()
    async def update_date_of_birth(self, dob: Annotated[str, Field(description="The caller's date of birth")], context: RunContext_T) -> str:
        context.userdata.dob = dob
        return "Thank you. Can I get your phone number?"

    @function_tool()
    async def update_phone(self, phone: Annotated[str, Field(description="The caller's phone number")], context: RunContext_T) -> str:
        context.userdata.phone = phone
        return "Thank you. Can you provide your email address? This is optional, so say None to skip."

    @function_tool()
    async def update_email(self, email: Annotated[str, Field(description="The caller's email address")], context: RunContext_T) -> str:
        context.userdata.email = email
        return "Thank you. Can you provide your home address?"

    @function_tool()
    async def update_address(self, address: Annotated[str, Field(description="The caller's address")], context: RunContext_T) -> str:
        address_validation_result = validate_address(address)
        if not address_validation_result["valid"]:
            return "Invalid address, please try again."
        context.userdata.address = address_validation_result["formatted_address"]
        return "Thank you. Can you briefly tell me the reason for your appointment?"

    @function_tool()
    async def update_insurance_provider(self, reason_for_visit: Annotated[str, Field(description="The reason for the appointments")], context: RunContext_T) -> str:
        context.userdata.reason_for_visit = reason_for_visit
        return "Thank you. Can you provide your insurance provider?"
    
    @function_tool()
    async def update_insurance_name(self, insurance_name: Annotated[str, Field(description="The name of the insurance provider")], context: RunContext_T) -> str:
        context.userdata.insurance_name = insurance_name
        return "Thank you. Can you provide your insurance ID number?"

    @function_tool()
    async def update_insurance_id(self, insurance_id: Annotated[str, Field(description="The caller's insurance id")], context: RunContext_T) -> str:
        context.userdata.insurance_id = insurance_id
        return "Thank you. Do you have a referral physician? If so, please say their name. If not, please say None"

    @function_tool()
    async def update_referral(self, referral: Annotated[str, Field(description="The referred doctor")], context: RunContext_T) -> str:
        context.userdata.referral = referral

        full_address = context.userdata.address or ""
        address_parts = [part.strip() for part in full_address.split(",")]

        city = ""
        if len(address_parts) >= 2:
            city = address_parts[1].lower()
        else:
            city = ""
        appointments = get_best_appointments(city, referral)

        if not appointments:
            return "I'm sorry, there are no available appointments right now. I will end the call now."

        slots = "Here are the best available appointments based on your referral doctor if provided and city of residence: "
        i = 0
        for appt in appointments:
            try:
                dt = datetime.strptime(appt['time'], '%Y-%m-%d %I:%M %p')
                day = get_ordinal(dt.day)
                spoken_time = dt.strftime(f'%B {day}, %Y at %I %p')  # e.g., 'July 7th, 2025 at 10 AM'
            except Exception:
                spoken_time = appt['time']  # fallback
            slots += f"Appointment ID {appt['id']} on {spoken_time} with {appt['doctor']}. "
            i += 1
            if i > 5:
                break
        slots += " Please tell me the ID of the appointment you would like to book."
        return slots

    @function_tool()
    async def update_appointment_id(self, appointment_id: Annotated[str, Field(description="The chosen appointment ID")], context: RunContext_T) -> str:
        context.userdata.appointment_id = appointment_id
        patient_info = {
            "name": context.userdata.name,
            "dob": context.userdata.dob,
            "email": context.userdata.email,
            "address": context.userdata.address,
            "reason_for_visit": context.userdata.reason_for_visit,
            "insurance_payer": context.userdata.insurance_name,
            "insurance_id": context.userdata.insurance_id,
            "referral": context.userdata.referral
        }
        booked_appt = book_slot(int(appointment_id), patient_info)
        send_confirmation_email(patient_info, booked_appt)
        context.userdata.confirmed = booked_appt is not None
        print("User data printed:", context.userdata)
        return f"Thank you, I have noted your appointment ID as {appointment_id}. I will now end the call and book your appointment. Goodbye."


async def entrypoint(ctx: JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    session.userdata = UserData(ctx=ctx)

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))