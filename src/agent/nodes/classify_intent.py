from typing import Dict
from ..state import State
from langchain_openai import ChatOpenAI
from src.agent.services.prompt_service import PromptService
from src.dependencies.container import Container
import json
from pydantic import BaseModel, Field

class ClassifyIntentOutput(BaseModel):
    language: str = Field(
        ...,
        description="The language detected from the user's message, e.g., 'spanish', 'english', etc."
    )
    intent: str = Field(
        ...,
        description=(
            "The classified intent of the user's message. "
            "Possible values: 'general_query' (for general questions), "
            "'new_appointment' (to book an appointment), "
            "'cancel_appointment' (to cancel an appointment), "
            "or 'human' (if the user requests a human representative)."
        )
    )

async def classify_intent(llm: ChatOpenAI, state: State) -> Dict:
    prompt_service: PromptService = Container.resolve("prompt_service")
    prompt = prompt_service.classify_intent_prompt_template(state=state)
    
    llm = llm.with_structured_output(ClassifyIntentOutput)
    chain = prompt | llm
    response = await chain.ainvoke({"input": state["input"]})
   
    intent = response.intent
    
    if intent:
        valid_intents = {"general_query", "new_appointment", "cancel_appointment", "human"}
        if intent not in valid_intents:
            intent = "human"  
    else: 
        intent = "human"
    
    if (intent == "new_appointment" or intent == "cancel_appointment") and not state.get("calendar_id"):
        intent = "human"
        
    language = response.language
    if language:
        state["chat_language"] = language
    else:
        state["chat_language"] = "spanish"
    
    state["intent"] = intent
    
    return state