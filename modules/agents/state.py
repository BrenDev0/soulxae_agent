from typing import Annotated, Optional
from typing_extensions import TypedDict
from datetime import datetime

class AppointmentState(TypedDict):
    step: str;
    name: str;
    email: str;
    phone: str;
    appointment_datetime: datetime;

class State(TypedDict):
    input: str;
    session_id: str;
    appointment_flow: bool;
    appointments_state: AppointmentState;
    response: Optional[str];