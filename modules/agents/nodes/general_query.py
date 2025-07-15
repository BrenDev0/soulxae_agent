from typing import Dict
from ..state import State
from langchain_openai import ChatOpenAI
from core.dependencies.container import Container
from modules.prompts.prompt_service import PromptService

async def general_query(llm: ChatOpenAI, state: State) -> Dict:
    prompt_service: PromptService = Container.resolve("prompt_service")

    prompt =await  prompt_service.general_query_prompt_template(
        state=state
    )

    chain = prompt | llm

    response = await chain.ainvoke({"input": state["input"]})

    state["response"] = response.content.strip().lower()

    return state