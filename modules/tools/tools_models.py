from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Tool(Base):
    __tablename__ = 'tools'
    tool_id = Column(String, primary_key=True)
    name = Column(String)
    

class Agent_Tool(Base):
    __tablename__ = 'ai_tools'
    agent_id = Column(String, ForeignKey('agents.agent_id'))
    tool_id = Column(String, ForeignKey('tools.tool_id'))

    __table_args__ = (
        PrimaryKeyConstraint('agent_id', 'tool_id'),
    )
    