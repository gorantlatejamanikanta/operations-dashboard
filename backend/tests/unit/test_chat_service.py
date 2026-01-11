"""
Unit tests for chat service
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.chat_service import ChatService, chat_service


class TestChatService:
    """Test cases for ChatService class."""
    
    def test_init_without_azure_openai(self):
        """Test ChatService initialization without Azure OpenAI."""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.AZURE_OPENAI_API_KEY = None
            mock_settings.AZURE_OPENAI_ENDPOINT = None
            
            service = ChatService()
            
            assert service.client is None
            assert service.system_prompt is not None
            assert service.conversations == {}
    
    def test_init_with_azure_openai(self):
        """Test ChatService initialization with Azure OpenAI."""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.AZURE_OPENAI_API_KEY = "test-key"
            mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
            mock_settings.AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
            
            with patch('app.services.chat_service.AzureOpenAI') as mock_azure_openai:
                service = ChatService()
                
                mock_azure_openai.assert_called_once()
                assert service.client is not None
    
    def test_get_system_prompt(self):
        """Test system prompt generation."""
        service = ChatService()
        prompt = service._get_system_prompt()
        
        assert "SQL-Agent assistant" in prompt
        assert "Database Schema" in prompt
        assert "project" in prompt
        assert "SELECT" in prompt
    
    def test_get_schema_info(self):
        """Test schema information generation."""
        service = ChatService()
        schema_info = service._get_schema_info()
        
        assert "Available Tables and Columns" in schema_info
        assert "project:" in schema_info
        assert "aiq_consumption:" in schema_info
        assert "Relationships:" in schema_info
    
    @pytest.mark.asyncio
    async def test_chat_without_openai_client(self):
        """Test chat method without OpenAI client."""
        service = ChatService()
        service.client = None
        
        response, sql_query, conv_id = await service.chat("test message")
        
        assert "Azure OpenAI is not configured" in response
        assert sql_query is None
        assert conv_id is not None
    
    @pytest.mark.asyncio
    async def test_chat_with_openai_client(self):
        """Test chat method with OpenAI client."""
        service = ChatService()
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Here are your projects:\n\n```sql\nSELECT * FROM project WHERE is_active = true;\n```"
        mock_client.chat.completions.create.return_value = mock_response
        service.client = mock_client
        
        # Mock database session
        mock_db = MagicMock(spec=Session)
        
        response, sql_query, conv_id = await service.chat("show me active projects", db=mock_db)
        
        assert "Here are your projects" in response
        assert sql_query == "SELECT * FROM project WHERE is_active = true;"
        assert conv_id is not None
        mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_chat_with_conversation_id(self):
        """Test chat method with existing conversation ID."""
        service = ChatService()
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response to follow-up question"
        mock_client.chat.completions.create.return_value = mock_response
        service.client = mock_client
        
        conv_id = "test-conversation-123"
        
        # First message
        await service.chat("first message", conversation_id=conv_id)
        
        # Follow-up message
        response, sql_query, returned_conv_id = await service.chat("follow-up", conversation_id=conv_id)
        
        assert returned_conv_id == conv_id
        assert len(service.conversations[conv_id]) > 2  # System + user + assistant + user + assistant
    
    def test_extract_sql_query_with_sql_block(self):
        """Test SQL query extraction from code block."""
        service = ChatService()
        
        message = "Here's your query:\n\n```sql\nSELECT * FROM project;\n```"
        sql_query = service._extract_sql_query(message)
        
        assert sql_query == "SELECT * FROM project;"
    
    def test_extract_sql_query_with_generic_block(self):
        """Test SQL query extraction from generic code block."""
        service = ChatService()
        
        message = "Here's your query:\n\n```\nSELECT * FROM project WHERE id = 1;\n```"
        sql_query = service._extract_sql_query(message)
        
        assert sql_query == "SELECT * FROM project WHERE id = 1;"
    
    def test_extract_sql_query_no_match(self):
        """Test SQL query extraction with no match."""
        service = ChatService()
        
        message = "This is just a regular response without SQL."
        sql_query = service._extract_sql_query(message)
        
        assert sql_query is None
    
    def test_execute_query_valid_select(self):
        """Test query execution with valid SELECT query."""
        service = ChatService()
        
        # Mock database session
        mock_db = MagicMock(spec=Session)
        mock_result = MagicMock()
        mock_result.keys.return_value = ["id", "name"]
        mock_result.fetchall.return_value = [(1, "Project 1"), (2, "Project 2")]
        mock_db.execute.return_value = mock_result
        
        query = "SELECT id, name FROM project;"
        result = service.execute_query(query, mock_db)
        
        expected = [
            {"id": 1, "name": "Project 1"},
            {"id": 2, "name": "Project 2"}
        ]
        assert result == expected
    
    def test_execute_query_invalid_statement(self):
        """Test query execution with invalid statement."""
        service = ChatService()
        mock_db = MagicMock(spec=Session)
        
        query = "DROP TABLE project;"
        
        with pytest.raises(Exception) as exc_info:
            service.execute_query(query, mock_db)
        
        assert "Only SELECT and WITH queries are allowed" in str(exc_info.value)
    
    def test_execute_query_dangerous_keyword(self):
        """Test query execution with dangerous keyword."""
        service = ChatService()
        mock_db = MagicMock(spec=Session)
        
        query = "SELECT * FROM project; DROP TABLE users;"
        
        with pytest.raises(Exception) as exc_info:
            service.execute_query(query, mock_db)
        
        assert "forbidden keyword" in str(exc_info.value)
    
    def test_execute_query_suspicious_pattern(self):
        """Test query execution with suspicious pattern."""
        service = ChatService()
        mock_db = MagicMock(spec=Session)
        
        query = "SELECT * FROM project WHERE 1=1 OR 1=1;"
        
        with pytest.raises(Exception) as exc_info:
            service.execute_query(query, mock_db)
        
        assert "suspicious patterns" in str(exc_info.value)
    
    def test_execute_query_too_long(self):
        """Test query execution with query too long."""
        service = ChatService()
        mock_db = MagicMock(spec=Session)
        
        query = "SELECT * FROM project WHERE " + "x = 1 AND " * 200 + "y = 2;"
        
        with pytest.raises(Exception) as exc_info:
            service.execute_query(query, mock_db)
        
        assert "Query too long" in str(exc_info.value)
    
    def test_execute_query_database_error(self):
        """Test query execution with database error."""
        service = ChatService()
        
        # Mock database session that raises an error
        mock_db = MagicMock(spec=Session)
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        query = "SELECT * FROM project;"
        
        with pytest.raises(Exception) as exc_info:
            service.execute_query(query, mock_db)
        
        assert "Query execution failed due to security or syntax error" in str(exc_info.value)
    
    def test_format_query_results_empty(self):
        """Test query results formatting with empty results."""
        service = ChatService()
        
        result = service._format_query_results([])
        
        assert result == "No results found."
    
    def test_format_query_results_single_row(self):
        """Test query results formatting with single row."""
        service = ChatService()
        
        results = [{"id": 1, "name": "Project 1", "status": "active"}]
        result = service._format_query_results(results)
        
        assert "id: 1" in result
        assert "name: Project 1" in result
        assert "status: active" in result
    
    def test_format_query_results_multiple_rows(self):
        """Test query results formatting with multiple rows."""
        service = ChatService()
        
        results = [
            {"id": 1, "name": "Project 1"},
            {"id": 2, "name": "Project 2"},
            {"id": 3, "name": "Project 3"}
        ]
        result = service._format_query_results(results)
        
        assert "id | name" in result
        assert "Project 1" in result
        assert "Project 2" in result
        assert "Project 3" in result
    
    def test_format_query_results_truncation(self):
        """Test query results formatting with truncation."""
        service = ChatService()
        
        # Create results with long values
        results = [
            {"id": 1, "description": "This is a very long description that should be truncated because it exceeds the limit"},
            {"id": 2, "description": "Short desc"}
        ]
        result = service._format_query_results(results)
        
        assert "..." in result  # Truncation indicator
        assert "Short desc" in result
    
    def test_format_query_results_many_rows(self):
        """Test query results formatting with many rows."""
        service = ChatService()
        
        # Create 15 results (more than display limit of 10)
        results = [{"id": i, "name": f"Project {i}"} for i in range(1, 16)]
        result = service._format_query_results(results)
        
        assert "... and 5 more rows" in result
        assert "Project 1" in result
        assert "Project 10" in result
        assert "Project 15" not in result  # Should be truncated


@pytest.mark.unit
@pytest.mark.chat
class TestChatServiceIntegration:
    """Integration tests for ChatService."""
    
    @pytest.mark.asyncio
    async def test_full_chat_flow_with_sql_execution(self):
        """Test complete chat flow with SQL execution."""
        service = ChatService()
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Here are your projects:\n\n```sql\nSELECT id, project_name FROM project WHERE is_active = true;\n```"
        mock_client.chat.completions.create.return_value = mock_response
        service.client = mock_client
        
        # Mock database session
        mock_db = MagicMock(spec=Session)
        mock_result = MagicMock()
        mock_result.keys.return_value = ["id", "project_name"]
        mock_result.fetchall.return_value = [(1, "Project 1"), (2, "Project 2")]
        mock_db.execute.return_value = mock_result
        
        response, sql_query, conv_id = await service.chat("show me active projects", db=mock_db)
        
        assert "Here are your projects" in response
        assert "Query Results:" in response
        assert "Project 1" in response
        assert "Project 2" in response
        assert sql_query == "SELECT id, project_name FROM project WHERE is_active = true;"
        assert conv_id is not None
    
    @pytest.mark.asyncio
    async def test_chat_with_sql_execution_error(self):
        """Test chat flow with SQL execution error."""
        service = ChatService()
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "```sql\nSELECT * FROM nonexistent_table;\n```"
        mock_client.chat.completions.create.return_value = mock_response
        service.client = mock_client
        
        # Mock database session that raises an error
        mock_db = MagicMock(spec=Session)
        mock_db.execute.side_effect = Exception("Table does not exist")
        
        response, sql_query, conv_id = await service.chat("show me data", db=mock_db)
        
        assert "Error executing query" in response
        assert sql_query == "SELECT * FROM nonexistent_table;"
        assert conv_id is not None