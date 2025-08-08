import httpx
import os
from src.agent.state import State
from langchain_openai import ChatOpenAI
from src.dependencies.container import Container
from src.agent.services.prompt_service import PromptService

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
    
    prompt_service: PromptService = Container.resolve("prompt_service")

    system_message = f"""
        The client has requested to speak with a human representative,
        or theyve requested help in a service that you cannot provide.
        Let them  know that you will tranfer them, and an agent will be with them at the earliest convenience.
        Only answer in {state['chat_language']}
    """

    prompt = prompt_service.custom_prompt_template(state=state, system_message=system_message)
        
    chain = prompt | llm
    
    response = await chain.ainvoke({"input": state["input"]})

    state["response"] = response.content.strip()

    return state