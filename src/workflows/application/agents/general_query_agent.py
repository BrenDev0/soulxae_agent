from src.workflows.application.services.prompt_service import PromptService
from src.workflows.domain.services.llm_service import LlmService
from src.workflows.domain.state import State
from src.workflows.application.use_cases.search_for_context import SearchForContext
from src.shared.utils.decorators.service_error_handler import service_error_handler

class GeneralQueryAgent:
    __MODULE = "general_query.agent"
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService,
        search_for_context: SearchForContext
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__search_for_context = search_for_context

    async def __get_prompt(self, state: State):
        collection_name = f"user_{state['user_id']}_agent_{state['agent_id']}"

        context = await self.__search_for_context.execute(
            input=state["input"],
            namespace=collection_name
        )

        prompt = self.__prompt_service.build_prompt(
            system_message=state["system_message"],
            input=state["input"],
            chat_history=state["chat_history"],
            context=context
        )

        return prompt

    @service_error_handler(module=__MODULE)
    async def interact(self, state: State):
        prompt = await self.__get_prompt(state)
            
        response = await self.__llm_service.invoke(
            prompt=prompt,
            temperature=state["temperature"],
            max_tokens=state["max_tokens"]
        )

        return response