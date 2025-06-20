from services.embedding_service import EmbeddingService
from sqlalchemy.orm import Session
from tools.tool_registry import tool_registry
from models.db.models import Agent_Tool
from typing import List
from langchain.tools import Tool
from functools import partial

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
        for tool_id, tool in self.tool_registry.items():
            self.embedding_service.add_tool(
                tool_id=tool_id,
                description=tool.description
            )

        print("Tools configured")
    
    def get_agents_tools(self, agent_id: str) -> List[str]: 
        tools = self.session.query(Agent_Tool).filter_by(agent_id=agent_id).all()
        
        return [
            tool.tool_id for tool in tools
        ]
    
    def get_tools_for_model(self, 
        tool_ids: List[str],
        conversation_id: str,
        token: str
    ) -> List[Tool]:
        tools = []

        for tool_id in tool_ids:
            if tool_id in self.tool_registry:
                tool_def = self.tool_registry[tool_id]
                
                func = tool_def.func
                if tool_def.name == "agent_handoff":
                    func = partial(func, conversation_id=conversation_id, token=token)

                tools.append(
                    Tool.from_function(
                        func=func,    
                        name=tool_def.name,          
                        description=tool_def.description  
                    )
                )

        return tools