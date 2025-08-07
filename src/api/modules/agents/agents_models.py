from pydantic import BaseModel

class InteractionRequest(BaseModel):
    conversation_id: str
