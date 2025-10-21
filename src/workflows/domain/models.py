from pydantic import BaseModel
from src.workflows.domain.state import AppointmentState

class OrchestratorOutput(BaseModel):
    appointment_data: AppointmentState
    intent: str 