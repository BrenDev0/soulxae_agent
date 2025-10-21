from uuid import UUID
from typing import List

from src.shared.domain.vector_repository import VectorRepository
from src.shared.domain.embedding_service import EmbeddingService
from src.shared.domain.web_extraction_service import WebExtractionService

class StoreWebContent():
    def __init__(
        self,
        vector_repository: VectorRepository,
        embedding_service: EmbeddingService,
        web_extraction_service: WebExtractionService
    ):
        self.__vector_repository = vector_repository
        self.__embedding_service = embedding_service
        self.__web_extraction_service = web_extraction_service

    async def execute(
        self,
        urls: List[str],
        agent_id: UUID,
        user_id: UUID
    ):
        extraction_results = self.__web_extraction_service.extract_webpage_content(urls=urls)
        namespace = f"user_{user_id}_agent_{agent_id}"
        text = ""
        for content in extraction_results["results"]:
            text += content["raw_content"]

            embedding_result = self.__embedding_service.embed_query(text)

            result = self.__vector_repository.store_embeddings(
                embeddings=embedding_result.embeddings,
                chunks=embedding_result.chunks,
                namespace=namespace,
                # Additional metadata
                filename=content["url"],
                agent_id=str(agent_id),
                user_id=str(user_id)
            )

            