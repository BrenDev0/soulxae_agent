from pydantic import BaseModel

class UploadRequest(BaseModel):
    agent_id: str
    user_id: str
    s3_url: str
    file_type: str
    filename: str