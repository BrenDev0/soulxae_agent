from typing import Dict
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from ..state import State
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from src.modules.prompts.prompt_service import PromptService
from src.core.dependencies.container import Container

async def classify_intent(llm: ChatOpenAI, state: State) -> Dict:
    
    prompt_service: PromptService = Container("prompt_service")
    prompt = prompt_service.classify_intent_prompt_template(state=state)
    
    chain = prompt | llm
    response = await chain.ainvoke({"input": state["input"]})
    intent = response.content.strip().lower()

    valid_intents = {"general_query", "appointment", "human"}

    if intent not in valid_intents:
        intent = "human"  #  fall back

    state["intent"] = intent
    
    return state