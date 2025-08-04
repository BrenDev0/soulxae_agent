from typing import Dict
from ..state import State
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage
import json
from src.dependencies.container import Container
from src.agent.services.prompt_service import PromptService
import os
import httpx


async def ask_name(llm: ChatOpenAI, state: State):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(f"Ask the user their full name in a friendly tone. Always respond in {state['chat_language']}."),
        ("human", "{input}")
    ])
    chain = prompt | llm
    res = await chain.ainvoke({"input": state["input"]})
    state["response"] = res.content.strip()
    return state

async def ask_email(llm: ChatOpenAI, state: State):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(f"Ask the user their email in a natural tone. Always respond in {state['chat_language']}."),
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
        SystemMessage(f"Ask the user their prefered appiontment date and time. Always respond in {state['chat_language']}."),
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
  
    parsed = json.loads(res.content)
  
    # Update state
    appointment = state["appointments_state"]
    for key in ["name", "email", "phone", "appointment_datetime"]:
        if parsed.get(key):
            appointment[key] = parsed[key]

    return state


async def check_availability_tool(state: State) -> State:
    host = os.getenv("APP_HOST")
    token = state["token"]
    
    url = f"https://{host}/google/calendars/secure/availability"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["is_available"]
    except httpx.HTTPStatusError as exc:
        print(f"Availability equest failed: {exc.response.status_code} - {exc.response.text}")
        return {"error": exc.response.text, "status_code": exc.response.status_code}
    

async def create_appoinment_tool(state: State) -> State:
    host = os.getenv("APP_HOST")
    token = state["token"]
    
    url = f"https://{host}/calendars/secure/event"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            return response.json()
        
    except httpx.HTTPStatusError as exc:
        print(f"Unable to create appointment: {exc.response.status_code} - {exc.response.text}")
        return {"error": exc.response.text, "status_code": exc.response.status_code}


async def get_available_slots(state):
    host = os.getenv("APP_HOST")
    token = state["token"]
    
    url = f"https://{host}/calendars/secure/event"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            return response.json()["data"]
        
    except httpx.HTTPStatusError as exc:
        print(f"Request failed: {exc.response.status_code} - {exc.response.text}")
        return []


async def check_avialablitly(llm: ChatOpenAI, state: State):
    is_available = await check_availability_tool(state)

    if is_available:
        await create_appoinment_tool(state)
        prompt = f"""Let the client know youve booked their appointment and thank them for thier time. 
        Only respond in {state['chat_language']}
        """
    else:
        state["appointments_state"]["appointment_datetime"] = None

        available_slots = await get_available_slots(state)
        if available_slots:
            slots_text = "\n".join([f"• {slot}" for slot in available_slots[:3]])

            prompt = f"""
            The user's requested time ({state['appointments_state']['appointment_datetime']}) is not available.
            Show them these alternative options i a ocnversation format:
            {slots_text}
            
            Ask them to choose one of these times or suggest a different time.
            Be helpful and friendly.Only respond in {state['chat_language']}
            """
        else: 
            prompt = f"""
             The user's requested time ({state['appointments_state']['appointment_datetime']}) is not available.
             Ask them  to provide an alternative date and time for thier appointment.
             Be helpful and friendly.Only respond in {state['chat_language']}
            """
    
    response = await llm.ainvoke(prompt)
    
    state["response"] = response.content.strip()

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
