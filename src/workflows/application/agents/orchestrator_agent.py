import datetime
from zoneinfo import ZoneInfo

from src.workflows.domain.services.llm_service import LlmService
from src.workflows.application.services.prompt_service import PromptService
from src.workflows.domain.state import State
from src.workflows.domain.models import OrchestratorOutput

from src.shared.utils.decorators.service_error_handler import service_error_handler

class Orchestrator:
    __MODULE = "orchestrator.agent"
    def __init__(
        self, 
        llm_service: LlmService, 
        prompt_service: PromptService
    ):
        self.__llm_service = llm_service
        self.__prompt_service = prompt_service
    
    @service_error_handler(module=__MODULE)
    def __get_prompt(
        self,
        state: State
    ):
        now = datetime.datetime.now(tz=ZoneInfo("America/Merida")).isoformat()
        system_message = f"""
        You are an assistant for a real estate workflow. 
        Your job is to analyze the latest client response and the chat history to:

        1. Extract any information that matches the following fields:
        - Appointment Data: appointment_datetime, name, email, phone
        the current date time is:
            {now}
            use this as a reference when adding appoinment_datetime

        2. Determine the client's intent:
        - "general_query": The user is asking a general question.
        - "appointments": The user wants to book an appointment.
        - "human": The user wants to speak to a human representative.

        CURRENT STATE:
        Appointment Data: {state.get('appointment_data')}

        Instructions:
        - Only extract and return fields that are explicitly mentioned in the latest client response or chat history.
        - If no new information is found for a section, set its value to null.
        - All phone numbers should be converted to numerical format.
        - All emails must me converted correct email format.
        - Do NOT guess or invent any values.
        - Do NOT use example names, locations, or dates unless they are present in the input or chat history.
        - Use natural, concise language.
        - Do NOT use emojis or special characters.
        - For intent, always choose the most relevant option based on the client's words.
        - The "intent" field should contain one of the valid intents listed above.
        - If the intent is unclear or does not match any of the valid intents, default to "human".
        """

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            input=state['input'],
            chat_history=state['chat_history']
        )

        return prompt
    
    @service_error_handler(module=__MODULE)
    async def interact(
        self,
        state: State
    ) -> OrchestratorOutput:
        
        prompt = self.__get_prompt(state=state)

        response = await self.__llm_service.invoke_structured(
            prompt=prompt,
            response_model=OrchestratorOutput,
            temperature=state['temperature'],
            max_tokens=state['max_tokens']
        )

        return response



        

        