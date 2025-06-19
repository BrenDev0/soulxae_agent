# dependencies/container.py
from sqlalchemy.orm import Session
from services.embedding_service import EmbeddingService
from services.agent_service import AgentService
from services.redis_service import RedisService
from services.prompt_service import PromptService

class Container:
    def __init__(self, db_session: Session):
        self.embedding_service = EmbeddingService()
        self.redis_service = RedisService()
        self.prompt_service = PromptService(
            session=db_session,
            redis_service=self.redis_service
        )
        self.agent_service = AgentService(
            embeddings_service=self.embedding_service,
            prompt_service=self.prompt_service,
        )
