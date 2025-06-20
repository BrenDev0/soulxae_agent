from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from routes import interact
from dependencies.container import Container
from database.sessions import get_db_session
from app.main import Main  

load_dotenv()

session = next(get_db_session())
Container = Container(db_session=session)
main_app = Main(container=Container)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await main_app.on_startup()  
    yield
    await main_app.on_shutdown() 

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
