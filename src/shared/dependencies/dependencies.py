from fastapi import Depends
import os

from src.shared.domain.embedding_service import EmbeddingService
from src.shared.domain.vector_repository import VectorRepository

from src.shared.infrastructure.qdrant_vector_repository import get_qdrant_client, QdrantVectorStore
from src.shared.infrastructure.openai_embedding_service import OpenAIEmbeddingService


def get_embedding_service() -> EmbeddingService:
    return OpenAIEmbeddingService(api_key=os.getenev("OPENAI_API_KEY"))


def get_vector_repository(
        client = Depends(get_qdrant_client)
) -> VectorRepository:
   return QdrantVectorStore(
       client=client
   )