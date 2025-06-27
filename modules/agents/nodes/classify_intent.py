from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from ..state import AgentState
from langchain_openai import ChatOpenAI

async def classify_intent(llm: ChatOpenAI, state: AgentState) -> Dict:
    """Classify user intent unless already in a flow."""
    if state["session_state"].get("appointment_flow"):
        return "appointment"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
         Classify the user's intent. Options: general_query, appointment, human.

         general_query is for all questions and information,
         
         if the user expresses any intrest in speaking to a human represetative your answer will be human

         if the user wants to book an appointment your answer will be appoinment
         

         Your response will always be either general_query, appointment, or human.

         do not explain your answer 
         
         """),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    response = await chain.ainvoke({"input": state["input"]})
    
    intent = response.content.lower()
    
    return intent