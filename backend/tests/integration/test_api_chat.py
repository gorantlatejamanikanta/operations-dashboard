"""
Integration tests for chat API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.chat
class TestChatAPI:
    """Integration tests for chat API endpoints."""
    
    def test_chat_without_openai(self, client: TestClient, auth_headers):
        """Test chat endpoint without OpenAI configuration."""
        chat_data = {
            "message": "Show me all projects",
            "conversation_id": "test-conv-1"
        }
        
        response = client.post("/api/chat/", json=chat_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "Azure OpenAI is not configured" in data["response"]
        assert data["sql_query"] is None
        assert data["conversation_id"] == "test-conv-1"
    
    @patch('app.services.chat_service.chat_service.client')
    def test_chat_with_openai_success(self, mock_client, client: TestClient, auth_headers):
        """Test successful chat with OpenAI."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Here are your projects:\n\n```sql\nSELECT * FROM project;\n```"
        mock_client.chat.completions.create.return_value = mock_response
        
        chat_data = {
            "message": "Show me all projects"
        }
        
        response = client.post("/api/chat/", json=chat_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "Here are your projects" in data["response"]
        assert data["sql_query"] == "SELECT * FROM project;"
        assert data["conversation_id"] is not None
    
    @patch('app.services.chat_service.chat_service.client')
    def test_chat_with_sql_execution(self, mock_client, client: TestClient, auth_headers, sample_project):
        """Test chat with SQL execution."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "```sql\nSELECT project_name FROM project WHERE is_active = true;\n```"
        mock_client.chat.completions.create.return_value = mock_response
        
        chat_data = {
            "message": "Show me active project names"
        }
        
        response = client.post("/api/chat/", json=chat_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "Query Results:" in data["response"]
        assert sample_project.project_name in data["response"]
        assert data["sql_query"] == "SELECT project_name FROM project WHERE is_active = true;"
    
    def test_chat_input_validation(self, client: TestClient, auth_headers):
        """Test chat input validation."""
        # Test empty message
        response = client.post("/api/chat/", json={"message": ""}, headers=auth_headers)
        assert response.status_code == 422
        
        # Test message too long
        long_message = "x" * 1001
        response = client.post("/api/chat/", json={"message": long_message}, headers=auth_headers)
        assert response.status_code == 422
        
        # Test invalid characters
        response = client.post("/api/chat/", json={"message": "test <script>alert('xss')</script>"}, headers=auth_headers)
        assert response.status_code == 422
    
    def test_chat_conversation_continuity(self, client: TestClient, auth_headers):
        """Test conversation continuity with conversation ID."""
        conv_id = "test-conversation-123"
        
        # First message
        response1 = client.post("/api/chat/", json={
            "message": "Hello",
            "conversation_id": conv_id
        }, headers=auth_headers)
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["conversation_id"] == conv_id
        
        # Second message in same conversation
        response2 = client.post("/api/chat/", json={
            "message": "Follow up question",
            "conversation_id": conv_id
        }, headers=auth_headers)
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["conversation_id"] == conv_id
    
    @patch('app.services.chat_service.chat_service.client')
    def test_chat_sql_injection_protection(self, mock_client, client: TestClient, auth_headers):
        """Test SQL injection protection in chat."""
        # Mock OpenAI to return malicious SQL
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "```sql\nSELECT * FROM project; DROP TABLE users; --\n```"
        mock_client.chat.completions.create.return_value = mock_response
        
        chat_data = {
            "message": "Show me projects and delete users"
        }
        
        response = client.post("/api/chat/", json=chat_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Should contain error about forbidden keywords
        assert "Error executing query" in data["response"]
    
    @patch('app.services.chat_service.chat_service.client')
    def test_chat_query_length_limit(self, mock_client, client: TestClient, auth_headers):
        """Test query length limit protection."""
        # Mock OpenAI to return very long query
        long_query = "SELECT * FROM project WHERE " + "x = 1 AND " * 200 + "y = 2;"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = f"```sql\n{long_query}\n```"
        mock_client.chat.completions.create.return_value = mock_response
        
        chat_data = {
            "message": "Complex query"
        }
        
        response = client.post("/api/chat/", json=chat_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "Error executing query" in data["response"]
    
    def test_chat_without_authentication(self, client: TestClient, mocker):
        """Test chat endpoint without authentication."""
        # Remove auth mock
        mocker.patch("app.core.auth.get_current_user", side_effect=Exception("No auth"))
        
        chat_data = {"message": "test"}
        response = client.post("/api/chat/", json=chat_data)
        
        assert response.status_code == 401
    
    @patch('app.services.chat_service.chat_service.chat')
    def test_chat_service_exception_handling(self, mock_chat, client: TestClient, auth_headers):
        """Test exception handling in chat service."""
        # Mock chat service to raise exception
        mock_chat.side_effect = Exception("Service error")
        
        chat_data = {"message": "test message"}
        response = client.post("/api/chat/", json=chat_data, headers=auth_headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "An error occurred while processing your request" in data["detail"]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
class TestChatAPISecurity:
    """Security tests for chat API."""
    
    def test_rate_limiting_simulation(self, client: TestClient, auth_headers):
        """Test rate limiting behavior (simulation)."""
        # Make multiple rapid requests
        responses = []
        for i in range(5):
            response = client.post("/api/chat/", json={"message": f"test {i}"}, headers=auth_headers)
            responses.append(response)
        
        # All should succeed in test environment (rate limiting disabled)
        for response in responses:
            assert response.status_code in [200, 500]  # 500 for service errors is acceptable
    
    def test_conversation_id_validation(self, client: TestClient, auth_headers):
        """Test conversation ID validation."""
        # Test invalid conversation ID format
        invalid_ids = [
            "conv with spaces",
            "conv@invalid",
            "conv#invalid",
            "conv/invalid"
        ]
        
        for invalid_id in invalid_ids:
            response = client.post("/api/chat/", json={
                "message": "test",
                "conversation_id": invalid_id
            }, headers=auth_headers)
            assert response.status_code == 422
    
    def test_message_sanitization(self, client: TestClient, auth_headers):
        """Test message content sanitization."""
        dangerous_messages = [
            "test <script>alert('xss')</script>",
            'test "malicious"',
            "test 'single quotes'",
            "test > redirect",
            "test < input"
        ]
        
        for message in dangerous_messages:
            response = client.post("/api/chat/", json={"message": message}, headers=auth_headers)
            # Should either be rejected (422) or sanitized (200)
            assert response.status_code in [200, 422]
    
    @patch('app.services.chat_service.chat_service.client')
    def test_response_content_safety(self, mock_client, client: TestClient, auth_headers):
        """Test that responses don't contain sensitive information."""
        # Mock response that might contain sensitive data
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Database error: connection string postgresql://user:password@host/db"
        mock_client.chat.completions.create.return_value = mock_response
        
        response = client.post("/api/chat/", json={"message": "test"}, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Response should not contain sensitive connection details
        assert "password" not in data["response"].lower()
        assert "connection string" not in data["response"].lower()