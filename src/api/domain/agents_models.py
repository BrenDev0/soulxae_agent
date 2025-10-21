from pydantic import BaseModel
from typing import Optional, Union, List
from uuid import UUID
from src.workflows.domain.state import AppointmentState
from src.workflows.domain.entities import Message

class InteractionRequest(BaseModel):
    system_message: str
    calendar_id: Optional[str] = None
    max_tokens: int
    temperature: float
    conversation_id: Union[str, UUID]
    user_id: Union[str, UUID]
    agent_id: Union[str, UUID]
    token: str
    input: str
    chat_history: List[Message]
    appointments_state: AppointmentState
