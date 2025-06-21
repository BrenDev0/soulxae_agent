from langchain.tools import tool
from datetime import datetime
from models.models import AppointmentPayload
import httpx
from dependencies.container import Container
from services.redis_service import RedisService


@tool
async def get_data(conversation_id: str) -> dict:
    """
    Use this tool first before making or checking any appointments.

    This retrieves the current session data for the user. 
    Check what has already been collected (name, email, phone, start_time)
    before asking the user for more information.
    """
    redis_service: RedisService = Container.resolve("redis_service")
    session = redis_service.get_session(f"data_session:{conversation_id}")
    return session or {}


@tool
async def set_data(conversation_id: str, key: str, value: str) -> dict:
    """
    Use this tool every time the user provides new appointment information.

    This saves one piece of information (e.g., name, email, phone, or start_time)
    in the session data. Call this tool immediately after the user responds with 
    any missing data.
    """
    redis_service: RedisService = Container.resolve("redis_service")
    session = redis_service.get_session(f"data_session:{conversation_id}") or {}
    session[key] = value
    redis_service.set_session(f"data_session:{conversation_id}", session)
    return session

    
