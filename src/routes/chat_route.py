# src/routes/chat_route.py
from fastapi import APIRouter, HTTPException
from src.handlers.chat_handler import chat_agent_handler

router = APIRouter(prefix="/chat")

@router.post("/{session_id}")
def post_chat(session_id: str, message: str):
    result = chat_agent_handler(message=message, session_id=session_id)
    if isinstance(result, tuple) and result[1] >= 400:
        raise HTTPException(status_code=result[1], detail=result[0])
    return result
