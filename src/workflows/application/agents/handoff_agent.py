from src.workflows.application.services.prompt_service import PromptService
from src.workflows.domain.services.llm_service import LlmService
from src.workflows.domain.state import State
from src.shared.utils.decorators.service_error_handler import service_error_handler

class HandoffAgent:
    __MODULE = "handoff.agent"
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    async def __get_prompt(self):
        system_message = """
        The client has requested to speak with a human representative,
        or theyve requested help in a service that you cannot provide.
        Let them  know that you will tranfer them, and an agent will be with them at the earliest convenience.
        """

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message
        )

        return prompt

    @service_error_handler(module=__MODULE)
    async def interact(self, state: State):
        prompt = await self.__get_prompt()
            
        response = await self.__llm_service.invoke(
            prompt=prompt,
            temperature=state["temperature"],
            max_tokens=state["max_tokens"]
        )

        return response