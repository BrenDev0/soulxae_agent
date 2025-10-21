from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.api.interface.routes import agents_routes
from src.api.interface.routes import knowledge_base_routes
from src.shared.dependencies.configure_container import configure_container

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_container()  
    yield

app = FastAPI(lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://soulxae.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(agents_routes.router)
app.include_router(knowledge_base_routes.router)
