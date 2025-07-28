from sqlalchemy.orm import Session
from src.modules.embeddings.embedding_service import EmbeddingService
from src.core.services.redis_service import RedisService
from src.modules.prompts.prompt_service import PromptService
from src.core.services.webtoken_service import WebTokenService
from src.core.middleware.middleware_service import MiddlewareService
from src.modules.messaging.messaging_service import MessagingService
from src.core.dependencies.container import Container

def configure_container(db_session: Session):
    # core   
    embedding_service = EmbeddingService()
    Container.register("embedding_service", embedding_service)

    messaging_service = MessagingService()
    Container.register("messaging_service", messaging_service)

    redis_service = RedisService()
    Container.register("redis_service", redis_service)

    webtoken_service = WebTokenService()
    Container.register("webtoken_service", webtoken_service)


    middleware_service = MiddlewareService(
        webtoken_service=webtoken_service
    )
    Container.register("middleware_service", middleware_service)

    prompt_service = PromptService(
        embedding_service=embedding_service,
        redis_service=redis_service
    )
    Container.register("prompt_service", prompt_service)






    





