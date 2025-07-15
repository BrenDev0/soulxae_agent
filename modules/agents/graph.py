from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from modules.agents.nodes.classify_intent import classify_intent
from modules.agents.nodes.general_query import general_query
from modules.agents.nodes.appointment_flow import appointment_flow
from modules.agents.nodes.agent_handoff import agent_handoff
from modules.agents.state import State

def create_graph(llm: ChatOpenAI):
    graph = StateGraph(State)

    
    async def classify_intent_node(state):
        return await classify_intent(llm, state)

    async def general_query_node(state):
        return await general_query(llm, state)
    
    async def appointments_node(state):
        return await appointment_flow(llm, state) 

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_query", general_query_node) 
    graph.add_node("appointment", appointments_node)
    graph.add_node("hand_off", agent_handoff)

    graph.add_conditional_edges(
        "classify_intent", 
        lambda state: state["intent"],
        {
            "general_query": "general_query",
            "human": "hand_off",
            "appointment": "appointment"
            
        }
    )

    graph.add_edge("general_query", END)
    graph.add_edge("hand_off", END)
    graph.add_edge("appointment", END)

    graph.set_entry_point("classify_intent")

    return graph.compile()