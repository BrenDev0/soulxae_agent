from fastapi import APIRouter, BackgroundTasks, Depends, Body
from fastapi.responses import JSONResponse
from middleware.middleware_service import MiddlewareService
from sqlalchemy.orm import Session
from dependencies.container import Container
from database.sessions import get_db_session
from models.models import InteractionRequest

router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)
def get_container(db: Session = Depends(get_db_session)) -> Container:
    return Container(db)

middleware_service = MiddlewareService()

@router.post("/interact", response_class=JSONResponse)
async def interact(
    backgroundTasks: BackgroundTasks,
    data: InteractionRequest = Body(...),
    container: Container = Depends(get_container),
    _: None = Depends(middleware_service.auth)
):
    print(data.conversation_id)
    print(data.agent_id)
    
    return JSONResponse(status_code=200, content="recived");