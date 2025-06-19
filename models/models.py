from pydantic import BaseModel, EmailStr
from typing import Optional

class InteractionRequest(BaseModel):
    agent_id: str;
    conversation_id: str
