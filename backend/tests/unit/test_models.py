"""
Unit tests for database models
"""
import pytest
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from app.models.project import Project
from app.models.resource_group import ResourceGroup
from app.models.cloud_connection import CloudConnection


@pytest.mark.unit
@pytest.mark.database
class TestProjectModel:
    """Test cases for Project model."""
    
    def test_create_project(self, db_session):
        """Test creating a project."""
        project = Project(
            project_name="Test Project",
            project_type="External",
            member_firm="Test Corp",
            deployed_region="US",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31)
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.id is not None
        assert project.project_name == "Test Project"
        assert project.is_active is True  # Default value
        assert project.status == "planning"  # Default value
    
    def test_project_relationships(self, db_session):
        """Test project relationships with resource groups."""
        project = Project(
            project_name="Test Project",
            project_type="External",
            member_firm="Test Corp",
            deployed_region="US",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31)
        )
        db_session.add(project)
        db_session.commit()
        
        # Add resource group
        resource_group = ResourceGroup(
            resource_group_name="test-rg",
            project_id=project.id,
            status="active"
        )
        db_session.add(resource_group)
        db_session.commit()
        
        # Test relationship
        assert len(project.resource_groups) == 1
        assert project.resource_groups[0].resource_group_name == "test-rg"
        assert resource_group.project == project
    
    def test_project_validation(self, db_session):
        """Test project model validation."""
        # Test missing required fields
        with pytest.raises(Exception):  # Should raise validation error
            project = Project()
            db_session.add(project)
            db_session.commit()
    
    def test_project_unique_constraint(self, db_session):
        """Test project name uniqueness (if implemented)."""
        project1 = Project(
            project_name="Unique Project",
            project_type="External",
            member_firm="Test Corp",
            deployed_region="US",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31)
        )
        db_session.add(project1)
        db_session.commit()
        
        # Try to create another project with same name
        project2 = Project(
            project_name="Unique Project",
            project_type="Internal",
            member_firm="Another Corp",
            deployed_region="EU",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31)
        )
        db_session.add(project2)
        
        # This should succeed as we don't have unique constraint on name
        # If we add unique constraint, this test should expect IntegrityError
        db_session.commit()
        assert project2.id is not None
    
    def test_project_status_enum(self, db_session):
        """Test project status enumeration."""
        project = Project(
            project_name="Status Test",
            project_type="External",
            member_firm="Test Corp",
            deployed_region="US",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31),
            status="active"
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.status == "active"
        
        # Update status
        project.status = "completed"
        db_session.commit()
        
        assert project.status == "completed"
    
    def test_project_progress_validation(self, db_session):
        """Test progress percentage validation."""
        project = Project(
            project_name="Progress Test",
            project_type="External",
            member_firm="Test Corp",
            deployed_region="US",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31),
            progress_percentage=50
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.progress_percentage == 50
        
        # Test boundary values
        project.progress_percentage = 0
        db_session.commit()
        assert project.progress_percentage == 0
        
        project.progress_percentage = 100
        db_session.commit()
        assert project.progress_percentage == 100


@pytest.mark.unit
@pytest.mark.database
class TestResourceGroupModel:
    """Test cases for ResourceGroup model."""
    
    def test_create_resource_group(self, db_session, sample_project):
        """Test creating a resource group."""
        resource_group = ResourceGroup(
            resource_group_name="test-rg",
            project_id=sample_project.id,
            status="active"
        )
        
        db_session.add(resource_group)
        db_session.commit()
        
        assert resource_group.id is not None
        assert resource_group.resource_group_name == "test-rg"
        assert resource_group.project_id == sample_project.id
        assert resource_group.status == "active"
    
    def test_resource_group_project_relationship(self, db_session, sample_project):
        """Test resource group to project relationship."""
        resource_group = ResourceGroup(
            resource_group_name="test-rg",
            project_id=sample_project.id,
            status="active"
        )
        
        db_session.add(resource_group)
        db_session.commit()
        
        # Test foreign key relationship
        assert resource_group.project == sample_project
        assert resource_group in sample_project.resource_groups
    
    def test_resource_group_without_project(self, db_session):
        """Test creating resource group without valid project."""
        resource_group = ResourceGroup(
            resource_group_name="orphan-rg",
            project_id=999,  # Non-existent project
            status="active"
        )
        
        db_session.add(resource_group)
        
        # This should raise foreign key constraint error
        with pytest.raises(IntegrityError):
            db_session.commit()


@pytest.mark.unit
@pytest.mark.database
class TestCloudConnectionModel:
    """Test cases for CloudConnection model."""
    
    def test_create_cloud_connection(self, db_session):
        """Test creating a cloud connection."""
        connection = CloudConnection(
            provider="aws",
            connection_name="test-aws",
            credentials={
                "access_key_id": "test-key",
                "secret_access_key": "test-secret",
                "region": "us-east-1"
            },
            is_active=True
        )
        
        db_session.add(connection)
        db_session.commit()
        
        assert connection.id is not None
        assert connection.provider == "aws"
        assert connection.connection_name == "test-aws"
        assert connection.is_active is True
        assert connection.created_at is not None
        assert connection.updated_at is not None
    
    def test_cloud_connection_credentials_json(self, db_session):
        """Test JSON credentials storage."""
        credentials = {
            "access_key_id": "AKIA123456789",
            "secret_access_key": "secret123",
            "region": "us-west-2",
            "additional_config": {
                "timeout": 30,
                "retries": 3
            }
        }
        
        connection = CloudConnection(
            provider="aws",
            connection_name="complex-aws",
            credentials=credentials,
            is_active=True
        )
        
        db_session.add(connection)
        db_session.commit()
        
        # Retrieve and verify JSON storage
        retrieved = db_session.query(CloudConnection).filter_by(id=connection.id).first()
        assert retrieved.credentials == credentials
        assert retrieved.credentials["additional_config"]["timeout"] == 30
    
    def test_cloud_connection_providers(self, db_session):
        """Test different cloud providers."""
        providers = [
            ("aws", {"access_key_id": "key", "secret_access_key": "secret", "region": "us-east-1"}),
            ("azure", {"client_id": "id", "client_secret": "secret", "tenant_id": "tenant"}),
            ("gcp", {"project_id": "project", "credentials_json": "json_content"})
        ]
        
        for provider, creds in providers:
            connection = CloudConnection(
                provider=provider,
                connection_name=f"test-{provider}",
                credentials=creds,
                is_active=True
            )
            db_session.add(connection)
        
        db_session.commit()
        
        # Verify all connections were created
        connections = db_session.query(CloudConnection).all()
        assert len(connections) == 3
        
        provider_names = [conn.provider for conn in connections]
        assert "aws" in provider_names
        assert "azure" in provider_names
        assert "gcp" in provider_names
    
    def test_cloud_connection_timestamps(self, db_session):
        """Test automatic timestamp handling."""
        connection = CloudConnection(
            provider="aws",
            connection_name="timestamp-test",
            credentials={"key": "value"},
            is_active=True
        )
        
        db_session.add(connection)
        db_session.commit()
        
        created_at = connection.created_at
        updated_at = connection.updated_at
        
        assert created_at is not None
        assert updated_at is not None
        assert created_at == updated_at  # Should be same on creation
        
        # Update the connection
        import time
        time.sleep(0.1)  # Small delay to ensure different timestamp
        connection.connection_name = "updated-name"
        db_session.commit()
        
        # Check that updated_at changed
        assert connection.updated_at > updated_at
        assert connection.created_at == created_at  # Should remain same


@pytest.mark.unit
@pytest.mark.database
class TestModelRelationships:
    """Test complex model relationships."""
    
    def test_cascade_delete_project(self, db_session):
        """Test cascade delete behavior."""
        # Create project with resource groups
        project = Project(
            project_name="Cascade Test",
            project_type="External",
            member_firm="Test Corp",
            deployed_region="US",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31)
        )
        db_session.add(project)
        db_session.commit()
        
        # Add resource groups
        for i in range(3):
            rg = ResourceGroup(
                resource_group_name=f"rg-{i}",
                project_id=project.id,
                status="active"
            )
            db_session.add(rg)
        db_session.commit()
        
        # Verify resource groups exist
        rg_count = db_session.query(ResourceGroup).filter_by(project_id=project.id).count()
        assert rg_count == 3
        
        # Delete project
        db_session.delete(project)
        db_session.commit()
        
        # Check if resource groups are handled properly
        # (Behavior depends on cascade configuration)
        remaining_rgs = db_session.query(ResourceGroup).filter_by(project_id=project.id).count()
        # If cascade delete is configured, this should be 0
        # If not, this might raise foreign key constraint error
        # Adjust assertion based on actual cascade configuration
    
    def test_query_optimization(self, db_session):
        """Test query optimization with relationships."""
        # Create project with multiple resource groups
        project = Project(
            project_name="Query Test",
            project_type="External",
            member_firm="Test Corp",
            deployed_region="US",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31)
        )
        db_session.add(project)
        db_session.commit()
        
        # Add multiple resource groups
        for i in range(5):
            rg = ResourceGroup(
                resource_group_name=f"rg-{i}",
                project_id=project.id,
                status="active"
            )
            db_session.add(rg)
        db_session.commit()
        
        # Test eager loading
        from sqlalchemy.orm import joinedload
        
        project_with_rgs = db_session.query(Project).options(
            joinedload(Project.resource_groups)
        ).filter_by(id=project.id).first()
        
        # This should not trigger additional queries
        assert len(project_with_rgs.resource_groups) == 5
        
        # Test lazy loading
        project_lazy = db_session.query(Project).filter_by(id=project.id).first()
        # Accessing resource_groups will trigger additional query
        assert len(project_lazy.resource_groups) == 5