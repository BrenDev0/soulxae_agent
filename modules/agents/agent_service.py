from modules.embeddings.embedding_service import EmbeddingService
from modules.prompts.prompt_service import PromptService
from core.services.redis_service import RedisService
from modules.tools.tools_service import ToolsService
from modules.agents.agents_models import AgentConfig
from modules.agents.agents_models import LLMConfig
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from modules.messaging.messaging_service import MessagingService

class AgentService:
    def __init__(
            self, 
            session: Session, 
            embeddings_service: EmbeddingService, 
            prompt_service: PromptService, 
            redis_service: RedisService,
            tools_service : ToolsService,
            messaging_service: MessagingService
        ):
        self.session = session
        self.embeddings_service = embeddings_service
        self.prompt_service = prompt_service
        self.redis_service = redis_service
        self.tools_service = tools_service
        self.messaging_service = messaging_service
    
    
    async def get_config(self, agent_id: str, conversation_id: str, user_id: str) -> LLMConfig:
        agent_config = self.session.query(AgentConfig).filter_by(agent_id=agent_id).first()
        if not agent_config:
            raise ValueError(f"Agent config with  agetn ID {agent_id} not found.")
          
        agent_tools = self.tools_service.get_agents_tools(
            agent_id=agent_id,
            conversation_id=conversation_id,
            user_id=user_id
        )

        scratch_pad_needed = bool(agent_tools)

        prompt = await self.prompt_service.build_prompt_template(
            system_prompt=agent_config.system_prompt,
            conversation_id=conversation_id,
            scratch_pad=scratch_pad_needed
        )

        return {
            "prompt": prompt,
            "tools": agent_tools,
            "max_tokens": agent_config.max_tokens,
            "temperature": agent_config.temperature
        }
    
    async def interact(self, agent_id: str, conversation_id: str, user_id: str, input: str):
        print(agent_id),
        print(conversation_id)
        print(user_id)
        print(input)
        config = await self.get_config(
            agent_id=agent_id,
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        prompt_template = config["prompt"]
        tools = config["tools"]
        print(tools)

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
            
            response = await executor.ainvoke({
                "input": input,  
                "agent_scratchpad": ""  
            })
        else:
            formatted_messages = prompt_template.format(input=input)
            response = await llm.ainvoke(formatted_messages)

        try:
            await self.messaging_service.send_message(
                conversation_id=conversation_id,
                user_id=user_id,
                text=response["output"] if tools else response.content
            ) 
        except Exception as e:
            print(e)
            raise
        return

        