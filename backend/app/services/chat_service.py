import uuid
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from openai import AzureOpenAI
from ..core.config import settings
from ..core.database import get_db
from sqlalchemy import text


class ChatService:
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
        self.system_prompt = self._get_system_prompt()
        self.client = None
        if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
            try:
                self.client = AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
                )
            except Exception:
                pass
    
    def _get_system_prompt(self) -> str:
        return """You are a SQL-Agent assistant for a Multi-Cloud Operations Dashboard. 
Your role is to answer questions ONLY using the provided database schema. You must:
1. NEVER make up data or provide information outside the database schema
2. Generate SQL queries to answer user questions
3. Execute the SQL queries and interpret the results
4. Provide clear, concise answers based on the query results

Database Schema:
- project (id, project_name, project_type, member_firm, deployed_region, is_active, description, engagement_code, engagement_partner, opportunity_code, engagement_manager, project_startdate, project_enddate)
- aiq_consumption (id, project_id, aiq_assumption_name, consumption_amount, consumption_day)
- resource_group (id, resource_group_name, project_id, status)
- project_resource_group (project_id, resource_group_id)
- monthly_cost (project_id, resource_group_id, month, cost)
- cost_data (key, period, month_year, resource_group_id, cost)
- project_cost_summary (project_id, resource_group_id, total_cost_to_date, updated_date, costs_passed_back_to_date, gpt_costs_to_date, gpt_costs_passed_back_to_date, remarks)

When a user asks a question:
1. First, determine if the question can be answered from the schema
2. If yes, generate an appropriate SQL query
3. If no, politely explain that the question cannot be answered with the available data

IMPORTANT: Do not provide information about projects, costs, or resources that are not in the database. Always verify your answers with actual data queries."""
    
    def _get_schema_info(self) -> str:
        """Get detailed schema information for the system prompt"""
        return """
Available Tables and Columns:
1. project: id, project_name, project_type (values: 'Internal', 'External', 'Client Demo'), member_firm, deployed_region (values: 'US', 'EU', 'APAC'), is_active, description, engagement_code, engagement_partner, opportunity_code, engagement_manager, project_startdate, project_enddate
2. aiq_consumption: id, project_id (FK to project.id), aiq_assumption_name, consumption_amount, consumption_day
3. resource_group: id, resource_group_name, project_id (FK to project.id), status
4. project_resource_group: project_id (FK), resource_group_id (FK)
5. monthly_cost: project_id (FK), resource_group_id (FK), month, cost
6. cost_data: key (PK), period, month_year, resource_group_id (FK), cost
7. project_cost_summary: project_id (FK), resource_group_id (FK), total_cost_to_date, updated_date, costs_passed_back_to_date, gpt_costs_to_date, gpt_costs_passed_back_to_date, remarks
"""
    
    async def chat(self, message: str, conversation_id: Optional[str] = None, db: Session = None) -> tuple[str, Optional[str], str]:
        """Process chat message and return response"""
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = [
                {"role": "system", "content": self.system_prompt + self._get_schema_info()}
            ]
        
        # Add user message
        self.conversations[conversation_id].append({"role": "user", "content": message})
        
        if not self.client:
            error_message = "Azure OpenAI is not configured. Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables."
            return error_message, None, conversation_id
        
        try:
            # Get response from Azure OpenAI
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=self.conversations[conversation_id],
                temperature=0.3,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Try to extract SQL query if present
            sql_query = None
            if "SELECT" in assistant_message.upper() or "WITH" in assistant_message.upper():
                # Simple extraction - look for SQL between code blocks
                import re
                sql_match = re.search(r'```sql\s*(.*?)\s*```', assistant_message, re.DOTALL | re.IGNORECASE)
                if not sql_match:
                    sql_match = re.search(r'```\s*(SELECT.*?)\s*```', assistant_message, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    sql_query = sql_match.group(1).strip()
            
            # Add assistant response to conversation
            self.conversations[conversation_id].append({"role": "assistant", "content": assistant_message})
            
            return assistant_message, sql_query, conversation_id
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
            return error_message, None, conversation_id
    
    def execute_query(self, query: str, db: Session) -> List[Dict]:
        """Execute SQL query and return results"""
        try:
            result = db.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")


chat_service = ChatService()
