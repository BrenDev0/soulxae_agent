from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph import Graph
from src.core.services.redis_service import RedisService
from langchain_openai import ChatOpenAI

class Agent:
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.5
        )

    workflow = Graph()

    

    
    

    
