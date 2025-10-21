import tiktoken
import io
import PyPDF2
from typing import List
from openai import AsyncOpenAI
import uuid

from src.shared.domain.embedding_service import EmbeddingService
from src.workflows.domain.entities import EmbeddingResult, DocumentChunk

class OpenAIEmbeddingService(EmbeddingService):
    def __init__(self, api_key: str, model: str = "text-embedding-3-large"):
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._encoding = tiktoken.get_encoding("cl100k_base")
    
    async def embed_document(
        self,
        file_bytes: bytes,
        filename: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **metadata
    ) -> EmbeddingResult:
        """Process document and create embeddings without LangChain"""
        
        # Extract text based on file type
        text = self._extract_text(file_bytes, filename)
        
        # Split into chunks
        chunks = self._split_text(text, chunk_size, chunk_overlap)
        
        # Create document chunks with metadata
        document_chunks = []
        for i, chunk_text in enumerate(chunks):
            document_chunks.append(DocumentChunk(
                content=chunk_text,
                metadata={
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **metadata
                },
                chunk_id=f"{filename}_{i}_{uuid.uuid4()}"
            ))
        
        # Generate embeddings
        texts = [chunk.content for chunk in document_chunks]
        embeddings = await self._embed_texts(texts)
        
        # Calculate tokens (approximate)
        total_tokens = sum(len(self._encoding.encode(chunk.content)) for chunk in document_chunks)
        
        return EmbeddingResult(
            chunks=document_chunks,
            embeddings=embeddings,
            total_tokens=total_tokens
        )
    
    async def embed_query(self, query: str) -> List[float]:
        """Embed a single query"""
        result = await self._client.embeddings.create(
            model=self._model,
            input=query
        )
        return result.data[0].embedding
    
    def get_embedding_dimension(self) -> int:
        """Return embedding dimension based on model"""
        model_dimensions = {
            "text-embedding-3-large": 3072,
            "text-embedding-3-small": 1536,
            "text-embedding-ada-002": 1536
        }
        return model_dimensions.get(self._model, 1536)
    
    def _extract_text(self, file_bytes: bytes, filename: str) -> str:
        """Extract text from different file types"""
        if filename.endswith('.pdf'):
            return self._extract_pdf_text(file_bytes)
        elif filename.endswith('.txt'):
            return file_bytes.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    def _extract_pdf_text(self, file_bytes: bytes) -> str:
        """Extract text from PDF without LangChain"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    
    def _split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Simple text splitter without LangChain"""
        words = text.split()
        chunks = []
        
        if len(words) <= chunk_size:
            return [text]
        
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
        
        return chunks
    
    async def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts efficiently"""
        # Batch process embeddings
        batch_size = 50  # Adjust based on your needs
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self._client.embeddings.create(
                model=self._model,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
