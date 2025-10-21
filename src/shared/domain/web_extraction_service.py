from abc import ABC, abstractmethod
from typing import List

class WebExtractionService(ABC):
    @abstractmethod
    def extract_webpage_content(
        urls: List[str]
    ):
        raise NotImplementedError