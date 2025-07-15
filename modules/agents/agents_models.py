from pydantic import BaseModel
from typing import List, Any
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from modules.agents.state import State



class InteractionRequest(BaseModel):
    conversation_id: str

class LLMConfig(BaseModel):
    prompt: str;
    tools: List[Any];
    max_tokens: int;
    temperature: float


# db 

Base = declarative_base()

class AgentConfig(Base):
    __tablename__ = 'ai_config'
    ai_config_id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey('agents.agent_id'))
    system_prompt = Column(Text)
    max_tokens = Column(Integer)
    temperature = Column(Float)