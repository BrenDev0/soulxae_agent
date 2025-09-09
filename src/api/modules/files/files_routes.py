from fastapi import APIRouter, Body, Request, Depends
from fastapi.responses import JSONResponse
from src.dependencies.container import Container
from src.agent.services.embedding_service import EmbeddingService
from src.api.modules.files.files_models import UploadRequest
from src.api.core.middleware.hmac_verification import verify_hmac

router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)


@router.post("/upload", response_class=JSONResponse)
async def upload_docs(
    request: Request,
    data: UploadRequest = Body(...),
    _: None = Depends(verify_hmac)
):
    try:
        user_id = data.user_id
        s3_url = data.s3_url
        file_type = data.file_type
        filename = data.filename
        agent_id = data.agent_id


        embedding_service: EmbeddingService = Container.resolve("embedding_service") 
        status = await embedding_service.embed_uploaded_document(
            s3_url = s3_url,
            file_type=file_type,
            filename=filename,
            user_id=user_id,
            agent_id=agent_id,
        )

        print(status)

        return JSONResponse(status_code=200, content={"message": "Document added to vector store"});

    except Exception as e:
        print(e)