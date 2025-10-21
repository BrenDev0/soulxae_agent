from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict
from datetime import datetime

class AppointmentState(TypedDict):
    next_node: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    appointment_datetime: Optional[datetime] = None

class State(TypedDict):
    system_message: str
    calendar_id: str
    max_tokens: int
    temperature: float
    input: str
    user_id: str
    agent_id: str
    conversation_id: str
    token: str
    appointments_state: AppointmentState
    response: Optional[str]
    intent: Optional[str] 
    chat_history: List[Dict[str, Any]]