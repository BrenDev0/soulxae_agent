from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate,  AIMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from typing import List, Dict
from core.services.redis_service import RedisService

class PromptService:
    def __init__(self, session: Session, redis_service: RedisService):
        self.session = session
        self.redis_service = redis_service

    async def build_prompt_template(
            self, 
            system_prompt: str,
            conversation_id: str,
            scratch_pad: bool
        ): 

        messages = [
            SystemMessage(content=system_prompt),
            SystemMessage(content="IMPORTANT! you will always respond in the language of the input")
        ]

        chat_history = await self.redis_service.get_session(f"conversation:{conversation_id}")
        
        if chat_history:
            for msg in chat_history:
                if msg["sender"] == "client":
                    messages.append(HumanMessage(content=msg["text"]))
                elif msg["sender"] == "agent":
                    messages.append(AIMessage(content=msg["text"]))
        
        messages.append(HumanMessagePromptTemplate.from_template('{input}'))
        
        if scratch_pad:
            messages.append(AIMessagePromptTemplate.from_template('{agent_scratchpad}'))

        prompt = ChatPromptTemplate.from_messages(messages)
        
        return prompt
    