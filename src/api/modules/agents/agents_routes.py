from fastapi import APIRouter, Depends, Body
from src.dependencies.container import Container
from src.api.modules.agents.agents_models import InteractionRequest
from src.agent.graph import create_graph
from langchain_openai import ChatOpenAI
from src.api.modules.agents.agent_controller import AgentController

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

@router.post("/interact", status_code=200)
async def interact(
    data: InteractionRequest = Body(...),
    graph = Depends(get_graph),
    controller: AgentController = Depends(get_controller)
):
    return await controller.interact(
        data=data,
        graph=graph
    )