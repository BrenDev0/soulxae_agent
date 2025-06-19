from  .embedding_service import EmbeddingService
from.prompt_service import PromptService
from typing import List

class AgentService:
    def __init__(self, embeddings_service: EmbeddingService, prompt_service: PromptService):
        self.embeddings_service = embeddings_service
        self.prompt_service = prompt_service
    
    
    def build_agent(self, allowed_tools: List[str], input: str):
        tools = self.embeddings_service.search_tool(input)

        agents_tools = []
        for tool in tools and tool in allowed_tools:
            agents_tools.append(tool)
        
        
        
        prompt = self.prompt_service.build_prompt_template()