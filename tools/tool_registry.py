from tools.agent_handoff import agent_handoff

tool_registry = {
    "uuidoftool": {
        "handler": agent_handoff,
        "description": "User has requested or expressed interest in speaking to a human representative"
    }
}
