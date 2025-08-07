from typing import Dict
from ..state import State
from langchain_openai import ChatOpenAI
from src.agent.services.prompt_service import PromptService
from src.dependencies.container import Container
import json

async def classify_intent(llm: ChatOpenAI, state: State) -> Dict:
    prompt_service: PromptService = Container.resolve("prompt_service")
    prompt = prompt_service.classify_intent_prompt_template(state=state)
    
    chain = prompt | llm
    response = await chain.ainvoke({"input": state["input"]})
    print(response.content)
    data = json.loads(response.content)

    langauge = data.get("language", None)
    
    intent = data.get("intent", None)
    if intent:
        valid_intents = {"general_query", "new_appointment", "cancel_appointment", "human"}
        if intent not in valid_intents:
            intent = "human"  
    else: 
        intent= "human"
    
    language = data.get("language", None)
    if language:
        state["chat_language"] = langauge
    else: state["chat_language"] = "spanish"
    
    state["intent"] = intent
    
    return state