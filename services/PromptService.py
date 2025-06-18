from sqlalchemy.orm import Session
from langchain_core.prompts import FewShotPromptTemplate, ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from models.db.tool import Tool
from models.db.example import Example

class PromptService:
    def __init__(self, session: Session):
        self.session = session

    def get_few_shot_prompt(self, tool_id: str) -> str:
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

        return few_shot_prompt.format()
        

    def get_examples(self, prompt_id: str):
        examples = self.session.query(Example).filter_by(prompt_id=prompt_id).all()

        return [
            {'input': example.input, 'output': example.output} for example in examples
        ]


    def build_prompt_template(self, main_prompt_id: str, system_prompt: str): 
        main_prompt = self.get_few_shot_prompt(main_prompt_id)

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            SystemMessagePromptTemplate.from_template(main_prompt),
            HumanMessagePromptTemplate.from_template('{input}')
        ])
        
        return prompt
    