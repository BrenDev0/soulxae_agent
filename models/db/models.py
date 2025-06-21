from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Tool(Base):
    __tablename__ = 'tools'
    tool_id = Column(String, primary_key=True)
    name = Column(String)
    

    examples = relationship("Example", back_populates="Tool")


class Agent(Base):
    __tablename__ = 'agents'
    agent_id = Column(String, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    user_id = Column(String, ForeignKey('users.user_id'))
    system_prompt = Column(Text)
    greeting_message = Column(Text)
    max_tokens = Column(Integer)
    temperature = Column(Float)

class Agent_Tool(Base):
    __tablename__ = 'agent_tools'
    agent_id = Column(String, ForeignKey('agents.agent_id'))
    tool_id = Column(String, ForeignKey('tools.tool_id'))

    __table_args__ = (
        PrimaryKeyConstraint('agent_id', 'tool_id'),
    )
    


    
