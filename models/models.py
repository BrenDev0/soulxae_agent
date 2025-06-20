from pydantic import BaseModel, EmailStr
from typing import Optional, List

class InteractionRequest(BaseModel):
    agent_id: str;
    conversation_id: str

class LLMConfig(BaseModel):
    prompt: str;
    tools: List[any];
    max_tokens: int;
    temperature: float
