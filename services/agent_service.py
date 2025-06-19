from  services.embedding_service import EmbeddingService
from services.prompt_service import PromptService
from typing import List
from sqlalchemy.orm import Session

class AgentService:
    def __init__(self, session: Session, embeddings_service: EmbeddingService, prompt_service: PromptService):
        self.embeddings_service = embeddings_service
        self.prompt_service = prompt_service
    
    
    def build_agent(self, agent_id: str, conversation_id: str, input: str):
        tools = self.embeddings_service.search_tool(input)
        agents_tools = []
        
        pass



        