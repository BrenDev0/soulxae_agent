from fastapi import Request
from src.agent.state import State
from src.api.core.services.redis_service import RedisService
from src.dependencies.container import Container
from src.api.modules.agents.agents_models import InteractionRequest

class AgentController:
    @staticmethod
    async def interact(
        data: InteractionRequest,
        graph
    ):
        redis_service: RedisService = Container.resolve("redis_service")
        state = await redis_service.get_session(f"conversation_state:{data.conversation_id}")
        
        final_state: State = await graph.ainvoke(state)

        return { "data": final_state["response"]}