
import os
import json
import httpx
import requests
from fastapi.responses import StreamingResponse

client = httpx.AsyncClient()
api_key = os.getenv('ANYTHINGLLM_API_KEY')
api_base_url = os.getenv('ANYTHINGLLM_API_URL')
headers = {
        'Authorization': f'Bearer {api_key}'
}

async def uploadFile(file_name: str, file_path: str):
    url = api_base_url + "/document/upload"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'rb') as file:
        files = {'file': (file_name, file, 'application/octet-stream')}
        response = await client.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

async def addEmbedding(file_location: str, workspace: str):
    url = api_base_url + f"/workspace/{workspace}/update-embeddings"

    ensureWorkspaceExists(workspace)

    payload = {
        "adds": [file_location],
        "deletes": []
    }
    response = await client.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


async def streamChat(workspace: str, thread: str, message: str):
    url = os.getenv('ANYTHINGLLM_API_URL') + f"/workspace/{workspace}/thread/{thread}/stream-chat"

    threadObj = ensureThreadExists(workspace=workspace, thread=thread, name=message[:30])

    async def anythingStream(message: str, thread: str):
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'mode': 'chat',
            'message': message
        }
        
        async with client.stream(method="POST", url=url, headers=headers, json=payload, timeout=60.0) as response:
            async for chunk in response.aiter_lines():
                try:
                    # Remove the "data: " prefix if present
                    if chunk.startswith("data: "):
                        chunk = chunk[len("data: "):]
                    json_chunk = json.loads(chunk)
                    message_id = json_chunk.get('id', '')
                    text_response = json_chunk.get('textResponse', '')
                    yield json.dumps({"thread_slug": thread,"message_id": message_id,"content": text_response}).encode('utf-8')
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON chunks

    return StreamingResponse(anythingStream(message, threadObj.get("slug")), media_type="application/json")

def getWorkspace(workspace: str):
    url = api_base_url + f"/workspace/{workspace}"
    response = requests.get(url=url,headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        if response_json.get("workspace"):
            return response_json.get("workspace")[0]
        else:
            return None
    else:
        response.raise_for_status()
        return None

def createWorkspace(workspace: str):
    url = api_base_url + f"/workspace/new"
    payload = {
        "slug": workspace,
        "name": workspace,
        "similarityThreshold": 0.5,
        "openAiHistory": 20,
        "chatMode": "chat",
        "topN": 4
    }
    response = requests.post(url=url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("workspace")
    else:
        response.raise_for_status()

def ensureWorkspaceExists(workspace: str):
    workspaceObj = getWorkspace(workspace)
    if workspaceObj is None:
        workspaceObj = createWorkspace(workspace)
    return workspaceObj

def getThread(workspace: str, thread: str):
    workspaceObj = getWorkspace(workspace)
    if workspaceObj and "threads" in workspaceObj:
        for t in workspaceObj["threads"]:
            if t["slug"] == thread:
                return t
    return None

def createThread(workspace: str, thread: str, name: str):
    url = api_base_url + f"/workspace/{workspace}/thread/new"
    payload = {
        "name": name,
        "slug": thread
    }
    response = requests.post(url=url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("thread")
    else:
        response.raise_for_status()

def ensureThreadExists(workspace: str, thread: str, name: str):
    threadObj = getThread(workspace, thread)
    if threadObj is None:
        threadObj = createThread(workspace, thread, name)
    return threadObj

def getThreadChats(workspace: str, thread: str):
    url = api_base_url + f"/workspace/{workspace}/thread/{thread}/chats"
    response = requests.get(url=url,headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        if response_json.get("history"):
            return response_json.get("history")
        else:
            return None
    else:
        response.raise_for_status()
        return None