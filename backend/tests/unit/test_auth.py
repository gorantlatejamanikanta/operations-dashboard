"""
Unit tests for authentication module
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from jose import JWTError

from app.core.auth import AuthService, get_current_user, require_role
from app.core.config import settings


class TestAuthService:
    """Test cases for AuthService class."""
    
    def test_init(self):
        """Test AuthService initialization."""
        auth_service = AuthService()
        assert auth_service.jwks_uri is not None
        assert auth_service.issuer is not None
        assert auth_service.audience is not None
        assert auth_service._jwks_cache is None
        assert auth_service._jwks_cache_time is None
    
    @patch('requests.get')
    def test_get_jwks_success(self, mock_get):
        """Test successful JWKS retrieval."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "test", "kty": "RSA"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        auth_service = AuthService()
        jwks = auth_service.get_jwks()
        
        assert jwks == {"keys": [{"kid": "test", "kty": "RSA"}]}
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_jwks_failure(self, mock_get):
        """Test JWKS retrieval failure."""
        mock_get.side_effect = Exception("Network error")
        
        auth_service = AuthService()
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.get_jwks()
        
        assert exc_info.value.status_code == 503
        assert "Unable to fetch JWKS" in str(exc_info.value.detail)
    
    @patch('app.core.auth.jwt.decode')
    @patch('app.core.auth.jwt.get_unverified_header')
    def test_verify_token_success(self, mock_get_header, mock_decode, mocker):
        """Test successful token verification."""
        # Mock header
        mock_get_header.return_value = {"kid": "test-kid"}
        
        # Mock JWKS
        mock_jwks = {"keys": [{"kid": "test-kid", "kty": "RSA"}]}
        
        # Mock decode
        mock_payload = {
            "sub": "user123",
            "name": "Test User",
            "preferred_username": "test@example.com"
        }
        mock_decode.return_value = mock_payload
        
        auth_service = AuthService()
        auth_service._jwks_cache = mock_jwks
        
        result = auth_service.verify_token("test-token")
        
        assert result == mock_payload
        mock_decode.assert_called_once()
    
    @patch('app.core.auth.jwt.get_unverified_header')
    def test_verify_token_missing_kid(self, mock_get_header):
        """Test token verification with missing kid."""
        mock_get_header.return_value = {}
        
        auth_service = AuthService()
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token("test-token")
        
        assert exc_info.value.status_code == 401
        assert "Token missing kid in header" in str(exc_info.value.detail)
    
    @patch('app.core.auth.jwt.decode')
    @patch('app.core.auth.jwt.get_unverified_header')
    def test_verify_token_jwt_error(self, mock_get_header, mock_decode):
        """Test token verification with JWT error."""
        mock_get_header.return_value = {"kid": "test-kid"}
        mock_decode.side_effect = JWTError("Invalid token")
        
        auth_service = AuthService()
        auth_service._jwks_cache = {"keys": [{"kid": "test-kid"}]}
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token("test-token")
        
        assert exc_info.value.status_code == 401
        assert "Token validation failed" in str(exc_info.value.detail)


class TestAuthDependencies:
    """Test cases for authentication dependencies."""
    
    @patch('app.core.config.settings')
    def test_get_current_user_development_mode(self, mock_settings):
        """Test get_current_user in development mode."""
        mock_settings.AZURE_TENANT_ID = None
        mock_settings.AZURE_CLIENT_ID = None
        mock_settings.ENVIRONMENT = "development"
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test-token"
        
        result = get_current_user(mock_credentials)
        
        assert result["sub"] == "dev-user"
        assert result["name"] == "Development User"
        assert result["email"] == "dev@example.com"
        assert result["roles"] == ["user"]
    
    @patch('app.core.config.settings')
    def test_get_current_user_production_no_azure(self, mock_settings):
        """Test get_current_user in production without Azure AD."""
        mock_settings.AZURE_TENANT_ID = None
        mock_settings.AZURE_CLIENT_ID = None
        mock_settings.ENVIRONMENT = "production"
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test-token"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_credentials)
        
        assert exc_info.value.status_code == 401
        assert "Authentication is required" in str(exc_info.value.detail)
    
    @patch('app.core.auth.auth_service.verify_token')
    @patch('app.core.config.settings')
    def test_get_current_user_with_azure(self, mock_settings, mock_verify):
        """Test get_current_user with Azure AD configured."""
        mock_settings.AZURE_TENANT_ID = "test-tenant"
        mock_settings.AZURE_CLIENT_ID = "test-client"
        
        mock_verify.return_value = {
            "sub": "azure-user",
            "name": "Azure User",
            "preferred_username": "azure@example.com",
            "roles": ["user"]
        }
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "azure-token"
        
        result = get_current_user(mock_credentials)
        
        assert result["sub"] == "azure-user"
        assert result["name"] == "Azure User"
        assert result["email"] == "azure@example.com"
        assert result["roles"] == ["user"]
    
    def test_require_role_success(self):
        """Test require_role with sufficient permissions."""
        mock_user = {"roles": ["user", "admin"]}
        
        role_checker = require_role("user")
        result = role_checker(mock_user)
        
        assert result == mock_user
    
    def test_require_role_admin_access(self):
        """Test require_role with admin access."""
        mock_user = {"roles": ["admin"]}
        
        role_checker = require_role("user")
        result = role_checker(mock_user)
        
        assert result == mock_user
    
    def test_require_role_insufficient_permissions(self):
        """Test require_role with insufficient permissions."""
        mock_user = {"roles": ["user"]}
        
        role_checker = require_role("admin")
        
        with pytest.raises(HTTPException) as exc_info:
            role_checker(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)
    
    def test_require_role_no_roles(self):
        """Test require_role with no roles."""
        mock_user = {"roles": []}
        
        role_checker = require_role("user")
        
        with pytest.raises(HTTPException) as exc_info:
            role_checker(mock_user)
        
        assert exc_info.value.status_code == 403


@pytest.mark.unit
@pytest.mark.auth
class TestAuthIntegration:
    """Integration tests for authentication flow."""
    
    @patch('app.core.auth.auth_service')
    def test_full_auth_flow(self, mock_auth_service):
        """Test complete authentication flow."""
        # Mock successful token verification
        mock_auth_service.verify_token.return_value = {
            "sub": "test-user",
            "name": "Test User",
            "preferred_username": "test@example.com",
            "roles": ["user"]
        }
        
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid-token"
        
        # Test authentication
        user = get_current_user(mock_credentials)
        assert user["sub"] == "test-user"
        
        # Test role requirement
        role_checker = require_role("user")
        result = role_checker(user)
        assert result == user
        
        # Test insufficient role
        admin_checker = require_role("admin")
        with pytest.raises(HTTPException):
            admin_checker(user)