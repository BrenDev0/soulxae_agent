from pydantic import BaseModel

class UploadRequest(BaseModel):
    agent_id: str
    user_id: str
    s3_url: str
    filename: str