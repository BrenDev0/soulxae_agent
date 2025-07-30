from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.api.modules.agents import agents_routes
from src.api.modules.files import files_routes
from src.api.core.middleware.auth_middleware import auth_middleware
from src.dependencies.configure_container import configure_container

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

app.middleware("http")(auth_middleware)

app.include_router(agents_routes.router)
app.include_router(files_routes.router)
