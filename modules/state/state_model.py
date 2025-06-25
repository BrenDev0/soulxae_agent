from pydantic import BaseModel
from datetime import datetime

class ConversationState(BaseModel):
    conversation_id: str;
    token: str;

class AppoinmentsState(BaseModel):
    name: str;
    email: str;
    phone: str;
    appointment_datetime: datetime;
