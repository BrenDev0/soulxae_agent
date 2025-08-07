from src.agent.state import State
from src.api.core.services.redis_service import RedisService
from src.dependencies.container import Container
from src.api.modules.agents.agents_models import InteractionRequest
from fastapi import BackgroundTasks


class AgentController:
    async def interact(
        self,
        state: State,
        graph,
        background_tasks: BackgroundTasks
    ): 
        ## use only when meta is connected
        # background_tasks.add_task(self.hanlde_interaction, state, graph)
        
        # return 

        ## only for testing 
        final_state: State = await graph.ainvoke(state)
        background_tasks.add_task(self.handle_state, final_state)

        return { "data": final_state["response"]}


    
    async def handle_state(self, state: State):
        redis_service: RedisService = Container.resolve("redis_service")
        await redis_service.set_session(f"conversation_state:{state['conversation_id']}", state)


    async def hanlde_interaction(self, state: State, graph):
        final_state: State = await graph.ainvoke(state)
        await self.handle_state(final_state)