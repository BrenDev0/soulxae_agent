from fastapi import APIRouter, File, UploadFile, Depends, Form, Request
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
    agent_id: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        user_id = request.state.user_id
        file_type = file.content_type
        filename =  file.filename
        file_obj = BytesIO(await file.read())


        embedding_service: EmbeddingService = Container.resolve("embedding_service") 
        status = await embedding_service.embed_uploaded_document(
            file_data=file_obj,
            file_type=file_type,
            filename=filename,
            agent_id=agent_id,
            user_id=user_id
        )

        print(status)

        return JSONResponse(status_code=200, content={"message": "success"});

    except Exception as e:
        print(e)