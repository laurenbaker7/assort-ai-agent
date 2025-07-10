from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=(
            "You are a clear, friendly voice assistant for Assort Health. "
            "Your job is to collect patient intake information by speaking with the caller step-by-step. "
            "First, greet the user warmly and immediately ask for their full name. "
            "Then, ask for their date of birth, phone number, email (optional), home address, reason for visit, insurance payer, insurance ID, and referral physician if they have one. "
            "Ask questions one by one, wait for clear responses, and confirm the information before moving to the next."
            "Do not repeat all of the information collected at the end of the call."
            "After you have collected all patient information, say ‘Thank you, I will now end the call to book your appointment,’ then stop speaking and end the session."
        ))

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt = deepgram.STT(model="nova-3", language="multi"),
        llm = openai.LLM(model="gpt-4o-mini"),
        tts = cartesia.TTS(model="sonic-2", voice="6f84f4b8-58a2-430c-8c79-688dad597532"),
        vad = silero.VAD.load(),
        turn_detection = MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="Hello! Welcome to Assort Health. Could you please tell me your full name to get started?"
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))