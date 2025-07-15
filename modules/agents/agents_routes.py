from fastapi import APIRouter, BackgroundTasks, Depends, Body, Request
from fastapi.responses import JSONResponse
from core.dependencies.container import Container
from core.services.redis_service import RedisService
from modules.agents.agents_models import InteractionRequest
from modules.agents.agent_service import AgentService
from  modules.agents.graph import create_graph
from langchain_openai import ChatOpenAI

router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"]
)

@router.post("/interact", response_class=JSONResponse)
async def interact(
    request: Request,
    backgroundTasks: BackgroundTasks,
    data: InteractionRequest = Body(...),
):
    # user_id = request.state.user_id
    # agent_service: AgentService = Container.resolve("agent_service")
    # print(data)

    # backgroundTasks.add_task(agent_service.interact, data.agent_id, data.conversation_id, user_id, data.input,)
    redis_service: RedisService = Container.resolve("redis_service")
    state = await redis_service.get_session(f"conversation_state:{data.conversation_id}")

    llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.5
        )
    graph = create_graph(llm)
    final_state = await graph.ainvoke(state)
    
    return JSONResponse(status_code=200, content={"response": final_state["response"], "intent": final_state["intent"]});