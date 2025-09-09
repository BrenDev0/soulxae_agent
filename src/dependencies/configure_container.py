from sqlalchemy.orm import Session
from src.agent.services.embedding_service import EmbeddingService
from src.api.core.services.redis_service import RedisService
from src.agent.services.prompt_service import PromptService
from src.api.core.services.webtoken_service import WebTokenService
from src.api.core.middleware.middleware_service import MiddlewareService
from src.api.modules.messaging.messaging_service import MessagingService
from src.dependencies.container import Container
from src.api.modules.agents.agent_controller import AgentController
from src.agent.services.appointments_service import AppoinmentsService
from qdrant_client import QdrantClient
import os

def configure_container():
    # core   
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    embedding_service = EmbeddingService(client=qdrant_client)
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

    appointments_service = AppoinmentsService(
        prompt_service=prompt_service
    )

    Container.register("appointments_service", appointments_service)
    
    
    # modules 

    agents_controller = AgentController()
    Container.register("agents_controller", agents_controller)





    





