from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import Generator

DB_URL = os.getenv("DATABASE_URL")
print(DB_URL)
engine = create_engine(DB_URL, pool_pre_ping=True)  
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
