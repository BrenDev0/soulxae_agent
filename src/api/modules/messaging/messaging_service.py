import httpx
from src.dependencies.container import Container
from src.api.core.services.webtoken_service import WebTokenService


class MessagingService:
    async def send_message(self, text: str, token: str, conversation_id: str): 
        url = f"https://soulxae.up.railway.app/direct/secure/send"
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "conversationId": conversation_id,
            "type": "text",
            "text": text
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, data=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            print(f"Unable to send message: {exc.response.status_code} - {exc.response.text}")
            return {"error": exc.response.text, "status_code": exc.response.status_code}
