from langchain.tools import tool
from pydantic import BaseModel
import httpx

class AgentHandoffPayload(BaseModel):
    conversation_id: str
    token: str

@tool(args_schema=AgentHandoffPayload)
async def agent_handoff(conversation_id: str, token: str) -> dict:
    """
    Use this tool if the client expresses interest in speaking to a human representative,
    or if a human should handle the conversation. You will let the client know you've
    handed off the conversation and the representative will resume the conversation
    at the earliest convenience.
    """
    url = f"https://soulxae.up.railway.app/conversations/{conversation_id}/agent-handoff?status=true"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        print(f"Agent handoff failed: {exc.response.status_code} - {exc.response.text}")
        return {"error": exc.response.text, "status_code": exc.response.status_code}
