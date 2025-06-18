from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Example(Base):
    __tablename__ = 'examples'
    example_id = Column(String, primary_key=True)
    prompt_id = Column(String, ForeignKey('tools.tool_id'))
    input = Column(Text)
    output = Column(Text)

    prompt = relationship("Tool", back_populates="examples")
