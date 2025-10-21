from abc import ABC, abstractmethod
from typing import List
from src.workflows.domain.entities import EmbeddingResult

class EmbeddingService(ABC):
    @abstractmethod
    async def embed_document(
        self,
        file_bytes: bytes,
        filename: str,
        **kwargs
    ) -> EmbeddingResult:
        raise NotImplementedError
    
    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        raise NotImplementedError
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        raise NotImplementedError