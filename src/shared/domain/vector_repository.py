from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from src.workflows.domain.entities import DocumentChunk, SearchResult

class DeleteFilter(BaseModel):
    filename: Optional[str] = None
    user_id: Optional[str] = None  
    company_id: Optional[str] = None
    document_id: Optional[str] = None

class VectorRepository(ABC):
    @abstractmethod
    async def similarity_search(
        self, 
        query_vector: List[float], 
        top_k: int = 4,
        namespace: Optional[str] = None
    ) -> List[SearchResult]:
        raise NotImplementedError

    @abstractmethod
    def store_embeddings(
        self,
        embeddings: List[List[float]],
        chunks: List[DocumentChunk],
        namespace: str,
        **kwargs
    ):
        raise NotImplementedError
    
    @abstractmethod
    def delete_embeddings(
        self,
        namespace: str,
        **filters
    ):
        raise NotImplementedError
    
    @abstractmethod
    def delete_namespace(self, namespace: str) -> bool:
        """Delete entire collection/namespace"""
        raise NotImplementedError
    
    @abstractmethod
    def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete all data for a user across all namespaces"""
        raise NotImplementedError