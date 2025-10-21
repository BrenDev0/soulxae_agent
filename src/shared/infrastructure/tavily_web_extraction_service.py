from tavily import TavilyClient
import os
from typing import List

from src.shared.domain.web_extraction_service import WebExtractionService

def get_tavily_client() -> TavilyClient:
    return TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class TavilyWebExtractionService(WebExtractionService):
    def __init__(
        self,
        client: TavilyClient
    ):
        super().__init__()

        self.__client = client

    def extract_webpage_content(self, urls: List[str]):
        response = self.__client.extract(
            urls=urls,
            format="text"
        )

        return response