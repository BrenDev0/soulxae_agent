from pydantic import BaseModel
from fastapi import UploadFile

class UploadRequest(BaseModel):
    agent_id: str
    user_id: str
    file: UploadFile