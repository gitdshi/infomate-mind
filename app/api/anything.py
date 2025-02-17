from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import json
import httpx
from app.services import AnythingLLM

router = APIRouter()

class StreamChatRequest(BaseModel):
    message: str
    workspace: str
    thread: str


@router.post("/anything/streamchat")
async def streamchat(request: StreamChatRequest):
    return await AnythingLLM.streamChat(message=request.message, workspace=request.workspace, thread=request.thread)

@router.get("/anything/messages")
def messages(workspace: str):
    workspaceObj = AnythingLLM.ensureWorkspaceExists(workspace)

    if not workspaceObj:
        raise HTTPException(status_code=404, detail="Workspace not found")

    result = {
        'id': workspaceObj.get('id'),
        'slug': workspaceObj.get('slug'),
        'threads': []
    }

    for t in workspaceObj.get("threads") or []:
        thread_obj = {
            'slug': t.get('slug'),
            'name': t.get('name'),
            'chats': []
        }
        for tc in AnythingLLM.getThreadChats(workspace=workspace, thread=t["slug"]) or []:
            if thread_obj['name'] is None:
                thread_obj['name'] = tc.get('content')[:30]
            chat_obj = {
                'role': tc.get('role'),
                'content': tc.get('content'),
                'sentAt': tc.get('sentAt')
            }
            thread_obj['chats'].append(chat_obj)
        result['threads'].append(thread_obj)

    return result
