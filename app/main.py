from dependencies.container import Container
class Main:
    def __init__(self, container: Container):
        self.container = container

    async def on_startup(self):
        print("Starting up...")
        await self.container.tools_service.configure_tools()

    async def on_shutdown(self):
        print("Shutting down...")
      
