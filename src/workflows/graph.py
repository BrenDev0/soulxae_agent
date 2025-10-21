from fastapi import Depends
import os
import httpx
from langgraph.graph import StateGraph, END, START

from src.workflows.application.agents.appoinments_agent import AppointmentsAgent
from src.workflows.application.agents.general_query_agent import GeneralQueryAgent
from src.workflows.application.agents.orchestrator_agent import Orchestrator
from src.workflows.application.agents.handoff_agent import HandoffAgent
from src.workflows.dependencies import get_appointments_agent, get_general_query_agent, get_orchestrator, get_handoff_agent
from src.workflows.domain.state import State


def create_graph(
    appointments_agent: AppointmentsAgent = Depends(get_appointments_agent),
    general_queary_agent: GeneralQueryAgent = Depends(get_general_query_agent),
    orchestrator: Orchestrator = Depends(get_orchestrator),
    handoff_agent: HandoffAgent = Depends(get_handoff_agent)
):
    graph = StateGraph(State)

    async def orchestrator_node(state: State):
        res = await orchestrator.interact(state=state)

        return {
            "appointment_data": res.appointment_data,
            "intent": res.intent
        }

    async def appointments_node(state: State):
        res = await appointments_agent.interact(state=state)

        return {"response": res}
    
    async def general_query_node(state: State):
        res = await general_queary_agent.interact(state)

        return {"response": res}
    
    async def handoff_node(state: State):
        host = os.getenv("APP_HOST")
        conversation_id = state["conversation_id"]
        token = state["token"]
        
        url = f"https://{host}/conversations/secure/{conversation_id}/agent-handoff?status=true"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(url, headers=headers)
                response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            print(f"Agent handoff failed: {exc.response.status_code} - {exc.response.text}")
            return {"error": exc.response.text, "status_code": exc.response.status_code}
        
        res = await handoff_agent.interact(state=state)

        return {"response": res}
        

    async def router(state: State):
        intent = state["intent"]

        if intent == "appointments":
            return "appointments"
        
        elif intent == "general_query":
            return "general_query"
        
        else:
            return "human"
        
    
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("appointments", appointments_node)
    graph.add_node("general_query", general_query_node)
    graph.add_node("handoff", handoff_node)

    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator",
        router,
        {
            "appointments": "appointments",
            "general_query": "general_query",
            "human": "handoff"
        }
    )
    graph.add_edge("general_query", END)
    graph.add_edge("appointments", END)
    graph.add_edge("handoff", END)

    return graph.compile()