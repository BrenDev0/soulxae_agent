from langchain.tools import tool
from datetime import datetime
import httpx

@tool
async def book_appointment_with_check(
    token: str, 
    name: str, 
    email: str, 
    phone: str, 
    appointment_datetime: datetime
) -> dict:
    """
    Use this tool only after all required data has been collected:
    name, email, phone, and appointment_datetime.

    This will check availability and then book the appointment if the time is available.
    If unavailable, inform the user and ask for a new appointment_datetime.

    Reminder: always use `get_data` to check for existing inputs and `set_data` to store new ones.

    Always follow this logic:

    Call get_data to see what is already saved.

    Ask the user for any missing values (name, email, phone, appointment_datetime).

    When the user provides a value, call set_data to save it.

    Once all values are collected, call book_appointment_with_check.

    If the time is unavailable, ask the user for a new appointment time and repeat.
    """
    headers = {"Authorization": f"Bearer {token}"}
    
     # Step 1: Check availability
    check_url = "https://soulxae.up.railway.app/calendars/availability"
    check_payload = {"appointment_datetime": appointment_datetime.isoformat()}

    try:
        async with httpx.AsyncClient() as client:
            check_res = await client.post(check_url, headers=headers, json=check_payload)
            check_res.raise_for_status()
            check_data = check_res.json()

            if not check_data.get("success") or not check_data.get("isavailable", False):
                return {"status": "unavailable", "message": "This time slot is not available."}

            # Step 2: Make the appointment
            book_url = "https://soulxae.up.railway.app/calendars/events"
            book_payload = {
                "name": name,
                "email": email,
                "phone": phone,
                "appointment_datetime": appointment_datetime.isoformat()
            }
            book_res = await client.post(book_url, headers=headers, json=book_payload)
            book_res.raise_for_status()
            return book_res.json()

    except httpx.HTTPStatusError as exc:
        return {
            "error": exc.response.text,
            "status_code": exc.response.status_code
        }
