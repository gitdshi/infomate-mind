from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ollama import AsyncClient
import os
import json

router = APIRouter()

@router.get("/ollama")
async def stream(model: str, message: str):
    client = AsyncClient(
        host=os.getenv('OLLAMA_HOST')
    )
    async def messageStream(model: str, message: str):
        message = {'role': 'user', 'content': message}
        async for part in await client.chat(model=model, messages=[message], stream=True):
            yield json.dumps({"content": part['message']['content']}).encode('utf-8')

    return StreamingResponse(messageStream(model, message), media_type="application/json")