"""
Test configuration and fixtures
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import tempfile
import os

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.project import Project
from app.models.resource_group import ResourceGroup
from app.models.cloud_connection import CloudConnection


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Clean up tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {
        "sub": "test-user-123",
        "name": "Test User",
        "email": "test@example.com",
        "roles": ["user"]
    }


@pytest.fixture
def mock_admin_user():
    """Mock admin user."""
    return {
        "sub": "admin-user-123",
        "name": "Admin User",
        "email": "admin@example.com",
        "roles": ["admin"]
    }


@pytest.fixture
def auth_headers():
    """Authentication headers for test requests."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "project_name": "Test Project",
        "project_type": "External",
        "member_firm": "Test Corp",
        "deployed_region": "US",
        "description": "Test project description",
        "engagement_manager": "John Doe",
        "project_startdate": "2024-01-01",
        "project_enddate": "2024-12-31",
        "budget_allocated": 100000,
        "priority": "medium"
    }


@pytest.fixture
def sample_project(db_session: Session, sample_project_data):
    """Create a sample project in the database."""
    project = Project(**sample_project_data)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def sample_resource_group(db_session: Session, sample_project):
    """Create a sample resource group."""
    resource_group = ResourceGroup(
        resource_group_name="test-rg",
        project_id=sample_project.id,
        status="active"
    )
    db_session.add(resource_group)
    db_session.commit()
    db_session.refresh(resource_group)
    return resource_group


@pytest.fixture
def sample_cloud_connection(db_session: Session):
    """Create a sample cloud connection."""
    connection = CloudConnection(
        provider="aws",
        connection_name="test-aws",
        credentials={"access_key_id": "test", "secret_access_key": "test", "region": "us-east-1"},
        is_active=True
    )
    db_session.add(connection)
    db_session.commit()
    db_session.refresh(connection)
    return connection


@pytest.fixture
def mock_azure_openai_client(mocker):
    """Mock Azure OpenAI client."""
    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.choices = [mocker.MagicMock()]
    mock_response.choices[0].message.content = "Test AI response with SQL query: SELECT * FROM project;"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture(autouse=True)
def mock_auth_dependency(mocker, mock_user):
    """Auto-mock authentication for all tests."""
    mocker.patch("app.core.auth.get_current_user", return_value=mock_user)
    mocker.patch("app.core.auth.require_role", return_value=lambda: mock_user)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)


class MockAzureService:
    """Mock Azure service for testing."""
    
    def __init__(self):
        self.authenticated = True
    
    async def get_costs(self, start_date, end_date, subscription_id=None):
        return [
            {
                "date": "2024-01-01",
                "cost": 100.50,
                "currency": "USD",
                "service": "Virtual Machines"
            }
        ]
    
    async def get_resources(self, subscription_id=None):
        return [
            {
                "name": "test-vm",
                "type": "Microsoft.Compute/virtualMachines",
                "location": "eastus",
                "resource_group": "test-rg"
            }
        ]


@pytest.fixture
def mock_azure_service():
    """Mock Azure service."""
    return MockAzureService()


class MockAWSService:
    """Mock AWS service for testing."""
    
    def __init__(self):
        self.authenticated = True
    
    async def get_costs(self, start_date, end_date):
        return [
            {
                "date": "2024-01-01",
                "cost": 75.25,
                "currency": "USD",
                "service": "EC2-Instance"
            }
        ]
    
    async def get_resources(self):
        return [
            {
                "name": "test-instance",
                "type": "EC2 Instance",
                "region": "us-east-1",
                "state": "running"
            }
        ]


@pytest.fixture
def mock_aws_service():
    """Mock AWS service."""
    return MockAWSService()


@pytest.fixture
def mock_settings(mocker):
    """Mock settings for testing."""
    mock_settings = mocker.MagicMock()
    mock_settings.ENVIRONMENT = "test"
    mock_settings.SECRET_KEY = "test-secret-key"
    mock_settings.CORS_ORIGINS = ["http://localhost:3000"]
    mock_settings.AZURE_CLIENT_ID = "test-client-id"
    mock_settings.AZURE_TENANT_ID = "test-tenant-id"
    mock_settings.AZURE_OPENAI_API_KEY = "test-api-key"
    mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
    return mock_settings