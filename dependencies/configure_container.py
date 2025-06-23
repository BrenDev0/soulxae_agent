from sqlalchemy.orm import Session
from services.embedding_service import EmbeddingService
from services.agent_service import AgentService
from services.redis_service import RedisService
from services.prompt_service import PromptService
from services.tools_service import ToolsService
from services.webtoken_service import WebTokenService
from middleware.middleware_service import MiddlewareService
from dependencies.container import Container

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
        tools_service=tools_service
    )
    Container.register("agent_service", agent_service)




    





