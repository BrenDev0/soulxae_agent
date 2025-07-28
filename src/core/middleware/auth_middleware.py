# middleware/auth_middleware.py
from fastapi import Request, HTTPException
from core.dependencies.container import Container
from fastapi.responses import JSONResponse

async def auth_middleware(request: Request, call_next):
    if request.url.path in []:
        return await call_next(request)
    
    try:
        middleware_service = Container.resolve("middleware_service")
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
        