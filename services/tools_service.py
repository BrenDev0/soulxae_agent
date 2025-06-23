from sqlalchemy.orm import Session
from tools.tool_registry import tool_registry
from models.db.models import Agent_Tool
from typing import List
from langchain.tools import Tool
from functools import partial
from dependencies.container import Container
from services.webtoken_service import WebTokenService

class ToolsService: 
    def __init__(
        self, 
        session: Session
    ):
        self.session = session
        self.tool_registry = tool_registry
    
    def get_agents_tools(self, agent_id: str, conversation_id: str, user_id: str) -> List[Tool]: 
        availible_tools = self.session.query(Agent_Tool).filter_by(agent_id=agent_id).all()
        tool_ids =  [
            str(tool.tool_id) for tool in availible_tools
        ]
        
        return self.get_tools_from_registry(
            tool_ids=tool_ids,
            conversation_id=conversation_id,
            user_id=user_id
        )
    
    def get_tools_from_registry(self, 
        tool_ids: List[str],
        conversation_id: str,
        user_id: str
    ) -> List[Tool]:
        tools = []

        webtoken_service: WebTokenService = Container.resolve("webtoken_service")
        token = webtoken_service.generate_token({"userId": user_id}, "2m")

        for tool_id in tool_ids:
            if tool_id not in self.tool_registry:
                continue
                
            tool_def = self.tool_registry[tool_id]
            
            if tool_def.name == "agent_handoff":
                
                async def handoff_wrapper(_: str = None) -> dict:
                    return await tool_def.coroutine(
                        conversation_id=conversation_id,
                        token=token
                    )
                
                tools.append(
                    Tool.from_function(
                        name=tool_def.name,
                        description=tool_def.description,
                        func=handoff_wrapper,  
                        coroutine=handoff_wrapper
                    )
                )
                
            elif tool_def.name == "make_appointment":  
                tools.append(
                    Tool.from_function(
                        func=partial(tool_def.coroutine, token=token),
                        name=tool_def.name,
                        description=tool_def.description
                    )
                )
            else:
                tools.append(
                    Tool.from_function(
                        func=tool_def.coroutine,
                        name=tool_def.name,
                        description=tool_def.description
                    )
                )

        return tools