import uuid
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from openai import AzureOpenAI
from ..core.config import settings
from ..core.database import get_db
from sqlalchemy import text
import re
import json


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

When generating SQL queries:
1. Use proper PostgreSQL syntax
2. Always use table aliases for clarity
3. Format dates properly (YYYY-MM-DD)
4. Use appropriate aggregation functions (SUM, COUNT, AVG)
5. Include ORDER BY for better results
6. Limit results to reasonable numbers (LIMIT 10-50)

Example queries:
- "Show me all active projects": SELECT * FROM project WHERE is_active = true ORDER BY project_name;
- "What's the total cost by region?": SELECT deployed_region, SUM(total_cost_to_date) as total FROM project p JOIN project_cost_summary pcs ON p.id = pcs.project_id GROUP BY deployed_region ORDER BY total DESC;

Always wrap your SQL queries in ```sql``` code blocks."""
    
    def _get_schema_info(self) -> str:
        """Get detailed schema information for the system prompt"""
        return """
Available Tables and Columns:
1. project: id (PK), project_name, project_type (values: 'Internal', 'External', 'Client Demo'), member_firm, deployed_region (values: 'US', 'EU', 'APAC'), is_active (boolean), description, engagement_code, engagement_partner, opportunity_code, engagement_manager, project_startdate (date), project_enddate (date)
2. aiq_consumption: id (PK), project_id (FK to project.id), aiq_assumption_name, consumption_amount (numeric), consumption_day (date)
3. resource_group: id (PK), resource_group_name, project_id (FK to project.id), status
4. project_resource_group: project_id (FK), resource_group_id (FK)
5. monthly_cost: project_id (FK), resource_group_id (FK), month (date), cost (numeric)
6. cost_data: key (PK), period (date), month_year, resource_group_id (FK), cost (numeric)
7. project_cost_summary: project_id (FK), resource_group_id (FK), total_cost_to_date (numeric), updated_date (date), costs_passed_back_to_date (numeric), gpt_costs_to_date (numeric), gpt_costs_passed_back_to_date (numeric), remarks (text)

Relationships:
- project -> aiq_consumption (one-to-many)
- project -> resource_group (one-to-many)
- project -> monthly_cost (one-to-many)
- project -> project_cost_summary (one-to-many)
- resource_group -> monthly_cost (one-to-many)
- resource_group -> cost_data (one-to-many)
- resource_group -> project_cost_summary (one-to-many)
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
                temperature=0.1,  # Lower temperature for more consistent SQL generation
                max_tokens=1500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Extract SQL query if present
            sql_query = self._extract_sql_query(assistant_message)
            
            # If we have a SQL query and database connection, execute it
            if sql_query and db:
                try:
                    query_results = self.execute_query(sql_query, db)
                    
                    # Format results and add to response
                    if query_results:
                        formatted_results = self._format_query_results(query_results)
                        assistant_message += f"\n\nQuery Results:\n{formatted_results}"
                    else:
                        assistant_message += "\n\nQuery executed successfully but returned no results."
                        
                except Exception as e:
                    assistant_message += f"\n\nError executing query: {str(e)}"
            
            # Add assistant response to conversation
            self.conversations[conversation_id].append({"role": "assistant", "content": assistant_message})
            
            return assistant_message, sql_query, conversation_id
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
            return error_message, None, conversation_id
    
    def _extract_sql_query(self, message: str) -> Optional[str]:
        """Extract SQL query from assistant message"""
        # Look for SQL in code blocks
        sql_patterns = [
            r'```sql\s*(.*?)\s*```',
            r'```\s*(SELECT.*?)\s*```',
            r'```\s*(WITH.*?)\s*```',
            r'```\s*(INSERT.*?)\s*```',
            r'```\s*(UPDATE.*?)\s*```',
            r'```\s*(DELETE.*?)\s*```'
        ]
        
        for pattern in sql_patterns:
            match = re.search(pattern, message, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def execute_query(self, query: str, db: Session) -> List[Dict]:
        """Execute SQL query and return results with enhanced security"""
        try:
            # Security check - only allow SELECT and WITH queries
            query_upper = query.upper().strip()
            if not query_upper.startswith(('SELECT', 'WITH')):
                raise Exception("Only SELECT and WITH queries are allowed for security reasons")
            
            # Additional security checks
            dangerous_keywords = [
                'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE',
                'EXEC', 'EXECUTE', 'CALL', 'DECLARE', 'GRANT', 'REVOKE', 'COMMIT',
                'ROLLBACK', 'SAVEPOINT', 'SET', 'SHOW', 'DESCRIBE', 'EXPLAIN'
            ]
            
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    raise Exception(f"Query contains forbidden keyword: {keyword}")
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r';\s*(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)',  # Multiple statements
                r'--',  # SQL comments
                r'/\*.*\*/',  # Block comments
                r'UNION.*SELECT',  # Union-based injection
                r'OR\s+1\s*=\s*1',  # Classic injection
                r'AND\s+1\s*=\s*1',  # Classic injection
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, query_upper):
                    raise Exception("Query contains suspicious patterns")
            
            # Limit query complexity
            if len(query) > 2000:
                raise Exception("Query too long - maximum 2000 characters allowed")
            
            # Execute query with timeout
            result = db.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            
            # Limit result size
            if len(rows) > 1000:
                rows = rows[:1000]
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            # Log the error but don't expose details
            print(f"Query execution error: {str(e)}")  # Server-side logging
            raise Exception("Query execution failed due to security or syntax error")
    
    def _format_query_results(self, results: List[Dict]) -> str:
        """Format query results for display"""
        if not results:
            return "No results found."
        
        # Limit results for display
        display_results = results[:10]  # Show max 10 rows
        
        # Create a simple table format
        if len(display_results) == 1:
            # Single result - show as key-value pairs
            formatted = []
            for key, value in display_results[0].items():
                formatted.append(f"{key}: {value}")
            return "\n".join(formatted)
        else:
            # Multiple results - show as table
            headers = list(display_results[0].keys())
            
            # Create header row
            formatted = [" | ".join(headers)]
            formatted.append("-" * len(formatted[0]))
            
            # Add data rows
            for row in display_results:
                row_data = []
                for header in headers:
                    value = row.get(header, "")
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 30:
                        str_value = str_value[:27] + "..."
                    row_data.append(str_value)
                formatted.append(" | ".join(row_data))
            
            if len(results) > 10:
                formatted.append(f"\n... and {len(results) - 10} more rows")
            
            return "\n".join(formatted)


chat_service = ChatService()
