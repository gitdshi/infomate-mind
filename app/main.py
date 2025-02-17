from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ollama, anything, nextcloud
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Hello World, Infomate Mind is running!"}

app.include_router(ollama.router)
app.include_router(anything.router)
app.include_router(nextcloud.router)
