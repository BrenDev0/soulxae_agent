import httpx
from src.core.dependencies.container import Container
from src.core.services.webtoken_service import WebTokenService


class MessagingService:
    async def send_message(self, text: str, user_id: str, conversation_id: str): 
        print(text)
        webtoken_service: WebTokenService = Container.resolve("webtoken_service")
        token = webtoken_service.generate_token({"userId": user_id}, "2m")

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
