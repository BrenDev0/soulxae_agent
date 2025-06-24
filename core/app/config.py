from core.database.sessions import get_db_session
from core.dependencies.configure_container import configure_container

class Config:
    async def on_startup():
        print("Starting up...")
        session = next(get_db_session())
        configure_container(session)

    async def on_shutdown():
        print("Shutting down...")
      
