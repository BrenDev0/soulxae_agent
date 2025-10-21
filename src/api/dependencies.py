from fastapi import Depends

from src.api.interface.middleware.middleware_service import MiddlewareService
from src.api.infrastructure.webtoken_service import WebTokenService
from src.api.application.use_cases.upload_document import UploadDocument
from  src.api.application.use_cases.store_web_content import StoreWebContent
from src.api.domain.session_repository import SessionRepository
from src.api.infrastructure.redis_session_repository import RedisSessionRepository
from src.shared.dependencies.dependencies import get_embedding_service, get_vector_repository, get_web_extraction_service

from src.api.interface.controllers.agent_controller import AgentController


def get_session_repository() -> SessionRepository:
    return RedisSessionRepository()

def get_web_token_service() -> WebTokenService:
    return WebTokenService()

def get_middleware_service(
    web_token_service: WebTokenService = Depends(get_web_token_service)
) -> MiddlewareService:
    return MiddlewareService(
        webtoken_service=web_token_service
    )

def get_agents_controller(
    session_repo: SessionRepository = Depends(get_session_repository)
) -> AgentController:
    return AgentController(
        session_repo=session_repo
    )

def get_upload_document_use_case(
        embedding_service = Depends(get_embedding_service),
        vector_repository = Depends(get_vector_repository)
):
    return UploadDocument(
        embedding_service=embedding_service,
        vector_repository=vector_repository
    )

def get_store_web_content_use_case(
        embedding_service = Depends(get_embedding_service),
        vector_repository = Depends(get_vector_repository),
        web_extraction_service = Depends(get_web_extraction_service)
):
    return StoreWebContent(
        embedding_service=embedding_service,
        vector_repository=vector_repository,
        web_extraction_service=web_extraction_service
    )