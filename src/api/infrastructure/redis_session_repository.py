import json
from typing import Any, Optional
from redis import Redis
import os
from dotenv import load_dotenv
from uuid import UUID
load_dotenv()

class RedisSessionRepository:
    def __init__(self):
        self.redis = Redis.from_url(url=os.getenv("REDIS_URL"))

    def set_session(self, key: str, value: Any, expire_seconds: Optional[int] = 3600) -> None:
        json_value = json.dumps(value)
        self.redis.set(key, json_value, ex=expire_seconds)

    def get_session(self, key: str) -> Optional[dict]:
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def delete_session(self, key: str) -> bool:
        return self.redis.delete(key) > 0
    
    @staticmethod
    def get_agent_state_key(chat_id: UUID):
        return f"chat_state:{chat_id}"