from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

class InteractionRequest(BaseModel):
    agent_id: str;
    conversation_id: str;
    input: str

class LLMConfig(BaseModel):
    prompt: str;
    tools: List[Any];
    max_tokens: int;
    temperature: float

class AppointmentPayload(BaseModel): 
    token: str;
    name: str;
    email: str;
    phone: str;
    start_time: datetime

