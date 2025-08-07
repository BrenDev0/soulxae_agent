from typing import Dict
from src.agent.state import State
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage
import json
from src.dependencies.container import Container
from src.agent.services.prompt_service import PromptService
import os
import httpx
from datetime import datetime, timedelta
from src.agent.nodes.agent_handoff import agent_handoff_tool


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
        prompt = f"""Let the user know youve booked their appointment and thank them for thier time. 
        Only respond in {state['chat_language']}
        """
    else:
        state["appointments_state"]["appointment_datetime"] = None

        available_slots = await get_available_slots(state)
        if available_slots:
            slots_text = "\n".join([f"{slot}" for slot in available_slots[:3]])

            prompt = f"""
            The user's requested time ({state['appointments_state']['appointment_datetime']}) is not available.
            Show them these alternative options in a conversational format:
            {slots_text}
            
            Ask them to choose one of these times or suggest a different time.
            Be helpful and friendly.Only respond in {state['chat_language']}.
            """
        else: 
            prompt = f"""
             The user's requested time ({state['appointments_state']['appointment_datetime']}) is not available.
             Ask them  to provide an alternative date and time for thier appointment.
             Be helpful and friendly. Only respond in {state['chat_language']}.
            """
    
    response = await llm.ainvoke(prompt)
    
    state["response"] = response.content.strip()

    return state

async def cancel_appointment(llm: ChatOpenAI, state: State): 
    appointment_canceled = await cancel_appointment_tool(state=state)

    if not appointment_canceled:
        await agent_handoff_tool(state=state)
        prompt = f"""
        The users appoinment was unable to be canceled.
        let them know you will tranfer the issue to a human representative that will reach out at the earliest convenience.
        Be friendly. Only respond in {state['chat_language']}.
        """        

    else: 
        prompt = f"""
        Let the user know that youve canceled thier appointment.
        Be friendly. Only respond in {state['chat_language']}.
        """
        
    response = await llm.ainvoke(prompt)

    state["response"] = response.content.strip()

    return state
        

    
async def appointment_router(state: State):
    appt = state["appointments_state"]
    if not appt.get("name") and state["intent"] == "new_appointment":
        state["next_node"] = "ask_name"
    elif not appt.get("email"):
        state["next_node"] = "ask_email"
    elif not appt.get("phone") and state["intent"] == "new_appointment":
        state["next_node"] = "ask_phone"
    elif not appt.get("appointment_datetime"):
        state["next_node"] = "ask_availability"
    else:
        if state["intent"] == "new_appointment":
            state["next_node"] = "check_availability"
        else:
            state["next_node"] = "cancel_appointment"
    return state


async def check_availability_tool(state: State) -> State:
    host = os.getenv("APP_HOST")
    token = state["token"]
    
    url = f"https://{host}/google/calendars/secure/availability/{state['calendar_id']}"
    headers = {"Authorization": f"Bearer {token}"}
    req_body = {
        "slot": state["appointments_state"]["appointment_datetime"],
        "calendarReferenceId": state["calendar_id"]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=req_body)
            response.raise_for_status()
            return response.json()["is_available"]
    except httpx.HTTPStatusError as exc:
        print(f"Availability equest failed: {exc.response.status_code} - {exc.response.text}")
        return {"error": exc.response.text, "status_code": exc.response.status_code}
    

async def create_appoinment_tool(state: State) -> State:
    host = os.getenv("APP_HOST")
    token = state["token"]
    print(state["appointments_state"]["appointment_datetime"])

    start_time_str = state["appointments_state"]["appointment_datetime"]
    start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
    end_time = start_time + timedelta(minutes=30)
    
    url = f"https://{host}/google/calendars/secure/events/{state['calendar_id']}"
    headers = {"Authorization": f"Bearer {token}"}
    
    req_body = {
        "startTime": state["appointments_state"]["appointment_datetime"],
        "endTime": end_time.isoformat(),
        "summary": f"{state['appointments_state']['name']}",
        "description": f"Phone: {state['appointments_state']['phone']}",
        "attendees": [{
            "email": state["appointments_state"]["email"]
        }]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=req_body)
            response.raise_for_status()
            return response.json()
        
    except httpx.HTTPStatusError as exc:
        print(f"Unable to create appointment: {exc.response.status_code} - {exc.response.text}")
        return {"error": exc.response.text, "status_code": exc.response.status_code}



async def cancel_appointment_tool(state: State):
    host = os.getenv("APP_HOST")
    token = state["token"]
    print(state["appointments_state"]["appointment_datetime"])
    print(state["appointments_state"]["email"])
    url = f"https://{host}/google/calendars/secure/events/{state['calendar_id']}"
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {
        "startTime": state["appointments_state"]["appointment_datetime"],
        "attendee": state["appointments_state"]["email"]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers, params=params)
            response.raise_for_status()
            return True
        
    except httpx.HTTPStatusError as exc:
        print(f"Unable to delete appointment: {exc.response.status_code} - {exc.response.text}")
        return False