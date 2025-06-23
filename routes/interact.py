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
    print(data)

    backgroundTasks.add_task(agent_service.interact, data.agent_id, data.conversation_id, user_id, data.input,)
   
    
    return JSONResponse(status_code=200, content={"message": "input recieved"});