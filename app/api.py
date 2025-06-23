from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes import interact, files
from middleware.auth_middleware import auth_middleware
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

app.middleware("http")(auth_middleware)

app.include_router(interact.router)
app.include_router(files.router)
