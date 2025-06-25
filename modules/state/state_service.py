from core.services.redis_service import RedisService
from modules.state.state_model import ConversationState, AppoinmentsState
from langchain.tools import StructuredTool

class StateService:
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service

    def get_conversation_state(self, conversation_id: str):
        key = f"conversation_state:{conversation_id}"
        
        state = self.redis_service.get_session(key)
        if state:
            return ConversationState.model_validate_json(state);

        return None

    def get_appointment_state(self, conversation_id: str):
        key = f"conversation_state:{conversation_id}"
        
        state = self.redis_service.get_session(key)
        if state:
            return AppoinmentsState.model_validate_json(state);

        return None
        
    
    def set_appointment_state(self, conversation_id: str, appointment_state: AppoinmentsState):
        key = f"appointment_state:{conversation_id}"
        self.redis_service.set_session(key, appointment_state.model_dump_json())
