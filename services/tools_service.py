from ..dependencies.container import embedding_service
from ..tools.tool_registry import tool_registry
from typing import List

class ToolsService: 
    def __init__(self):
        self.ebedding_service = embedding_service
        self.tool_resgisty = tool_registry

    def configure_tools(self):
        for tool in tool_registry:
            embedding_service.add_tool(
                tool_id=tool["id"],
                description=tool["description"]
            )
    
    def get_agents_tools(self, tool_ids: List[str]): 
        tools = []

        for tool in tool_ids:
            tools.append(self.tool_resgisty[tool])

        return tools