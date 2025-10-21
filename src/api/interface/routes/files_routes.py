from fastapi import APIRouter, Body,  Depends, Depends
from fastapi.responses import JSONResponse
from src.api.application.use_cases.upload_document import UploadDocument
from src.api.dependencies import get_upload_document_use_case
from src.api.domain.files_models import UploadRequest
from src.api.interface.middleware.hmac_verification import verify_hmac
import asyncio

router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)


@router.post("/upload", response_class=JSONResponse)
async def upload_docs(
    data: UploadRequest = Body(...),
    _: None = Depends(verify_hmac),
    upload_doc_use_case: UploadDocument = Depends(get_upload_document_use_case)
):
    try:
        user_id = data.user_id
        file = data.file
        agent_id = data.agent_id
        bytes = await file.read()

        
        asyncio.create_task(
            upload_doc_use_case.execute(
                content_type=file.content_type,
                file_bytes=bytes,
                filename=file.filename,
                user_id=user_id,
                agent_id=agent_id
            )
        )
    except Exception as e:
        print(e)
    
    return JSONResponse(status_code=202, content={"message": "Request received"});