from fastapi import APIRouter, BackgroundTasks, Depends, Body, Request
from fastapi.responses import JSONResponse
from middleware.middleware_service import MiddlewareService
from sqlalchemy.orm import Session
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
    response = await agent_service.interact(
        conversation_id=data.conversation_id,
        agent_id=data.agent_id,
        input=data.input,
        user_id=user_id
    )

    print(response)
    
    return JSONResponse(status_code=200, content={"message": response});