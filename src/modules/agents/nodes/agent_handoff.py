import httpx
import os
from src.modules.agents.state import State
from langchain_openai import ChatOpenAI

async def agent_handoff_tool(state: State) -> State:
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


async def agent_handoff(llm: ChatOpenAI, state: State):

    await agent_handoff_tool(state=state)
    prompt = f"""
        The client has requested to speak with a human representative please let them  know that you will tranfer them
        only anwer in {state['chat_language']}
    """

    response = await llm.ainvoke(prompt)

    print(response.content, "RESPONSE::::::::::::")