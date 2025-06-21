from dependencies.container import Container
from database.sessions import get_db_session
from dependencies.configure_container import configure_container
from services.tools_service import ToolsService

class Config:
    async def on_startup():
        print("Starting up...")
        session = next(get_db_session())
        configure_container(session)
        
        tools_service: ToolsService = Container.resolve("tools_service")
        await tools_service.configure_tools()

    async def on_shutdown():
        print("Shutting down...")
      
