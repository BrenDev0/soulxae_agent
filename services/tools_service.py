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

    async def configure_tools(self):
        print("configuring tools")
        for tool_id, tool in self.tool_registry.items():
            await self.embedding_service.add_tool(
                tool_id=tool_id,
                description=tool.description,
            )

        print("Tools configured")
    
    def get_agents_tools(self, agent_id: str, conversation_id: str, token: str) -> List[Tool]: 
        availible_tools = self.session.query(Agent_Tool).filter_by(agent_id=agent_id).all()
        tool_ids =  [
            str(tool.tool_id) for tool in availible_tools
        ]
        
        return self.get_tools_from_registry(
            tool_ids=tool_ids,
            conversation_id=conversation_id,
            token=token
        )
    
    def get_tools_from_registry(self, 
        tool_ids: List[str],
        conversation_id: str,
        token: str
    ) -> List[Tool]:
        tools = []

        for tool_id in tool_ids:
            if tool_id in self.tool_registry:
                tool_def = self.tool_registry[tool_id]
                
                func = tool_def.coroutine
                if tool_def.name == "agent_handoff":
                    func = partial(func, conversation_id=conversation_id, token=token)
                if tool_def.name == "make_appointmnet":
                    func = partial(func, token=token)

                tools.append(
                    tool_def
                )

        return tools