from fastapi import APIRouter, BackgroundTasks, Depends, Body, Request
from fastapi.responses import JSONResponse
from src.core.dependencies.container import Container
from src.core.services.redis_service import RedisService
from src.modules.agents.agents_models import InteractionRequest
from src.modules.agents.graph import create_graph
from langchain_openai import ChatOpenAI
from src.modules.agents.agent_controller import AgentController

router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)

def get_graph(): 
    llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.5
        )
    return create_graph(llm)

def get_controller():
    controller = Container.resolve("agents_controller")
    return controller

@router.post("/interact", response_class=JSONResponse)
async def interact(
    request: Request,
    backgroundTasks: BackgroundTasks,
    data: InteractionRequest = Body(...),
    graph = Depends(get_graph),
    controller: AgentController = Depends(get_controller)
):
    # user_id = request.state.user_id
    # agent_service: AgentService = Container.resolve("agent_service")
    # print(data)

    # backgroundTasks.add_task(agent_service.interact, data.agent_id, data.conversation_id, user_id, data.input,)
    return controller.interact(
        request=request,
        data=data,
        graph=graph
    )