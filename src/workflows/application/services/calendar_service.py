from datetime import datetime
import os 
import httpx
from datetime import timedelta

from src.workflows.domain.state import State

class CalendarService:
    @classmethod
    async def get_available_slots(cls, state: State):
        host = os.getenv("APP_HOST")
        token = state["token"]
        
        url = f"https://{host}/google/calendars/secure/get-slots/{state['calendar_id']}"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "startTime": state["appointments_state"]["appointment_datetime"]
        }
      
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()["data"]
            
        except httpx.HTTPStatusError as exc:
            print(f"Request failed: {exc.response.status_code} - {exc.response.text}")
            return []
    
    @classmethod
    async def create_event(cls, state: State):
        host = os.getenv("APP_HOST")
        token = state["token"]

        start_time_str = state["appointments_state"]["appointment_datetime"]
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        end_time = start_time + timedelta(minutes=30)
        
        url = f"https://{host}/google/calendars/secure/events/{state['calendar_id']}"
        headers = {"Authorization": f"Bearer {token}"}
        
        req_body = {
            "startTime": state["appointments_state"]["appointment_datetime"],
            "endTime": end_time.isoformat(),
            "summary": f"{state['appointments_state']['name']}",
            "description": f"Phone: {state['appointments_state']['phone']}",
            "attendees": [{
                "email": state["appointments_state"]["email"]
            }]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=req_body)
                response.raise_for_status()
                return response.json()
            
        except httpx.HTTPStatusError as exc:
            print(f"Unable to create appointment: {exc.response.status_code} - {exc.response.text}")
            return {"error": exc.response.text, "status_code": exc.response.status_code}


    
    @classmethod
    async def check_availability(cls, state: State):
        host = os.getenv("APP_HOST")
        token = state["token"]
        
        url = f"https://{host}/google/calendars/secure/availability/{state['calendar_id']}"
        headers = {"Authorization": f"Bearer {token}"}
        req_body = {
            "slot": state["appointments_state"]["appointment_datetime"].isoformat(),
            "calendarReferenceId": state["calendar_id"]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=req_body)
                response.raise_for_status()
                return response.json()["is_available"]
        except httpx.HTTPStatusError as exc:
            print(f"Availability equest failed: {exc.response.status_code} - {exc.response.text}")
            return {"error": exc.response.text, "status_code": exc.response.status_code}