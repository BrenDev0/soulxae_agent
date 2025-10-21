from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, Filter, FieldCondition, 
    MatchValue, PointStruct, FilterSelector
)

from typing import List, Dict, Any, Optional
import uuid
import os
from qdrant_client.http.exceptions import UnexpectedResponse

from src.shared.domain.vector_repository import VectorRepository
from src.workflows.domain.entities import DocumentChunk, SearchResult
from src.shared.utils.decorators.service_error_handler import service_error_handler


def get_qdrant_client():
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

class QdrantVectorStore(VectorRepository):
    __MODULE = "qdrant.vector_store"
    
    def __init__(self, client: QdrantClient):
        self._client = client
    


    async def similarity_search(
        self, 
        namespace: str,
        query_vector: List[float], 
        top_k: int = 4
    ) -> List[SearchResult]:
        results = self._client.search(
            collection_name=namespace,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )
        
        return [
            SearchResult(
                id=point.id,
                score=point.score,
                payload=point.payload,
                text=point.payload.get("text"),
                metadata=point.payload.get("metadata", {}) 
            )
            for point in results
        ]


    @service_error_handler(__MODULE)
    def store_embeddings(
        self,
        embeddings: List[List[float]],
        chunks: List[DocumentChunk],
        namespace: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Store embeddings in Qdrant"""
        self._ensure_collection_exists(namespace, len(embeddings[0]))
        
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "content": chunk.content,
                    **chunk.metadata,
                    **kwargs  # Include filename, user_id, company_id, etc.
                }
            ))
        
        # Batch upsert
        batch_size = 50
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self._client.upsert(collection_name=namespace, points=batch)
        
        return {
            "status": "success",
            "chunks_processed": len(points),
            "namespace": namespace
        }
    
    @service_error_handler(__MODULE)
    def delete_embeddings(
        self,
        namespace: str,
        **filters
    ) -> Dict[str, Any]:
        """Delete embeddings with filters"""
        delete_filter = self._build_filter(filters)
        
        if delete_filter is None:
            return {"status": "error", "message": "No valid filters provided"}
        
        try:
            self._client.delete(
                collection_name=namespace,
                points_selector=FilterSelector(filter=delete_filter)
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        return {
            "status": "success",
            "operation": "delete_embeddings",
            "namespace": namespace,
            "filters": filters
        }
    
    @service_error_handler(__MODULE)
    def delete_namespace(self, namespace: str) -> bool:
        """Delete entire collection/namespace"""
        try:
            self._client.delete_collection(namespace)
            return True
        except UnexpectedResponse:
            return True  # Collection didn't exist
        except Exception:
            return False
    
    @service_error_handler(__MODULE)
    def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete all collections for a user"""
        try:
            collections = self._client.get_collections()
            user_prefix = f"user_{user_id}_"
            deleted_collections = []
            
            for collection in collections.collections:
                if collection.name.startswith(user_prefix):
                    try:
                        self._client.delete_collection(collection.name)
                        deleted_collections.append(collection.name)
                    except Exception:
                        continue
            
            return {
                "status": "success",
                "operation": "delete_user_data",
                "user_id": user_id,
                "collections_deleted": deleted_collections,
                "count": len(deleted_collections)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _ensure_collection_exists(self, collection_name: str, vector_size: int):
        """Create collection if it doesn't exist"""
        try:
            self._client.get_collection(collection_name)
        except UnexpectedResponse:
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            
            # Create indexes with error handling
            try:
                self._client.create_payload_index(
                    collection_name=collection_name, 
                    field_name="document_id", 
                    field_schema="keyword"
                )
                self._client.create_payload_index(
                    collection_name=collection_name, 
                    field_name="user_id", 
                    field_schema="keyword"
                )
                self._client.create_payload_index(
                    collection_name=collection_name, 
                    field_name="company_id", 
                    field_schema="keyword"
                )
            except Exception:
                pass  # Indexes might already exist
    
    def _build_filter(self, filters: Dict[str, Any]) -> Optional[Filter]:
        """Build Qdrant filter from dictionary"""
        conditions = []
        
        for key, value in filters.items():
            if value is not None:
                conditions.append(FieldCondition(
                    key=key,
                    match=MatchValue(value=str(value))
                ))
        
        return Filter(must=conditions) if conditions else None