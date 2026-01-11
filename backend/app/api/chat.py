from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.chat import ChatMessage, ChatResponse
from ..core.database import get_db
from ..services.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    chat_message: ChatMessage,
    db: Session = Depends(get_db)
):
    """Chat endpoint for AI-powered SQL queries"""
    try:
        response, sql_query, conversation_id = await chat_service.chat(
            message=chat_message.message,
            conversation_id=chat_message.conversation_id,
            db=db
        )
        
        return ChatResponse(
            response=response,
            sql_query=sql_query,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
