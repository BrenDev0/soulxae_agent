from fastapi import Depends
import os

from src.workflows.domain.services.llm_service import LlmService
from src.shared.domain.embedding_service import EmbeddingService
from src.shared.domain.vector_repository import VectorRepository
from src.shared.dependencies.dependencies import get_embedding_service, get_vector_repository

from src.workflows.application.services.prompt_service import PromptService
from src.workflows.application.use_cases.search_for_context import SearchForContext
from src.workflows.application.agents.appoinments_agent import AppointmentsAgent
from src.workflows.application.agents.general_query_agent import GeneralQueryAgent
from src.workflows.application.agents.orchestrator_agent import Orchestrator
from src.workflows.application.agents.handoff_agent import HandoffAgent

from src.workflows.infrastructure.langchain_llm_service import LangchainLlmService



def get_llm_service() -> LlmService:
    return LangchainLlmService()


def get_prompt_service() -> PromptService:
    return PromptService()

def get_search_for_context_use_case(
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_repository: VectorRepository = Depends(get_vector_repository)
) -> SearchForContext:
    return SearchForContext(
        embedding_service=embedding_service,
        vector_repository=vector_repository
    )

def get_appointments_agent(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service)
) -> AppointmentsAgent:
    return AppointmentsAgent(
        llm_service=llm_service,
        prompt_service=prompt_service
    )

def get_general_query_agent(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service),
    search_for_context: SearchForContext = Depends(get_search_for_context_use_case)
) -> GeneralQueryAgent:
    return GeneralQueryAgent(
        llm_service=llm_service,
        prompt_service=prompt_service,
        search_for_context=search_for_context
    )

def get_orchestrator(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> Orchestrator:
    return Orchestrator(
        llm_service=llm_service,
        prompt_service=prompt_service,
    )


def get_handoff_agent(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> HandoffAgent:
    return HandoffAgent(
        llm_service=llm_service,
        prompt_service=prompt_service,
    )
