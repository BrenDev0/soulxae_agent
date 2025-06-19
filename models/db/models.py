from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Tool(Base):
    __tablename__ = 'tools'
    tool_id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(Text)
    prompt = Column(Text)

    examples = relationship("Example", back_populates="Tool")

class Example(Base):
    __tablename__ = 'examples'
    example_id = Column(String, primary_key=True)
    prompt_id = Column(String, ForeignKey('tools.tool_id'))
    input = Column(Text)
    output = Column(Text)

    prompt = relationship("Tool", back_populates="examples")

class Agent(Base):
    __tablename__ = 'agents'
    agent_id = Column(String, primary_key=True)
    system_prompt = Column(Text)
    max_tokens = Column(Integer)
    temperature = Column(Float)
    user_id = Column(Text)

class Agent_tool(Base):
    __tablename__ = 'agent_tools'
    
