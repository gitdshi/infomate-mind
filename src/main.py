from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ollama import AsyncClient
from dotenv import load_dotenv
import os
import json

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

@app.get("/stream")
async def stream(model: str, message: str):
    client = AsyncClient(
        host=os.getenv('OLLAMA_HOST')
    )
    async def messageStream(model: str, message: str):
        message = {'role': 'user', 'content': message}
        async for part in await client.chat(model=model, messages=[message], stream=True):
            yield json.dumps({"content": part['message']['content']}).encode('utf-8')

    return StreamingResponse(messageStream(model, message), media_type="application/json")
