import httpx

from src.workflows.domain.state import State
from src.api.domain.session_repository import SessionRepository
from fastapi import BackgroundTasks
from src.api.domain.agents_models import InteractionRequest


class AgentController:
    def __init__(self, session_repo: SessionRepository,):
        self.__session_repository = session_repo

    async def interact(
        self,
        data: InteractionRequest,
        graph,
        background_tasks: BackgroundTasks
    ): 
        # use only when meta is connected
        state = State(
            system_message=data.system_message,
            calendar_id=data.calendar_id,
            max_tokens=data.max_tokens,
            temperature=data.temperature,
            input=data.input,
            user_id=data.user_id,
            agent_id=data.agent_id,
            conversation_id=data.conversation_id,
            token=data.token,
            appointments_state=data.appointments_state,
            chat_history=data.chat_history,
            response="",
            intent=""
        )
        background_tasks.add_task(self.hanlde_interaction, state, graph)
        
        return 

        ## only for testing 
        # final_state: State = await graph.ainvoke(state)
        # background_tasks.add_task(self.handle_state, final_state)

        # return { "data": final_state["response"]}



    async def hanlde_interaction(self, state: State, graph):
        print(state, "state::::::::interaction")
        final_state: State = await graph.ainvoke(state)

        await self.__send_message(final_state["response"], state["token"], state["conversation_id"])

        self.handle_state(final_state)
    

    def handle_state(self, state: State, chat_history_limit: int = 8):
        human_message = {
            "sender": "client",
            "text": state["input"]
        }
        ai_message = {
            "sender": "agent",
            "text": state["response"]
        }

        chat_history = state["chat_history"]

        chat_history.insert(0, human_message)
        if len(chat_history) > chat_history_limit:
            chat_history.pop()  

        chat_history.insert(0, ai_message)
        if len(chat_history) > chat_history_limit:
            chat_history.pop()  

        self.__session_repository.set_session(f"conversation_state:{state['conversation_id']}", state)



    @staticmethod
    async def __send_message(text: str, token: str, conversation_id: str): 
        url = f"https://soulxae.up.railway.app/direct/secure/send"
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "conversationId": conversation_id,
            "type": "text",
            "text": text
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, data=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            print(f"Unable to send message: {exc.response.status_code} - {exc.response.text}")
            return {"error": exc.response.text, "status_code": exc.response.status_code}


    
    