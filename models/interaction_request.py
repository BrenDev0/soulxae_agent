from pydantic import BaseModel, EmailStr
from typing import Optional

class InteractionRequest(BaseModel):
    system_prompt: str;
    max_tokens: str;
