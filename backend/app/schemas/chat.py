from pydantic import BaseModel
from typing import Optional


class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sql_query: Optional[str] = None
    conversation_id: str
