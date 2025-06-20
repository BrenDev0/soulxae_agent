from langchain.tools import Tool
import httpx

async def agent_handoff(conversation_id: str, token: str) -> dict:
    url = f"https://soulxae.up.railway.app/conversations/{conversation_id}/agent-handoff?status=true"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        print(f"Agent handoff failed: {exc.response.status_code} - {exc.response.text}")
        return {"error": exc.response.text, "status_code": exc.response.status_code}


agent_handoff_tool = Tool(
    tool_id="agent_handoff",
    name="agent_handoff",
    func=agent_handoff,
    description=(
        "Use this tool if the client expresses interest in speaking to a human representative, "
        "or if a human should handle the conversation.\n\n"
        "Required arguments:\n"
        "- conversation_id (e.g. '0fb1a939-e56f-4cc6-bf64-41ecd7451459')\n"
        "- token (e.g. 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55SWQiOjE3LCJpYXQiOjE3NTAzNTM5OTIsImV4cCI6MTc1MDk1ODc5Mn0.vQXZa8qJdJVlXw6VdMCZVTEzuvsuP4_x1J1-zRp6aFE')\n\n"
        "Example usage:\n"
        "agent_handoff(conversation_id='0fb1a939-e56f-4cc6-bf64-41ecd7451459', token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55SWQiOjE3LCJpYXQiOjE3NTAzNTM5OTIsImV4cCI6MTc1MDk1ODc5Mn0.vQXZa8qJdJVlXw6VdMCZVTEzuvsuP4_x1J1-zRp6aFE')"
    )
)