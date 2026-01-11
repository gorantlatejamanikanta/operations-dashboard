"""
Integration tests for projects API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.project import Project


@pytest.mark.integration
@pytest.mark.api
class TestProjectsAPI:
    """Integration tests for projects API endpoints."""
    
    def test_get_projects_empty(self, client: TestClient, auth_headers):
        """Test getting projects when database is empty."""
        response = client.get("/api/projects/", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_projects_with_data(self, client: TestClient, auth_headers, sample_project):
        """Test getting projects with data in database."""
        response = client.get("/api/projects/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["project_name"] == sample_project.project_name
        assert data[0]["id"] == sample_project.id
    
    def test_get_projects_pagination(self, client: TestClient, auth_headers, db_session: Session):
        """Test projects pagination."""
        # Create multiple projects
        for i in range(5):
            project = Project(
                project_name=f"Test Project {i}",
                project_type="External",
                member_firm="Test Corp",
                deployed_region="US",
                project_startdate="2024-01-01",
                project_enddate="2024-12-31"
            )
            db_session.add(project)
        db_session.commit()
        
        # Test pagination
        response = client.get("/api/projects/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        response = client.get("/api/projects/?skip=3&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_projects_filtering(self, client: TestClient, auth_headers, db_session: Session):
        """Test projects filtering by status and region."""
        # Create projects with different statuses and regions
        projects_data = [
            {"project_name": "US Active", "deployed_region": "US", "is_active": True},
            {"project_name": "EU Active", "deployed_region": "EU", "is_active": True},
            {"project_name": "US Inactive", "deployed_region": "US", "is_active": False},
        ]
        
        for data in projects_data:
            project = Project(
                project_type="External",
                member_firm="Test Corp",
                project_startdate="2024-01-01",
                project_enddate="2024-12-31",
                **data
            )
            db_session.add(project)
        db_session.commit()
        
        # Test region filtering
        response = client.get("/api/projects/?region=US", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["deployed_region"] == "US" for p in data)
        
        # Test status filtering (using is_active as proxy for status)
        response = client.get("/api/projects/?region=US", headers=auth_headers)
        us_projects = response.json()
        active_us_projects = [p for p in us_projects if p["is_active"]]
        assert len(active_us_projects) == 1
    
    def test_get_project_by_id(self, client: TestClient, auth_headers, sample_project):
        """Test getting a specific project by ID."""
        response = client.get(f"/api/projects/{sample_project.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_project.id
        assert data["project_name"] == sample_project.project_name
    
    def test_get_project_not_found(self, client: TestClient, auth_headers):
        """Test getting a non-existent project."""
        response = client.get("/api/projects/999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Project not found" in response.json()["detail"]
    
    def test_create_project(self, client: TestClient, auth_headers, sample_project_data):
        """Test creating a new project."""
        response = client.post("/api/projects/", json=sample_project_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == sample_project_data["project_name"]
        assert data["project_type"] == sample_project_data["project_type"]
        assert "id" in data
    
    def test_create_project_validation_error(self, client: TestClient, auth_headers):
        """Test creating a project with validation errors."""
        invalid_data = {
            "project_name": "",  # Empty name
            "project_type": "Invalid Type",  # Invalid type
            "deployed_region": "INVALID",  # Invalid region
        }
        
        response = client.post("/api/projects/", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("project_name" in str(error) for error in errors)
    
    def test_update_project(self, client: TestClient, auth_headers, sample_project):
        """Test updating an existing project."""
        update_data = {
            "description": "Updated description",
            "progress_percentage": 50
        }
        
        response = client.put(f"/api/projects/{sample_project.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["progress_percentage"] == 50
    
    def test_update_project_not_found(self, client: TestClient, auth_headers):
        """Test updating a non-existent project."""
        update_data = {"description": "Updated"}
        
        response = client.put("/api/projects/999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_project_status(self, client: TestClient, auth_headers, sample_project):
        """Test updating project status."""
        status_data = {
            "status": "active",
            "progress_percentage": 75,
            "health_status": "green",
            "status_notes": "Project is on track"
        }
        
        response = client.patch(f"/api/projects/{sample_project.id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["progress_percentage"] == 75
        assert data["health_status"] == "green"
        assert data["status_notes"] == "Project is on track"
    
    def test_update_project_status_invalid_progress(self, client: TestClient, auth_headers, sample_project):
        """Test updating project status with invalid progress percentage."""
        status_data = {
            "status": "active",
            "progress_percentage": 150  # Invalid: > 100
        }
        
        response = client.patch(f"/api/projects/{sample_project.id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Progress percentage must be between 0 and 100" in response.json()["detail"]
    
    def test_get_project_status_history(self, client: TestClient, auth_headers, sample_project):
        """Test getting project status history."""
        response = client.get(f"/api/projects/{sample_project.id}/status-history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == sample_project.id
        assert "current_status" in data
        assert "last_update" in data
    
    def test_delete_project(self, client: TestClient, auth_headers, sample_project, mocker):
        """Test deleting a project."""
        # Mock admin user for delete operation
        mock_admin = {"roles": ["admin"], "sub": "admin", "name": "Admin", "email": "admin@test.com"}
        mocker.patch("app.core.auth.require_role", return_value=lambda: mock_admin)
        
        response = client.delete(f"/api/projects/{sample_project.id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify project is deleted
        get_response = client.get(f"/api/projects/{sample_project.id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_project_not_found(self, client: TestClient, auth_headers, mocker):
        """Test deleting a non-existent project."""
        # Mock admin user
        mock_admin = {"roles": ["admin"], "sub": "admin", "name": "Admin", "email": "admin@test.com"}
        mocker.patch("app.core.auth.require_role", return_value=lambda: mock_admin)
        
        response = client.delete("/api/projects/999", headers=auth_headers)
        
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
class TestProjectsAPISecurity:
    """Security tests for projects API."""
    
    def test_get_projects_without_auth(self, client: TestClient, mocker):
        """Test accessing projects without authentication."""
        # Remove auth mock
        mocker.patch("app.core.auth.get_current_user", side_effect=Exception("No auth"))
        
        response = client.get("/api/projects/")
        
        assert response.status_code == 401
    
    def test_create_project_insufficient_role(self, client: TestClient, auth_headers, mocker):
        """Test creating project with insufficient role."""
        # Mock user without required role
        mocker.patch("app.core.auth.require_role", side_effect=Exception("Insufficient permissions"))
        
        project_data = {
            "project_name": "Test Project",
            "project_type": "External",
            "member_firm": "Test Corp",
            "deployed_region": "US",
            "project_startdate": "2024-01-01",
            "project_enddate": "2024-12-31"
        }
        
        response = client.post("/api/projects/", json=project_data, headers=auth_headers)
        
        assert response.status_code == 500  # Exception handling
    
    def test_input_validation_sql_injection(self, client: TestClient, auth_headers):
        """Test input validation against SQL injection attempts."""
        malicious_data = {
            "project_name": "Test'; DROP TABLE projects; --",
            "project_type": "External",
            "member_firm": "Test Corp",
            "deployed_region": "US",
            "project_startdate": "2024-01-01",
            "project_enddate": "2024-12-31"
        }
        
        response = client.post("/api/projects/", json=malicious_data, headers=auth_headers)
        
        # Should either succeed (input sanitized) or fail validation
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            # If created, verify the malicious content was sanitized
            data = response.json()
            assert "DROP TABLE" not in data["project_name"]
    
    def test_parameter_validation(self, client: TestClient, auth_headers):
        """Test parameter validation for query parameters."""
        # Test negative skip
        response = client.get("/api/projects/?skip=-1", headers=auth_headers)
        assert response.status_code == 400
        
        # Test invalid limit
        response = client.get("/api/projects/?limit=0", headers=auth_headers)
        assert response.status_code == 400
        
        # Test limit too high
        response = client.get("/api/projects/?limit=2000", headers=auth_headers)
        assert response.status_code == 400
        
        # Test invalid status
        response = client.get("/api/projects/?status=invalid_status", headers=auth_headers)
        assert response.status_code == 400
        
        # Test invalid region
        response = client.get("/api/projects/?region=INVALID", headers=auth_headers)
        assert response.status_code == 400