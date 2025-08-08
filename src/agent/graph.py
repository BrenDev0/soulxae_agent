from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from src.agent.nodes.classify_intent import classify_intent
from src.agent.nodes.general_query import general_query
from src.agent.services.appointments_service import AppoinmentsService
from src.agent.nodes.agent_handoff import agent_handoff
from src.agent.state import State
from src.dependencies.container import Container

def create_graph(llm: ChatOpenAI):
    graph = StateGraph(State)

    async def classify_intent_node(state):
        return await classify_intent(llm, state)
    
    async def agent_handoff_node(state):
        return await agent_handoff(llm, state)

    async def general_query_node(state):
        return await general_query(llm, state)
    
    # Appointments
    appointments_service: AppoinmentsService = Container.resolve("appointments_service") 
    
    async def extract_appointment_data_node(state):
        return await appointments_service.extract_and_set_data(llm, state)
    
    async def appointments_router_node(state):
        return await appointments_service.appointment_router(state)
    
    async def ask_name_node(state):
        return await appointments_service.ask_name(llm, state)
    
    async def ask_email_node(state):
        return await appointments_service.ask_email(llm, state)
    
    async def ask_phone_node(state):
        return await appointments_service.ask_phone(llm, state)
    
    async def ask_availability_node(state):
        return await appointments_service.ask_availability(llm, state)
    
    async def check_availability_node(state):
        return await appointments_service.check_avialablitly(llm, state)
    
    async def cancel_appointment_node(state):
        return await appointments_service.cancel_appointment(llm, state)
    
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_query", general_query_node) 
    graph.add_node("hand_off", agent_handoff_node)
    graph.add_node("appointment", extract_appointment_data_node)
    graph.add_node("appointment_router", appointments_router_node)
    graph.add_node("ask_name", ask_name_node)
    graph.add_node("ask_email", ask_email_node)
    graph.add_node("ask_phone", ask_phone_node)
    graph.add_node("ask_availability", ask_availability_node)
    graph.add_node("check_availability", check_availability_node)
    graph.add_node("cancel_appointment", cancel_appointment_node)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("general_query", END)
    graph.add_edge("hand_off", END)
    graph.add_edge("appointment", "appointment_router")
    graph.add_edge("ask_name", END)
    graph.add_edge("ask_email", END)
    graph.add_edge("ask_phone", END)
    graph.add_edge("ask_availability", END)
    graph.add_edge("check_availability", END)
    graph.add_edge("cancel_appointment", END)

    graph.add_conditional_edges(
        "classify_intent", 
        lambda state: state["intent"],
        {
            "general_query": "general_query",
            "human": "hand_off",
            "new_appointment": "appointment",
            "cancel_appointment": "appointment"
            
        }
    )

    graph.add_conditional_edges(
        "appointment_router",
        lambda state: state["next_node"],
        {
            "ask_name": "ask_name",
            "ask_email": "ask_email",
            "ask_phone": "ask_phone",
            "ask_availability": "ask_availability",
            "check_availability": "check_availability",
            "cancel_appointment": "cancel_appointment"
        }
    )

    return graph.compile()