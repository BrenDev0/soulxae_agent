from langchain_core.tools import Tool
import httpx

@Tool
async def agent_handoff(conversation_id: str, token: str):
    url = f"https://soulxae.up.railway.app/conversations/{conversation_id}/agent-handoff?status=true"
    header = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                headers=header
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        print(f"Agent handoff failed: {exc.response.status_code} - {exc.response.text}")