from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import interact
from dependencies.container import Container
from database.sessions import get_db_session


app = FastAPI()

origins = [
    "http://localhost:3000",
    "soulxae.up.railway.app"
]
session = get_db_session()

Container = Container(db_session=session)
Container.tools_service.configure_tools()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

app.include_router(interact.router)



