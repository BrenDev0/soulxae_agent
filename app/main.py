from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import interact


app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

@app.get("/", response_class=JSONResponse)
async def home():
    return JSONResponse(status_code=200, content="hola");

app.include_router(interact.router)



