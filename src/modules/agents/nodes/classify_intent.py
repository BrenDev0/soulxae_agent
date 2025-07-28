from typing import Dict
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from ..state import State
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from src.modules.prompts.prompt_service import PromptService
from src.core.dependencies.container import Container

async def classify_intent(llm: ChatOpenAI, state: State) -> Dict:
    system_message = """
        Classify the user's intent. Options: general_query, appointment, human.

        use the context of the conversation to guide your desicion,

        general_query is for all questions and information,
        
        if the user expresses any intrest in speaking to a human represetative your answer will be human

        if the user wants to book an appointment your answer will be appointment
        
        Your response will always be either general_query, appointment, or human.

        do not explain your answer 
    
    """

    messages = [
        SystemMessage(content=system_message),
    ]

    chat_history = state.get("chat_history", [])
    if chat_history:
        prompt_service: PromptService = Container.resolve("prompt_service")
        messages = prompt_service.add_chat_history(chat_history, messages)
    
    messages.append(HumanMessagePromptTemplate.from_template('{input}'))

    prompt = ChatPromptTemplate.from_messages(messages)
    
    chain = prompt | llm
    response = await chain.ainvoke({"input": state["input"]})
    intent = response.content.strip().lower()

    valid_intents = {"general_query", "appointment", "human"}

    if intent not in valid_intents:
        intent = "human"  #  fall back

    state["intent"] = intent
    
    return state