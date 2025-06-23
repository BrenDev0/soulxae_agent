from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from dependencies.container import Container
from middleware.middleware_service import MiddlewareService
from services.embedding_service import EmbeddingService
from io import BytesIO

router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)


@router.post("/upload", response_class=JSONResponse)
async def upload_docs(
    request: Request,
    agent_id: str = Body(...),
    s3_key: str = Body(...),
    file_type: str = Body(...),
    filename: str = Body(...)
):
    try:
        user_id = request.state.user_id
        s3_key = s3_key
        file_type = file_type
        filename = filename
        agent_id = agent_id


        embedding_service: EmbeddingService = Container.resolve("embedding_service") 
        status = await embedding_service.embed_uploaded_document(
            s3_key=s3_key,
            file_type=file_type,
            filename=filename,
            user_id=user_id,
            agent_id=agent_id,
        )

        print(status)

        return JSONResponse(status_code=200, content={"message": "Document added to vector store"});

    except Exception as e:
        print(e)