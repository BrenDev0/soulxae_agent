from typing import Dict
from ..state import State
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
import json
from src.core.services.redis_service import RedisService
from src.core.dependencies.container import Container
from src.modules.prompts.prompt_service import PromptService

async def appointment_flow(llm: ChatOpenAI, state: State) -> Dict:
    current_data = {
        "name": state["appointments_state"].get("name"),
        "phone": state["appointments_state"].get("phone"),
        "email": state["appointments_state"].get("email"),
        "time": state["appointments_state"].get("time")
    }

    if not current_data["name"] or not current_data["phone"] or not current_data["email"]:
        system_message = f"""
        You are an assistant helping to schedule an appointment.
        You will receive the chat history and the user's latest message.
        Your job:
        1. Identify whether the client provided any of the following:
        - Full name
        - Email
        - Phone number
        - Preferred appointment time
        2. Extract those into structured JSON. If a value wasn't provided, use `null`.
        3. Generate a friendly response asking *only* for what is missing.
        ALWAYS respond in this format (as a single JSON object):
        {{
            "name": <string or null>,
            "email": <string or null>,
            "phone": <string or null>,
            "time": <string or null>,
            "response": <string>  // Ask only for what's missing
        }}
        Here is what we currently know:
        - Name: {current_data.get("name") or "Not provided"}
        - Phone: {current_data.get("phone") or "Not provided"}
        - Email: {current_data.get("email") or "Not provided"}
        - Appointment Time: {current_data.get("time") or "Not provided"}
        Ask the client *only* for the missing details in a clear and friendly way.
        IMPORTANT: You will always respond in the language of the input.
        """

        messages = [
            SystemMessage(system_message),
        ]

        chat_history = state.get("chat_history", [])
        
        if chat_history:
            prompt_service: PromptService = Container.resolve("promt_service")
            messages = prompt_service.add_chat_history(chat_history, messages)
        
        messages.append(HumanMessagePromptTemplate.from_template('{input}'))

        prompt = ChatPromptTemplate.from_messages(messages)

        chain = prompt | llm
        
        response = await chain.ainvoke({"input": state["input"]});
        try:
            parsed = json.loads(response.content)
        
        except json.JSONDecodeError:
            raise ValueError("LLM response was not valid JSON:\n" + response.content)

        state["appointments_state"]["name"] = parsed.get("name") or current_data["name"]
        state["appointments_state"]["email"] = parsed.get("email") or current_data["email"]
        state["appointments_state"]["phone"] = parsed.get("phone") or current_data["phone"]
        state["response"] = parsed["response"]

    redis_service: RedisService = Container.resolve("redis_service")
    await redis_service.set_session(f"conversation_state:{state['conversation_id']}", state)
    
    return state

    
    