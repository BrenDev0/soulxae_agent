import httpx
import os
from modules.agents.state import State

async def agent_handoff(state: State) -> State:
    print("state in agent hand off::::::::::::", state)
    host = os.getenv("APP_HOST")
    conversation_id = state["conversation_id"]
    token = state["token"]
    
    url = f"https://{host}/conversations/secure/{conversation_id}/agent-handoff?status=true"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        print(f"Agent handoff failed: {exc.response.status_code} - {exc.response.text}")
        return {"error": exc.response.text, "status_code": exc.response.status_code}
