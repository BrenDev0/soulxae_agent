from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader
)
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue,  PointIdsList
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import os
from typing import Optional, List, Dict, Union, BinaryIO
from io import BytesIO
import uuid
import time

class EmbeddingService:
    def __init__(self, embedding_model=None):
        self.client = QdrantClient(
            base_url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        self.embedding_model = embedding_model or OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        self.loader_mapping = {
            'application/pdf': PyPDFLoader,
            'text/plain': TextLoader,
            'text/csv': CSVLoader,
            'application/vnd.ms-excel': UnstructuredExcelLoader,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': UnstructuredExcelLoader,
            'application/msword': UnstructuredWordDocumentLoader,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': UnstructuredWordDocumentLoader
        }
    
    def get_collection_name(self, user_id: str, agent_id: str) -> str:
        """Generate standardized collection names."""
        return f"user_{user_id}_agent_{agent_id}"
    
    async def create_collection(self, user_id: str, agent_id: str) -> bool:
        collection_name = self.get_collection_name(user_id, agent_id)
        
        try:
            self.client.get_collection(collection_name)
            return False  
        except:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=3072,
                    distance=Distance.COSINE
                ),
            )
            return True
    
    async def delete_user_data(self, user_id: str) -> int:
        deleted = 0
        collections = self.client.get_collections()
        prefix = f"user_{user_id}_agent_"
        
        for collection in collections.collections:
            if collection.name.startswith(prefix):
                self.client.delete_collection(collection.name)
                deleted += 1
        return deleted
    
    async def _process_in_memory_document(
        self, 
        file_data: BinaryIO, 
        file_type: str, 
        filename: str
    ) -> List[Dict]:
        temp_file = BytesIO()
        temp_file.write(file_data.read())
        temp_file.seek(0)
        
        loader_class = self.loader_mapping.get(file_type)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        if file_type == 'application/pdf':
            loader = loader_class(temp_file)
        else:
            temp_file.seek(0)
            content = temp_file.read().decode('utf-8')
            loader = loader_class(file_path=BytesIO(content.encode('utf-8')))
        
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        
        processed_chunks = []
        for chunk in chunks:
            processed_chunks.append({
                "text": chunk.page_content,
                "metadata": {
                    **chunk.metadata,
                    "original_filename": filename,
                    "chunk_id": str(uuid.uuid4())
                }
            })
        
        return processed_chunks
    
    async def embed_uploaded_document(
        self,
        file_data: BinaryIO,
        file_type: str,
        filename: str,
        user_id: str,
        agent_id: str,
        custom_metadata: Optional[Dict] = None
    ) -> Dict:
        collection_name = self.get_collection_name(user_id, agent_id)
        await self.create_collection(user_id, agent_id)
        
        chunks = await self._process_in_memory_document(file_data, file_type, filename)
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embedding_model.aembed_documents(texts)
        
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = {
                "user_id": user_id,
                "agent_id": agent_id,
                "upload_timestamp": int(time.time()),
                **chunk["metadata"]
            }
            
            if custom_metadata:
                metadata.update(custom_metadata)
            
            points.append({
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {
                    "text": chunk["text"],
                    "metadata": metadata
                }
            })
        
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        return {
            "status": "success",
            "chunks_processed": len(points),
            "collection": collection_name,
            "document_id": str(uuid.uuid4())
        }
    
    async def search_collection(
        self,
        query: str,
        user_id: str,
        agent_id: str,
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        collection_name = self.get_collection_name(user_id, agent_id)
        
        query_embedding = await self.embedding_model.aembed_query(query)
        
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.user_id",
                    match=MatchValue(value=user_id)
                ),
                FieldCondition(
                    key="metadata.agent_id",
                    match=MatchValue(value=agent_id)
                )
            ]
        )
        
        if filters:
            for key, value in filters.items():
                qdrant_filter.must.append(
                    FieldCondition(
                        key=f"metadata.{key}",
                        match=MatchValue(value=value)
                    )
                )
        
        
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=qdrant_filter,
            limit=top_k
        )
        
        return [{
            "text": hit.payload["text"],
            "metadata": hit.payload["metadata"],
            "score": hit.score,
            "id": hit.id
        } for hit in results]
    
    async def delete_documents(
        self,
        user_id: str,
        agent_id: str,
        document_ids: List[str]
    ) -> Dict:
        collection_name = self.get_collection_name(user_id, agent_id)
        
        self.client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(
                points=document_ids
            )
        )
        
        return {
            "status": "success",
            "deleted_count": len(document_ids),
            "collection": collection_name
        }