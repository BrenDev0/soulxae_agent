from fastapi import APIRouter, BackgroundTasks, Depends, Body
from fastapi.responses import JSONResponse
from middleware.middleware_service import MiddlewareService
from sqlalchemy.orm import Session
from dependencies.container import Container
from models.models import InteractionRequest


router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)


middleware_service = MiddlewareService()

@router.post("/interact", response_class=JSONResponse)
async def interact(
    backgroundTasks: BackgroundTasks,
    data: InteractionRequest = Body(...),
    token: str = Depends(middleware_service.auth)
):
    
    agent_service = Container.resolve("agent_service")
    response = await agent_service.interact(
        conversation_id=data.conversation_id,
        agent_id=data.agent_id,
        input=data.input,
        token=token
    )

    print(response)
    
    return JSONResponse(status_code=200, content={"message": response});