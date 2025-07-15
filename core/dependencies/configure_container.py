from sqlalchemy.orm import Session
from modules.embeddings.embedding_service import EmbeddingService
from core.services.redis_service import RedisService
from modules.prompts.prompt_service import PromptService
from core.services.webtoken_service import WebTokenService
from core.middleware.middleware_service import MiddlewareService
from modules.messaging.messaging_service import MessagingService
from core.dependencies.container import Container

def configure_container(db_session: Session):
    # core   
    redis_service = RedisService()
    Container.register("redis_service", redis_service)

    webtoken_service = WebTokenService()
    Container.register("webtoken_service", webtoken_service)

    middleware_service = MiddlewareService(
        webtoken_service=webtoken_service
    )
    Container.register("middleware_service", middleware_service)


    # embedding
    embedding_service = EmbeddingService()
    Container.register("embedding_service", embedding_service)

    # messaging
    messaging_service = MessagingService()
    Container.register("messaging_service", messaging_service)

    # prompt
    prompt_service = PromptService(
        embedding_service=embedding_service,
        redis_service=redis_service
    )
    Container.register("prompt_service", prompt_service)






    





