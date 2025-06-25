from modules.tools.agent_handoff import agent_handoff
from modules.tools.make_appointment import book_appointment_with_check
from modules.tools.appointment_state import get_appointment_data, set_appointment_data

tool_registry = {
    "ee9f7c84-0a88-4bea-a6b1-e4e8dfa55c5a": agent_handoff,
    
    "a208b832-4194-4b50-9f4e-3d1619778033": book_appointment_with_check
}
