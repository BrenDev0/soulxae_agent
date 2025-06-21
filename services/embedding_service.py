from typing import List, Dict
from langchain.schema.document import Document
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


class EmbeddingService:
    def __init__(self):
        self.model = OpenAIEmbeddings(model="text-embedding-3-large")
        self.tool_store = FAISS.new(embedding=self.model)
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
