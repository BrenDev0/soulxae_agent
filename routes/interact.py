from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from middleware import MiddlewareService

router = APIRouter(
    prefix="/api/agent/interact",
    tags=["Agent"]
)

middleware_service = MiddlewareService()

@router.post("/interact", response_class=JSONResponse)
async def createComponent(
    backgroundTasks: BackgroundTasks,
    client_request: str,
    _: None = Depends(middleware_service.auth)
):
    return