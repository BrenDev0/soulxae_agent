from typing import Annotated, Optional
from typing_extensions import TypedDict
from datetime import datetime

class AppointmentState(TypedDict):
    name: str
    email: str
    phone: str
    appointment_datetime: datetime

class State(TypedDict):
    system_message: str
    input: str
    conversation_id: str
    token: str
    agent_id: str
    user_id: str
    appointments_state: AppointmentState
    response: Optional[str]
    intent: Optional[str] 
    chat_history: list[dict]