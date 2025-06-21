from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import List, Dict

class PromptService:
    def __init__(self, session: Session, redis_service):
        self.session = session
        self.redis_service = redis_service 

    def build_prompt_template(
            self, 
            system_prompt: str, 
            chat_history: List[Dict]
        ): 
        messages = [
            SystemMessagePromptTemplate(prompt=system_prompt),
            SystemMessagePromptTemplate(prompt="IMPORTANT! you will always respond in the language of the input")
        ]
        
        for msg in chat_history:
            if msg["sender"] == "client":
                messages.append(HumanMessagePromptTemplate(prompt=msg["text"]))
            elif msg["sender"] == "agent":
                messages.append(SystemMessagePromptTemplate(prompt=msg["text"]))
        
        messages.append(HumanMessagePromptTemplate.from_template('{input}'))

        prompt = ChatPromptTemplate.from_messages(messages)
        
        return prompt
    