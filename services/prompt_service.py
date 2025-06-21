from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from typing import List, Dict

class PromptService:
    def __init__(self, session: Session):
        self.session = session

    def build_prompt_template(
            self, 
            system_prompt: str, 
            chat_history: List[Dict]
        ): 
        messages = [
            SystemMessage(content=system_prompt),
            SystemMessage(content="IMPORTANT! you will always respond in the language of the input")
        ]
        
        for msg in chat_history:
            if msg["sender"] == "client":
                messages.append(HumanMessage(content=msg["text"]))
            elif msg["sender"] == "agent":
                messages.append(AIMessage(content=msg["text"]))
        
        messages.append(HumanMessagePromptTemplate.from_template('{input}'))

        prompt = ChatPromptTemplate.from_messages(messages)
        
        return prompt
    