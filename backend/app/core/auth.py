"""
Authentication and authorization utilities
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import requests
from .config import settings

security = HTTPBearer()


class AuthService:
    def __init__(self):
        self.jwks_uri = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/discovery/v2.0/keys"
        self.issuer = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/v2.0"
        self.audience = settings.AZURE_CLIENT_ID
        self._jwks_cache = None
        self._jwks_cache_time = None
    
    def get_jwks(self):
        """Get JWKS from Azure AD with caching"""
        now = datetime.utcnow()
        if (self._jwks_cache is None or 
            self._jwks_cache_time is None or 
            (now - self._jwks_cache_time).seconds > 3600):  # Cache for 1 hour
            
            try:
                response = requests.get(self.jwks_uri, timeout=10)
                response.raise_for_status()
                self._jwks_cache = response.json()
                self._jwks_cache_time = now
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Unable to fetch JWKS: {str(e)}"
                )
        
        return self._jwks_cache
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token from Azure AD"""
        try:
            # Decode header to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing kid in header"
                )
            
            # Get JWKS and find matching key
            jwks = self.get_jwks()
            key = None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == kid:
                    key = jwk
                    break
            
            if not key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find matching key"
                )
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer
            )
            
            return payload
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication error"
            )


auth_service = AuthService()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user
    Returns user info from JWT token
    """
    if not settings.AZURE_TENANT_ID or not settings.AZURE_CLIENT_ID:
        # Require proper authentication in production
        if getattr(settings, 'ENVIRONMENT', 'development') == "production":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required. Azure AD must be configured in production."
            )
        # Development mode only - return mock user with limited permissions
        return {
            "sub": "dev-user",
            "name": "Development User",
            "email": "dev@example.com",
            "roles": ["user"]  # Limited role instead of admin
        }
    
    token = credentials.credentials
    user_info = auth_service.verify_token(token)
    
    return {
        "sub": user_info.get("sub"),
        "name": user_info.get("name"),
        "email": user_info.get("preferred_username") or user_info.get("email"),
        "roles": user_info.get("roles", [])
    }


def require_role(required_role: str):
    """
    Dependency factory to require specific role
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        if required_role not in user_roles and "admin" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        return current_user
    
    return role_checker


# Optional authentication - returns None if no token provided
def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """
    Optional authentication dependency
    Returns user info if token is provided and valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None