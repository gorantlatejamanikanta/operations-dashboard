from pydantic import BaseModel, Field, validator
from typing import Optional
import re


class ChatMessage(BaseModel):
    """Chat message input schema"""
    
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Natural language query about projects, costs, or resources",
        example="Show me all active projects in the US region"
    )
    conversation_id: Optional[str] = Field(
        None, 
        max_length=100, 
        description="Optional conversation ID to maintain context",
        example="conv-123e4567-e89b-12d3-a456-426614174000"
    )
    
    @validator('message')
    def validate_message(cls, v):
        """Validate and sanitize chat message"""
        # Remove potentially dangerous characters
        if re.search(r'[<>"\']', v):
            raise ValueError("Message contains invalid characters")
        return v.strip()
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        """Validate conversation ID format"""
        if v and not re.match(r'^[a-zA-Z0-9\-_]+$', v):
            raise ValueError("Invalid conversation ID format")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What are the total costs by region for this month?",
                "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000"
            }
        }


class ChatResponse(BaseModel):
    """Chat response output schema"""
    
    response: str = Field(
        ..., 
        description="AI-generated response to the user's query",
        example="Here are the total costs by region for this month:\n\nUS: $45,230\nEU: $32,150\nAPAC: $28,900\n\nTotal: $106,280"
    )
    sql_query: Optional[str] = Field(
        None, 
        description="SQL query that was executed (if any)",
        example="SELECT deployed_region, SUM(cost) as total_cost FROM monthly_cost WHERE EXTRACT(MONTH FROM month) = EXTRACT(MONTH FROM CURRENT_DATE) GROUP BY deployed_region ORDER BY total_cost DESC;"
    )
    conversation_id: str = Field(
        ..., 
        description="Conversation ID for maintaining context",
        example="conv-123e4567-e89b-12d3-a456-426614174000"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "response": "I found 5 active projects:\n\n1. Cloud Migration Project (US) - 75% complete\n2. Data Analytics Platform (EU) - 45% complete\n3. Security Upgrade (APAC) - 30% complete\n4. Infrastructure Modernization (US) - 60% complete\n5. Compliance Initiative (EU) - 90% complete",
                "sql_query": "SELECT project_name, deployed_region, progress_percentage FROM project WHERE is_active = true ORDER BY progress_percentage DESC;",
                "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000"
            }
        }
