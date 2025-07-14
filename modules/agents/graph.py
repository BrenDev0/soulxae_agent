from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from modules.agents.nodes import classify_intent
from modules.agents.nodes import general_query
from  modules.tools.agent_handoff import agent_handoff

def create_graph(llm: ChatOpenAI):
    graph = StateGraph()

    graph.add_node("classify_intent", lambda state: classify_intent(llm, state))
    graph.add_node("general_query", lambda state:  general_query(llm, state)) 
    graph.add_node("hand_off", agent_handoff)

    graph.add_conditional_edges(
        "classify_intent", 
        lambda state: state["intent"],
        {
            "general_query": "general_query"
        }
    )

    graph.add_edge("general_query", END)

    graph.set_entry_point("classify_intent")

    return graph.compile()