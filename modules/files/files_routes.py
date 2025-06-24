from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from core.dependencies.container import Container
from modules.embeddings.embedding_service import EmbeddingService
from modules.files.files_models import UploadRequest

router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)


@router.post("/upload", response_class=JSONResponse)
async def upload_docs(
    request: Request,
    data: UploadRequest = Body(...)
):
    try:
        user_id = request.state.user_id
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