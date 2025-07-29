from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate,  AIMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from typing import List, Dict, Any
from src.core.services.redis_service import RedisService
from src.modules.embeddings.embedding_service import EmbeddingService
from src.modules.agents.state import State

class PromptService:
    def __init__(self, embedding_service: EmbeddingService, redis_service: RedisService):
        self.embedding_service = embedding_service
        self.redis_service = redis_service

    def classify_intent_prompt_template(
        self, 
        state: State
    ):
        system_message = """
            Classify the user's intent and determine their language. Intent options: "general_query", "appointment", "human".
            Use the context of the conversation to guide your decision:
            - "general_query" is for all types of questions and information.
            - If the user expresses any interest in speaking to a human representative, the intent will be "human".
            - If the user wants to book an appointment, the intent will be "appointment".
            Your response should always be like the example below:
            {
                "language": "spanish",
                "intent": "human"
            }
            Do not explain your answer.

        """

        messages = [
            SystemMessage(content=system_message),
        ]

        chat_history = state.get("chat_history", [])
        if chat_history:
            messages = self.add_chat_history(chat_history, messages)
        
        messages.append(HumanMessagePromptTemplate.from_template('{input}'))

        prompt = ChatPromptTemplate.from_messages(messages)
        
        return prompt

    async def general_query_prompt_template(
            self, 
            state: State
        ): 

        messages = [
            SystemMessage(content=state["system_message"]),
            SystemMessage(content="IMPORTANT! you will always respond in the language of the input")
        ]

        context = await self.embedding_service.search_for_context(
            input=state["input"],
            agent_id=state["agent_id"],
            user_id=state["user_id"]
        )
 
        if context:
            print(context)
            messages.append(SystemMessage(content=f"""
                You have access to the following relevant context retrieved from documents. Use this information to inform your response. Do not make up facts outside of this context.

                Relevant context:
                {context}
            """))

        chat_history = state.get("chat_history", [])
        
        if chat_history:
            messages = self.add_chat_history(chat_history, messages)
        
        messages.append(HumanMessagePromptTemplate.from_template('{input}'))

        prompt = ChatPromptTemplate.from_messages(messages)
        
        return prompt
    
    def appointment_data_extraction_prompt(self, state: State):
        messages = [
        SystemMessage("""
                From the chat history and latest message, extract available data for:

                - name
                - email
                - phone
                - appointment_datetime

                Do not ask for any information.
                Respond only in this format:
                {
                "name": "...",
                "email": "...",
                "phone": "...",
                "appointment_datetime": "..."
                }
                If anything is missing, return null for that field.
            """)
        ]
    
        chat_history = state.get("chat_history", [])
        
        if chat_history:
            messages = self.add_chat_history(chat_history, messages)

    
        messages.append(HumanMessagePromptTemplate.from_template('{input}'))

        prompt = ChatPromptTemplate.from_messages(messages)
        
        return prompt
    
    @staticmethod
    def add_chat_history(chat_history: List[Dict], messages: List[Any]) -> List[Any]:
        for msg in chat_history:
            if msg["sender"] == "client":
                messages.append(HumanMessage(content=msg["text"]))
            elif msg["sender"] == "agent":
                messages.append(AIMessage(content=msg["text"]))

        return messages
    
    