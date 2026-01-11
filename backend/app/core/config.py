from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str
    
    # Azure Entra ID
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_SUBSCRIPTION_ID: Optional[str] = None
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list[str] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Validate required settings
        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-change-in-production":
            if self.ENVIRONMENT == "production":
                raise ValueError("SECRET_KEY must be set to a secure value in production")
            else:
                # Generate a random key for development
                import secrets
                self.SECRET_KEY = secrets.token_urlsafe(32)
        
        # Set default CORS origins if not provided
        if not self.CORS_ORIGINS:
            if self.ENVIRONMENT == "production":
                # In production, CORS_ORIGINS must be explicitly set
                raise ValueError("CORS_ORIGINS must be explicitly configured in production")
            else:
                # Development defaults
                self.CORS_ORIGINS = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
