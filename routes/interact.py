from fastapi import APIRouter, BackgroundTasks, Depends, Body, Request
from fastapi.responses import JSONResponse
from dependencies.container import Container
from models.models import InteractionRequest
from services.agent_service import AgentService

router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)

@router.post("/interact", response_class=JSONResponse)
async def interact(
    request: Request,
    backgroundTasks: BackgroundTasks,
    data: InteractionRequest = Body(...),
):
    user_id = request.state.user_id
    agent_service: AgentService = Container.resolve("agent_service")

    backgroundTasks.add_task(agent_service.interact, data.conversation_id, data.agent_id, data.input, user_id)
   
    
    return JSONResponse(status_code=200, content={"message": "input recieved"});