from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

class SessionRepository(ABC):
    @abstractmethod
    def set_session(self, key: str, value: str, expire_seconds: Optional[int] = 3600) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_session(self, key: str) -> Optional[dict]:
        raise NotImplementedError
    
    @abstractmethod
    def delete_session(self, key: str) -> bool:
        raise NotImplementedError
    
  