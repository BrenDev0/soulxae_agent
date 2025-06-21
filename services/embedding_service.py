from typing import List, Dict
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS 
from langchain.docstore import InMemoryDocstore
import faiss

class EmbeddingService:
    def __init__(self):
        self.model = OpenAIEmbeddings(model="text-embedding-3-large")
        
        dimension = 3027
        index = faiss.IndexFlatIP(dimension)
        
        docstore = InMemoryDocstore({})

        index_to_docstore_id = {} 

        self.tool_store = FAISS(
            self.model.embed_query,
            index,
            docstore,
            index_to_docstore_id
        )

        self._tools_added = 0

    async def add_tool(self, tool_id: str, description: str, metadata: Dict = {}):
        doc = Document(
            page_content=description,
            metadata={"tool_id": tool_id, **metadata}
        )
        self.tool_store.add_documents([doc])
        self._tools_added += 1

    async def search_tool(self, query: str, top_k: int = 3, threshold: float = 0.8) -> List[str]:
        if self._tools_added == 0:
            return []

        results = await self.tool_store.asimilarity_search_with_score(query, k=top_k)

        matches = []
        for doc, score in results:
            if score >= threshold:
                tool_id = doc.metadata.get("tool_id")
                if tool_id:
                    matches.append(tool_id)

        return matches
