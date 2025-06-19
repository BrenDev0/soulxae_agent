from sqlalchemy.orm import Session
from langchain_core.prompts import FewShotPromptTemplate, ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from models.db.models import Tool
from models.db.models import Example
from typing import List, Optional, Dict
from ..dependencies.container import redis_service

class PromptService:
    def __init__(self, session: Session):
        self.session = session
        self.redis_service = redis_service 

    def get_few_shot_prompt(self, tool_ids: List[str]) -> str:
        prompts = []

        for tool_id in tool_ids:    
            prompt = self.session.query(Tool).filter_by(tool_id=tool_id).first()
            examples = self.get_examples(tool_id=tool_id)

            example_prompt = PromptTemplate(
                input_variables=["input", "output"],
                template="human: {input}\nai: {output}"
            )

            few_shot_prompt = FewShotPromptTemplate(
                prefix=prompt.content,
                examples=examples,
                example_prompt=example_prompt
            )

            prompts.append(few_shot_prompt.format())

        return "\n\n".join(prompts)
        

    def get_examples(self, prompt_id: str):
        examples = self.session.query(Example).filter_by(prompt_id=prompt_id).all()

        return [
            {'input': example.input, 'output': example.output} for example in examples
        ]


    def build_prompt_template(self, system_prompt: str, chat_history: List[Dict], tool_ids: Optional[List[str]] = None): 
        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
        ]
        
        if tool_ids:
            messages.append(self.get_few_shot_prompt(tool_ids=tool_ids))

        for msg in chat_history:
            if msg["sender"] == "client":
                messages.append(HumanMessagePromptTemplate(msg["text"]))
            elif msg["sender"] == "agent":
                messages.append(SystemMessagePromptTemplate(msg["text"]))
        
        messages.append(HumanMessagePromptTemplate.from_template('{input}'))

        prompt = ChatPromptTemplate.from_messages(messages)
        
        return prompt
    