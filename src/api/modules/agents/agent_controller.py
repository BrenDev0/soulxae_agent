from src.agent.state import State
from src.api.core.services.redis_service import RedisService
from src.dependencies.container import Container
from fastapi import BackgroundTasks
from src.api.modules.messaging.messaging_service import MessagingService


class AgentController:
    async def interact(
        self,
        state: State,
        graph,
        background_tasks: BackgroundTasks
    ): 
        # use only when meta is connected
        background_tasks.add_task(self.hanlde_interaction, state, graph)
        
        return 

        ## only for testing 
        # final_state: State = await graph.ainvoke(state)
        # background_tasks.add_task(self.handle_state, final_state)

        # return { "data": final_state["response"]}



    async def hanlde_interaction(self, state: State, graph):
        messaging_service: MessagingService = Container.resolve("messaging_service")

        final_state: State = await graph.ainvoke(state)

        await messaging_service.send_message(final_state["response"], state["token"], state["conversation_id"])

        await self.handle_state(final_state)
    

    @staticmethod
    async def handle_state(state: State):
        redis_service: RedisService = Container.resolve("redis_service")
        await redis_service.set_session(f"conversation_state:{state['conversation_id']}", state)