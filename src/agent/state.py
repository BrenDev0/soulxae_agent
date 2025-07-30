from typing import Optional, List, Dict
from typing_extensions import TypedDict
from datetime import datetime

class AppointmentState(TypedDict):
    next_node: str
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
    chat_language: str
    chat_history: List[Dict]