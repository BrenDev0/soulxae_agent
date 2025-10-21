import datetime
from zoneinfo import ZoneInfo

from src.workflows.domain.services.llm_service import LlmService
from src.workflows.application.services.prompt_service import PromptService
from src.shared.utils.decorators.service_error_handler import service_error_handler
from src.workflows.domain.state import State
from src.workflows.application.services.calendar_service import CalendarService

class AppointmentsAgent:
    __MODULE = "appointments.agent"
    
    def __init__(
        self, 
        llm_service: LlmService,
        prompt_service: PromptService
    ):
        self.__llm_service = llm_service
        self.__prompt_service = prompt_service

    def __get_prompt_data_collection(
        self, 
        state: State
    ) -> str:
        missing_data = [key for key, value in state["appointments_state"].items() if value is None]
        now = datetime.datetime.now(tz=ZoneInfo("America/Merida")).isoformat()
        system_message = f"""
        You are a personal data collector speaking with a client on a phone call to book thier appointment.
        Your job is to interact in a calm, friendly, and natural conversational tone, collecting any missing data needed for the appointment.

        The data that you will be collecting:
        name - the clients full name
        email - the clients email address  
        phone - the clients phone number
        appointment_datetime datestring

        the current date time is:
            {now}
            use this as a reference when adding appoinment_datetime

        This data is required for making appointments and for any information they client may be request, and to best help the client with thier needs.

        The missing data that you need to request:
        {missing_data}
        
        IMPORTANT:
        - you will not ask for a datetime untill all other fields are filled.
        - Personalize each response using information from the chat history and user input.
        - DO NOT repeat greetings, opening phrases, or explanations already used in the conversation.
        - Avoid robotic or scripted language; respond as a real person would on a phone call.
        - If the client asks why data is needed, explain briefly and naturally.
        - If you already have a piece of data, do not ask for it again.
        - Vary your language and sentence structure; do not start every response the same way.
        - Use context from previous exchanges to make the conversation flow smoothly.

        Remember:
        - Be friendly and conversational.
        - Do not repeat yourself.
        - Use the chat history to avoid redundancy.
        """
    
        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            chat_history=state["chat_history"],
            input=state["input"]
        )

        return prompt
    

    def __get_prompt_unavailible(
        self, 
        slots,
        state: State
    ) -> str:
        
        slots_text = "\n".join([f"{slot}" for slot in slots[:3]])
        system_message = f"""
        You are on a phone call with a client whose making an appoinmnet but the date they have requested is unavailbale.
        Ask the client for another date time for the appoinment

        Show them these alternative options in a conversational format:
            {slots_text}
        """
    
        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            chat_history=state["chat_history"],
            input=state["input"]
        )

        return prompt
    

    def __get_prompt_confirmation(
        self, 
        state: State
    ) -> str:
        system_message = f"""
        You are on a phone call with a client whose making an appoinmnet please let the client know that thier appointment hase been made.
        Thank the client for thier time and ask if there is anything else you can be of help with.
        """
    
        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            chat_history=state["chat_history"],
            input=state["input"]
        )

        return prompt

    @service_error_handler(module=__MODULE)
    async def interact(
        self,
        state: State,
    ):
        appointments_state = state["appointments_state"]
        if appointments_state["appointment_datetime"]:
            available = await CalendarService.check_availability(state=state)
            if available:
                prompt = self.__get_prompt_confirmation(
                    state=state
                )

                await CalendarService.create_event(state=state)
            else: 
                slots = await CalendarService.get_available_slots(state=state)
                prompt = self.__get_prompt_unavailible(
                    slots=slots,
                    state=state
                )
                state["appointments_state"]["appointment_datetime"] = None
        else: 
            prompt = self.__get_prompt_data_collection(
                state=state
            )
             

        response = await self.__llm_service.invoke(
            prompt=prompt,
            temperature=state["temperature"],
            max_tokens=state["max_tokens"]
        )

        return response