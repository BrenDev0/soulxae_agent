from services.embedding_service import EmbeddingService
from sqlalchemy.orm import Session
from tools.tool_registry import tool_registry
from models.db.models import Agent_Tool
from typing import List

class ToolsService: 
    def __init__(
            self, 
            session: Session,
            embedding_service: EmbeddingService
        ):
        self.session = session
        self.embedding_service = embedding_service
        self.tool_registry = tool_registry

    def configure_tools(self):
        print("configuring tools")
        for tool in tool_registry:
            self.embedding_service.add_tool(
                name=tool.name,
                description=tool.description
            )
        print("Tools configured")
    
    def get_agents_tools(self, agent_id: str) -> List[str]: 
        tools = self.session.query(Agent_Tool).filter_by(agent_id=agent_id).all()
        
        return [
            tool.tool_id for tool in tools
        ]
    
    def get_tools_for_model(self, tool_ids: List[str]): 
        return [
            self.tool_registry[tool_id]
            for tool_id in tool_ids
            if tool_id in self.tool_registry
        ]