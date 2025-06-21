from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes import interact
from dependencies.container import Container
from database.sessions import get_db_session
from app.config import Config  

config = Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    await config.on_startup()  
    yield
    await config.on_shutdown() 

app = FastAPI(lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://soulxae.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interact.router)
