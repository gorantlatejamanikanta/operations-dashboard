from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.chat import ChatMessage, ChatResponse
from ..core.database import get_db
from ..core.auth import get_current_user
from ..services.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", 
             response_model=ChatResponse,
             summary="AI Chat Query",
             description="Send a natural language query to get AI-powered SQL responses",
             responses={
                 200: {
                     "description": "Chat response generated successfully",
                     "content": {
                         "application/json": {
                             "example": {
                                 "response": "Here are the active projects:\n\n1. Cloud Migration Project - US Region\n2. Data Analytics Platform - EU Region\n\nTotal: 2 active projects",
                                 "sql_query": "SELECT project_name, deployed_region FROM project WHERE is_active = true ORDER BY project_name;",
                                 "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000"
                             }
                         }
                     }
                 },
                 400: {"description": "Invalid input - message too long or contains invalid characters"},
                 401: {"description": "Authentication required"},
                 429: {"description": "Rate limit exceeded"},
                 500: {"description": "Error processing request"}
             })
async def chat_endpoint(
    chat_message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    AI-powered chat interface for querying the database using natural language.
    
    **How it works:**
    1. Send a natural language question about your projects, costs, or resources
    2. The AI converts your question into a SQL query
    3. The query is executed safely against the database
    4. Results are formatted and returned in a human-readable format
    
    **Example Queries:**
    - "Show me all active projects"
    - "What's the total cost by region?"
    - "Which projects are over budget?"
    - "List projects ending this month"
    - "Show resource groups with highest costs"
    
    **Security Features:**
    - Only SELECT queries are allowed
    - SQL injection protection
    - Query validation and sanitization
    - Result size limits
    
    **Input Validation:**
    - Message length: 1-1000 characters
    - No HTML/script tags allowed
    - Conversation ID format validation
    
    **Authentication:** Required (any authenticated user)
    
    **Rate Limiting:** 
    - Included in 100 requests/minute limit
    - Additional AI service rate limits may apply
    """
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
        # Log the actual error server-side
        print(f"Chat endpoint error: {str(e)}")
        # Return generic error to client
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing your request. Please try again."
        )
