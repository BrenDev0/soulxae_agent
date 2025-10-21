from fastapi import Request, HTTPException, Depends
from shared.dependencies.container import Container
from fastapi.responses import JSONResponse

from api.dependencies import get_middleware_service

async def auth_middleware(request: Request, call_next, middleware_service = Depends(get_middleware_service)):
    if request.url.path in []:
        return await call_next(request)
    
    try:
        token = await middleware_service.auth(request)
        if not token["userId"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        request.state.user_id = token["userId"]
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.detail}
        )
        