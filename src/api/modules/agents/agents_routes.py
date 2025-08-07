from fastapi import APIRouter, Depends, Body, BackgroundTasks
from src.dependencies.container import Container
from src.api.modules.agents.agents_models import InteractionRequest
from src.agent.graph import create_graph
from langchain_openai import ChatOpenAI
from src.api.modules.agents.agent_controller import AgentController
from src.api.core.services.redis_service import RedisService
from src.agent.state import State

router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)

# Dependencies
async def get_state(data: InteractionRequest = Body(...)) -> State: 
    redis_service: RedisService = Container.resolve("redis_service")
    state = await redis_service.get_session(f"conversation_state:{data.conversation_id}")

    return state

async def get_graph(state: State = Depends(get_state)): 
    llm = ChatOpenAI(
            model="gpt-4o",
            temperature=state["temperature"],
            max_completion_tokens=state["max_tokens"]
        )
    return create_graph(llm)

def get_controller():
    controller = Container.resolve("agents_controller")
    return controller


# Routes
@router.post("/interact", status_code=200)
async def interact(
    background_tasks: BackgroundTasks,
    data: InteractionRequest = Body(...),
    state: State = Depends(get_state),
    graph = Depends(get_graph),
    controller: AgentController = Depends(get_controller) 
):
    return await controller.interact(
        state=state,
        graph=graph,
        background_tasks=background_tasks
    )