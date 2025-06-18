from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

class SessionService:
    def __init__(self):
        self.DB_URL = os.getenv("DB_URL")
        self.engine = create_engine(self.DB_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()
