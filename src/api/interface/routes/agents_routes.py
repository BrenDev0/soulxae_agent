from fastapi import APIRouter, Depends, Body, BackgroundTasks
from src.api.domain.agents_models import InteractionRequest
from src.workflows.graph import create_graph
from src.api.interface.controllers.agent_controller import AgentController
from src.api.interface.middleware.hmac_verification import verify_hmac
from src.api.dependencies import get_agents_controller

router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)


# Routes
@router.post("/interact", status_code=200)
async def interact(
    background_tasks: BackgroundTasks,
    data: InteractionRequest = Body(...),
    _: None = Depends(verify_hmac),
    graph = Depends(create_graph),
    controller: AgentController = Depends(get_agents_controller) 
):
    return await controller.interact(
        data=data,
        graph=graph,
        background_tasks=background_tasks
    )