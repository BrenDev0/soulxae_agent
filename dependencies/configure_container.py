from sqlalchemy.orm import Session
from services.embedding_service import EmbeddingService
from services.agent_service import AgentService
from services.redis_service import RedisService
from services.prompt_service import PromptService
from services.tools_service import ToolsService
from dependencies.container import Container

def configure_container(db_session: Session):
    embedding_service = EmbeddingService()
    Container.register("embedding_service", embedding_service)

    tools_service = ToolsService(
        session=db_session,
        embedding_service=embedding_service
    )
    Container.register("tools_service", tools_service)

    redis_service = RedisService()
    Container.register("redis_service", redis_service)

    prompt_service = PromptService(
        session=db_session,
        redis_service=redis_service
    )
    Container.register("prompt_service", prompt_service)

    agent_service = AgentService(
        session=db_session,
        embeddings_service=embedding_service,
        prompt_service=prompt_service,
        redis_service=redis_service,
        tools_service=tools_service
    )
    Container.register("agent_service", agent_service)

    





