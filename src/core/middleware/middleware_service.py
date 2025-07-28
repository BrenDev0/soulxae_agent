import os
import jwt
from fastapi import Request, HTTPException
from src.core.services.webtoken_service import WebTokenService


class MiddlewareService:
    def __init__(self, webtoken_service: WebTokenService):
        self.TOKEN_KEY = os.getenv("TOKEN_KEY")
        self.webtoken_service = webtoken_service
    
    async def auth(self, request: Request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unautrhorized, Missing required auth headers")
        
        token = auth_header.split(" ")[1]
        token_payload = self.verify_token(token)

        return token_payload
        
    
    def verify_token(self, token):
        try:
            payload = self.webtoken_service.decode_token(token=token)
            return payload
        
        except jwt.ExpiredSignatureError:
            print("token expired")
            raise HTTPException(status_code=403, detail="Expired Token")
        
        except jwt.InvalidTokenError:
            print("token invalid")
            raise HTTPException(status_code=401, detail="Invlalid token")
        
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        

