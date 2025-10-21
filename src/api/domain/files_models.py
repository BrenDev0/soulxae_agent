from pydantic import BaseModel
from fastapi import UploadFile
from typing import List

class UploadRequest(BaseModel):
    agent_id: str
    user_id: str
    file: UploadFile

class StoreWebContentRequest(BaseModel):
    urls: List[str]
    agent_id: str
    user_id: str