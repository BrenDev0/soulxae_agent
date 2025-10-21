from uuid import UUID

from src.shared.domain.vector_repository import VectorRepository
from src.shared.domain.embedding_service import EmbeddingService

class UploadDocument():
    def __init__(
        self,
        vector_repository: VectorRepository,
        embedding_service: EmbeddingService,
    ):
        self.__vector_repository = vector_repository
        self.__embedding_service = embedding_service

    async def execute(
        self,
        content_type: str,
        filename: str,
        file_bytes: bytes,
        agent_id: UUID,
        user_id: UUID
    ):
        embedding_result = await self.__embedding_service.embed_document(
            file_bytes=file_bytes,
            filename=filename,
            agent_id=agent_id,
            user_id=user_id
        )

        namespace = f"user_{user_id}_agent_{agent_id}"
        
        result = self.__vector_repository.store_embeddings(
            embeddings=embedding_result.embeddings,
            chunks=embedding_result.chunks,
            namespace=namespace,
            # Additional metadata
            filename=filename,

            agent_id=str(agent_id),
            user_id=str(user_id),
            file_type=content_type
        )
        
        print(f"Stored {len(embedding_result.chunks)} chunks in Qdrant")
        print(f"Result: {result}")

        return result