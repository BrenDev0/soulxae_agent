from langchain_openai import OpenAIEmbeddings
import faiss
import numpy as np
from typing import List, Tuple, Dict, Union
import uuid

class EmbeddingService:
    def __init__(self):
        self.model = OpenAIEmbeddings(
            model="text-embedding-3-large"
        )

        self.tool_index = faiss.IndexFlat(1536)
        self.tool_metadata = {}

        self.doc_index = faiss.IndexFlat(1536)
        self.doc_metadata = {}

    async def get_embedding(self,  text: str) -> List[float]: 
        vectors = await self.model.aembed_query(text)
        return vectors


    async def add_tool(self, tool_id: str, description: str, metadata: Dict = {}):
        embedding = await self.get_embedding(description)
        self.tool_index.add(np.array([embedding], dtype=np.float32))

        index = len(self.tool_metadata)
        self.tool_metadata[index] = {
            "tool_id": tool_id,
            "description": description,
            **metadata
        }

    async def search_tool(self, query: str, tok_k: int = 3, threshold: float = 0.8) -> List[Dict]:
        query_embedding = await self.get_embedding(query)
        D, I = self.tool_index.search(np.array([query_embedding], dtype=np.float32), tok_k)

        results = []
        for idx, dist in zip([I[0]], D[0]):
            if idx == -1:
                continue
            score = 1 / (1 + dist)
            if score >= threshold:
                metadata = self.tool_metadata.get(idx, {})
                tool_id = metadata.get("tool_id")

                if tool_id:
                    results.append(tool_id)

        return results
