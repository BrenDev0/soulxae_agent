from fastapi import APIRouter, Body, Request, Depends
from fastapi.responses import JSONResponse
from src.dependencies.container import Container
from src.agent.services.embedding_service import EmbeddingService
from src.api.modules.files.files_models import UploadRequest
from src.api.core.middleware.hmac_verification import verify_hmac
import asyncio

router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)


@router.post("/upload", response_class=JSONResponse)
async def upload_docs(
    data: UploadRequest = Body(...),
    _: None = Depends(verify_hmac)
):
    try:
        print("in route")
        user_id = data.user_id
        s3_url = data.s3_url
        filename = data.filename
        agent_id = data.agent_id

        embedding_service: EmbeddingService = Container.resolve("embedding_service") 
        asyncio.create_task(
            embedding_service.add_document,
            s3_url = s3_url,
            filename=filename,
            user_id=user_id,
            agent_id=agent_id
        )
    except Exception as e:
        print(e)
    
    return JSONResponse(status_code=202, content={"message": "Request received"});