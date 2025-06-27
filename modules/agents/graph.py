from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from modules.agents.nodes import classify_intent

def create_graph(llm: ChatOpenAI):
    graph = StateGraph()

    graph.add_node("classify_intent", lambda state: classify_intent(llm, state))
    graph.add_node()