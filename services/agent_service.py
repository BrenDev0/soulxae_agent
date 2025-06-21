from services.embedding_service import EmbeddingService
from services.prompt_service import PromptService
from services.redis_service import RedisService
from services.tools_service import ToolsService
from models.db.models import Agent
from models.models import LLMConfig
from typing import List
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent

class AgentService:
    def __init__(
            self, 
            session: Session, 
            embeddings_service: EmbeddingService, 
            prompt_service: PromptService, 
            redis_service: RedisService,
            tools_service : ToolsService
        ):
        self.session = session
        self.embeddings_service = embeddings_service
        self.prompt_service = prompt_service
        self.redis_service = redis_service
        self.tools_service = tools_service
    
    
    async def get_config(self, agent_id: str, conversation_id: str, token: str, input: str) -> LLMConfig:
        agent = self.session.query(Agent).filter_by(agent_id=agent_id).first()
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found.")
        
        tools_needed = await self.embeddings_service.search_tool(input)
        print(f"🔍 Tools needed for input: {tools_needed}")

        
        agent_tools = self.tools_service.get_agents_tools(agent_id=agent_id)
        print(f"🔍 agents tools: {agent_tools}")

        tool_ids = []
        tools_for_model = []
        if len(tools_needed) != 0:
            for tool_id in tools_needed:
                if tool_id in agent_tools:
                    tool_ids.append(tool_id)
        
        if len(tool_ids) != 0:
            tools_for_model = self.tools_service.get_tools_for_model(
                tool_ids=tool_ids,
                conversation_id=conversation_id,
                token=token
            )
                    

        chat_history = await self.redis_service.get_session(f"conversation:{conversation_id}")

        prompt = self.prompt_service.build_prompt_template(
            system_prompt=agent.system_prompt, 
            chat_history=chat_history
        )

        return {
            "prompt": prompt,
            "tools": tools_for_model,
            "max_tokens": agent.max_tokens,
            "temperature": agent.temperature
        }
    
    async def interact(self, agent_id: str, conversation_id: str, token: str, input: str):
        config = await self.get_config(
            agent_id=agent_id,
            conversation_id=conversation_id,
            input=input,
            token=token
        )
        print(config["prompt"])
        print(config["tools"])

        prompt_template = config["prompt"]
        tools = config["tools"]
        formatted_messages = prompt_template.format_messages(input=input)

        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            timeout=None,
            max_retries=2
        )

        if tools:
            agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt_template)
            executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            response = await executor.ainvoke({"input": input})
        else:
            response = await llm.ainvoke(formatted_messages)

        return response["output"] if tools else response.content





        