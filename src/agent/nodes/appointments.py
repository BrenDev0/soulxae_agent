from typing import Dict
from ..state import State
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage
import json
from src.dependencies.container import Container
from src.agent.services.prompt_service import PromptService


async def ask_name(llm: ChatOpenAI, state: State):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(f"Ask the user their full name in a friendly and natural tone. Always respond in {state['chat_language']}."),
        ("human", "{input}")
    ])
    chain = prompt | llm
    res = await chain.ainvoke({"input": state["input"]})
    state["response"] = res.content.strip()
    return state

async def ask_email(llm: ChatOpenAI, state: State):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(f"Ask the user their email in a friendly and natural tone. Always respond in {state['chat_language']}."),
        ("human", "{input}")
    ])
    chain = prompt | llm
    res = await chain.ainvoke({"input": state["input"]})
    state["response"] = res.content.strip()
    return state

async def ask_phone(llm: ChatOpenAI, state: State):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(f"Ask the user their phone in a friendly and natural tone. Always respond in {state['chat_language']}."),
        ("human", "{input}")
    ])
    chain = prompt | llm
    res = await chain.ainvoke({"input": state["input"]})
    state["response"] = res.content.strip()
    return state

async def ask_availability(llm: ChatOpenAI, state: State):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(f"Ask the user their prefered appiontment date and time in a friendly and natural tone. Always respond in {state['chat_language']}."),
        ("human", "{input}")
    ])
    chain = prompt | llm
    res = await chain.ainvoke({"input": state["input"]})
    state["response"] = res.content.strip()
    return state



async def extract_and_set_data(llm: ChatOpenAI, state: State):
    prompt_service: PromptService = Container.resolve("prompt_service")
    prompt = prompt_service.appointment_data_extraction_prompt(state=state)
    
    chain = prompt | llm
    res = await chain.ainvoke({"input": state["input"]})
  
    print("EXTRACT DATA:::::", res.content)
    parsed = json.loads(res.content)

    # Update state
    appointment = state["appointments_state"]
    for key in ["name", "email", "phone", "appointment_datetime"]:
        if parsed.get(key):
            appointment[key] = parsed[key]

    state["next_node"] = "appointment_router"
    return state


async def check_avialablitly(state: State):
    state["response"] = "your date hase been confirmed"

    return state

    
async def appointment_router(state: State):
    appt = state["appointments_state"]
    if not appt.get("name"):
        state["next_node"] = "ask_name"
    elif not appt.get("email"):
        state["next_node"] = "ask_email"
    elif not appt.get("phone"):
        state["next_node"] = "ask_phone"
    elif not appt.get("appointment_datetime"):
        state["next_node"] = "ask_availability"
    else:
        state["next_node"] = "check_availability"
    return state
