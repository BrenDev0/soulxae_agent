from langchain.tools import tool
import httpx

@tool
async def agent_handoff(conversation_id: str, token: str) -> dict:
    """Trigger agent handoff by updating the conversation's status."""
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
