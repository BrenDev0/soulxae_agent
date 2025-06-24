from sqlalchemy.orm import Session
from modules.embeddings.embedding_service import EmbeddingService
from modules.agents.agent_service import AgentService
from core.services.redis_service import RedisService
from modules.prompts.prompt_service import PromptService
from modules.tools.tools_service import ToolsService
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

    # tools
    tools_service = ToolsService(
        session=db_session
    )
    Container.register("tools_service", tools_service)

    # messaging
    messaging_service = MessagingService()

    # prompt
    prompt_service = PromptService(
        session=db_session,
        redis_service=redis_service
    )
    Container.register("prompt_service", prompt_service)

    # agent
    agent_service = AgentService(
        session=db_session,
        embeddings_service=embedding_service,
        prompt_service=prompt_service,
        redis_service=redis_service,
        tools_service=tools_service,
        messaging_service=messaging_service
    )
    Container.register("agent_service", agent_service)




    





