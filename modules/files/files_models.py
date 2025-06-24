from pydantic import BaseModel
from typing import List, Any

class UploadRequest(BaseModel):
    agent_id: str;
    s3_url: str;
    file_type: str;
    filename: str;