from fastapi import Depends
import os

from src.shared.domain.embedding_service import EmbeddingService
from src.shared.domain.vector_repository import VectorRepository
from  src.shared.domain.web_extraction_service import  WebExtractionService

from src.shared.infrastructure.qdrant_vector_repository import get_qdrant_client, QdrantVectorStore
from src.shared.infrastructure.openai_embedding_service import OpenAIEmbeddingService
from src.shared.infrastructure.tavily_web_extraction_service import  get_tavily_client, TavilyWebExtractionService


def get_embedding_service() -> EmbeddingService:
    return OpenAIEmbeddingService(api_key=os.getenv("OPENAI_API_KEY"))


def get_vector_repository(
        client = Depends(get_qdrant_client)
) -> VectorRepository:
   return QdrantVectorStore(
       client=client
   )

def get_web_extraction_service(
    client = Depends(get_tavily_client)
) -> WebExtractionService:
    return TavilyWebExtractionService(client=client)