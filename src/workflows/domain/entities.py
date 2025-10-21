from pydantic import BaseModel
from typing import Dict, Any, List
from typing_extensions import TypedDict

class DocumentChunk(BaseModel):
    content: str
    metadata: Dict[str, Any]
    chunk_id: str

class EmbeddingConfig(BaseModel):
    model_name: str = "text-embedding-3-large"
    distance_metric: str = "cosine"
    vector_size: int = 3072  

class EmbeddingResult(BaseModel):
    chunks: List[DocumentChunk]
    embeddings: List[List[float]]
    total_tokens: int

class SearchResult(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float

class Message(TypedDict):
    sender: str
    text: str


