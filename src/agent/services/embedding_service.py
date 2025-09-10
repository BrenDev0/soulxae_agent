from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from src.utils.decorators.service_error_handler import service_error_handler
import os
import uuid
from typing import Dict, Any
from uuid import UUID

class EmbeddingService:
    __MODULE = "embeddings.service"
    
    def __init__(self, client: QdrantClient):
        self.client = client
        
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    @service_error_handler(__MODULE)
    def get_collection_name(self, user_id: str, company_id: str) -> str:
        return f"user_{user_id}_agent_{company_id}"
    
    @service_error_handler(__MODULE)
    def ensure_collection_exists(self, user_id: str, company_id: str) -> None:
        collection_name = self.get_collection_name(user_id, company_id)
        
        try:
            self.client.get_collection(collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
            )

    @service_error_handler(__MODULE)
    async def add_document(
        self,
        s3_url: str,
        filename: str,
        user_id: str,
        agent_id: str
    ) -> Dict[str, Any]:
        self.ensure_collection_exists(user_id, agent_id)
        collection_name = self.get_collection_name(user_id, agent_id)

        if filename.endswith('.pdf'):
            loader = PyPDFLoader(s3_url)
        elif filename.endswith('.txt'):
            loader = TextLoader(s3_url)
        elif filename.endswith('.csv'):
            loader = CSVLoader(s3_url)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        embeddings = await self.embedding_model.aembed_documents(texts)

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append({
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {
                    "text": chunk.page_content,
                    "filename": filename,
                    "user_id": user_id,
                    "agent_id": agent_id
                }
            })

        # --- Batching upserts to avoid Qdrant payload limit ---
        BATCH_SIZE = 200  # You can adjust this as needed

        def batch(iterable, n=1):
            l = len(iterable)
            for ndx in range(0, l, n):
                yield iterable[ndx:min(ndx + n, l)]

        for batch_points in batch(points, BATCH_SIZE):
            self.client.upsert(collection_name=collection_name, points=batch_points)
        # -----------------------------------------------------

        return {
            "status": "success",
            "chunks_processed": len(points),
            "collection": collection_name
        }

    @service_error_handler(__MODULE)
    def delete_document_data(self, user_id: str, agent_id: str, filename: str) -> Dict[str, Any]:
        """Delete all embeddings for a specific document"""
        collection_name = self.get_collection_name(user_id, agent_id)
        
        points_filter = Filter(
            must=[
                FieldCondition(key="filename", match=MatchValue(value=filename)),
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="agent_id", match=MatchValue(value=agent_id))
            ]
        )
        
        result = self.client.delete(
            collection_name=collection_name,
            points_selector=points_filter
        )
        
        return {
            "status": "success",
            "operation": "delete_document",
            "filename": filename,
            "collection": collection_name
        }

    @service_error_handler(__MODULE)
    def delete_agent_data(self, user_id: str, agent_id: str) -> Dict[str, Any]:
        """Delete entire collection for an agent (all documents)"""
        collection_name = self.get_collection_name(user_id, agent_id)
        
        self.client.delete_collection(collection_name)
        return {
            "status": "success",
            "operation": "delete_company",
            "collection_deleted": collection_name
        }

    @service_error_handler(__MODULE)
    def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete all collections for a user (across all agents)"""
        collections = self.client.get_collections()
        user_prefix = f"user_{user_id}_agent_"
        deleted_collections = []
        
        for collection in collections.collections:
            if collection.name.startswith(user_prefix):
                self.client.delete_collection(collection.name)
                deleted_collections.append(collection.name)
        
        return {
            "status": "success",
            "operation": "delete_user",
            "collections_deleted": deleted_collections,
            "count": len(deleted_collections)
        }