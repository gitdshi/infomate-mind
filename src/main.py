from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ollama import chat
from ollama import ChatResponse
import asyncio
from ollama import AsyncClient

app = FastAPI()

@app.get("/")
async def root():
    # response = send_message_to_ollama("hello")
    return {"message": "Hello World"}


@app.get("/stream")
async def stream_message(message: str):
    client = AsyncClient(
        host='http://localhost:11434'
    )
    async def message_stream():
        message = {'role': 'user', 'content': 'Why is the sky blue?'}
        async for part in await client.chat(model='deepseek-r1:1.5b', messages=[message], stream=True):
            yield {"content": part['message']['content']}

    return StreamingResponse(message_stream(), media_type="application/json")
