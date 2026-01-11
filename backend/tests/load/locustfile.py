"""
Load testing with Locust
"""
import json
import random
from locust import HttpUser, task, between


class DashboardUser(HttpUser):
    """Simulate dashboard user behavior."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup for each user."""
        self.headers = {
            "Authorization": "Bearer demo-token",
            "Content-Type": "application/json"
        }
        
        # Test authentication
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"Health check failed: {response.status_code}")
    
    @task(3)
    def view_dashboard(self):
        """View dashboard summary."""
        self.client.get("/api/dashboard/summary", headers=self.headers)
    
    @task(5)
    def list_projects(self):
        """List projects with various filters."""
        params = {}
        
        # Randomly add filters
        if random.choice([True, False]):
            params['status'] = random.choice(['active', 'planning', 'completed'])
        
        if random.choice([True, False]):
            params['region'] = random.choice(['US', 'EU', 'APAC'])
        
        if random.choice([True, False]):
            params['limit'] = random.choice([10, 25, 50])
        
        self.client.get("/api/projects/", params=params, headers=self.headers)
    
    @task(2)
    def view_project_details(self):
        """View specific project details."""
        # Get a random project ID (assuming projects exist)
        project_id = random.randint(1, 10)
        response = self.client.get(f"/api/projects/{project_id}", headers=self.headers)
        
        if response.status_code == 200:
            # Also get status history
            self.client.get(f"/api/projects/{project_id}/status-history", headers=self.headers)
    
    @task(1)
    def create_project(self):
        """Create a new project."""
        project_data = {
            "project_name": f"Load Test Project {random.randint(1000, 9999)}",
            "project_type": random.choice(["External", "Internal", "Client Demo"]),
            "member_firm": f"Test Corp {random.randint(1, 100)}",
            "deployed_region": random.choice(["US", "EU", "APAC"]),
            "description": "Project created during load testing",
            "engagement_manager": f"Manager {random.randint(1, 50)}",
            "project_startdate": "2024-01-01",
            "project_enddate": "2024-12-31",
            "budget_allocated": random.randint(50000, 500000),
            "priority": random.choice(["low", "medium", "high", "critical"])
        }
        
        self.client.post("/api/projects/", json=project_data, headers=self.headers)
    
    @task(1)
    def update_project_status(self):
        """Update project status."""
        project_id = random.randint(1, 10)
        status_data = {
            "status": random.choice(["planning", "active", "on_hold", "completed"]),
            "progress_percentage": random.randint(0, 100),
            "health_status": random.choice(["green", "yellow", "red"]),
            "status_notes": f"Updated during load test at {random.randint(1000, 9999)}"
        }
        
        self.client.patch(f"/api/projects/{project_id}/status", json=status_data, headers=self.headers)
    
    @task(2)
    def chat_query(self):
        """Send chat queries."""
        queries = [
            "Show me all active projects",
            "What are the total costs by region?",
            "Which projects are behind schedule?",
            "List projects ending this month",
            "Show me project status summary",
            "What is the average project budget?",
            "How many projects are in each region?",
            "Show me the most expensive projects"
        ]
        
        chat_data = {
            "message": random.choice(queries),
            "conversation_id": f"load-test-{self.environment.runner.user_count}-{random.randint(1, 1000)}"
        }
        
        self.client.post("/api/chat/", json=chat_data, headers=self.headers)
    
    @task(1)
    def view_costs(self):
        """View cost data."""
        params = {}
        
        # Randomly filter by project
        if random.choice([True, False]):
            params['project_id'] = random.randint(1, 10)
        
        self.client.get("/api/costs/", params=params, headers=self.headers)
    
    @task(1)
    def view_resource_groups(self):
        """View resource groups."""
        self.client.get("/api/resource-groups/", headers=self.headers)
    
    @task(1)
    def test_cloud_providers(self):
        """Test cloud provider endpoints."""
        self.client.get("/api/cloud-providers/", headers=self.headers)


class AdminUser(HttpUser):
    """Simulate admin user behavior with more privileged operations."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Setup for admin user."""
        self.headers = {
            "Authorization": "Bearer admin-token",
            "Content-Type": "application/json"
        }
    
    @task(2)
    def admin_dashboard_view(self):
        """Admin views dashboard."""
        self.client.get("/api/dashboard/summary", headers=self.headers)
    
    @task(1)
    def delete_project(self):
        """Admin deletes projects."""
        # Try to delete a project (might not exist)
        project_id = random.randint(100, 200)  # Use higher IDs to avoid deleting test data
        self.client.delete(f"/api/projects/{project_id}", headers=self.headers)
    
    @task(1)
    def manage_cloud_connections(self):
        """Admin manages cloud connections."""
        # Test connection
        test_data = {
            "provider": "aws",
            "credentials": {
                "access_key_id": "test-key",
                "secret_access_key": "test-secret",
                "region": "us-east-1"
            }
        }
        
        self.client.post("/api/cloud-providers/test-connection", json=test_data, headers=self.headers)
    
    @task(1)
    def bulk_operations(self):
        """Admin performs bulk operations."""
        # Simulate bulk project creation
        for i in range(3):
            project_data = {
                "project_name": f"Bulk Project {random.randint(10000, 99999)}",
                "project_type": "Internal",
                "member_firm": "Admin Corp",
                "deployed_region": random.choice(["US", "EU", "APAC"]),
                "project_startdate": "2024-01-01",
                "project_enddate": "2024-12-31"
            }
            
            self.client.post("/api/projects/", json=project_data, headers=self.headers)


class APIStressUser(HttpUser):
    """Stress test specific API endpoints."""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    def on_start(self):
        """Setup for stress testing."""
        self.headers = {
            "Authorization": "Bearer demo-token",
            "Content-Type": "application/json"
        }
    
    @task(10)
    def rapid_project_list(self):
        """Rapidly list projects."""
        self.client.get("/api/projects/", headers=self.headers)
    
    @task(5)
    def rapid_dashboard_access(self):
        """Rapidly access dashboard."""
        self.client.get("/api/dashboard/summary", headers=self.headers)
    
    @task(3)
    def rapid_chat_queries(self):
        """Rapid chat queries."""
        chat_data = {
            "message": "Quick query",
            "conversation_id": f"stress-{random.randint(1, 100)}"
        }
        
        self.client.post("/api/chat/", json=chat_data, headers=self.headers)
    
    @task(1)
    def test_rate_limiting(self):
        """Test rate limiting by making many requests."""
        for i in range(10):
            response = self.client.get("/health")
            if response.status_code == 429:
                print(f"Rate limit hit after {i} requests")
                break


class SecurityTestUser(HttpUser):
    """Test security aspects of the API."""
    
    wait_time = between(1, 2)
    
    @task(1)
    def test_no_auth(self):
        """Test endpoints without authentication."""
        # These should return 401
        self.client.get("/api/projects/")
        self.client.get("/api/dashboard/summary")
        self.client.post("/api/chat/", json={"message": "test"})
    
    @task(1)
    def test_invalid_auth(self):
        """Test with invalid authentication."""
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        
        self.client.get("/api/projects/", headers=invalid_headers)
        self.client.get("/api/dashboard/summary", headers=invalid_headers)
    
    @task(1)
    def test_malicious_input(self):
        """Test with potentially malicious input."""
        headers = {"Authorization": "Bearer demo-token", "Content-Type": "application/json"}
        
        # SQL injection attempts
        malicious_chat = {
            "message": "'; DROP TABLE projects; --",
            "conversation_id": "malicious"
        }
        self.client.post("/api/chat/", json=malicious_chat, headers=headers)
        
        # XSS attempts
        malicious_project = {
            "project_name": "<script>alert('xss')</script>",
            "project_type": "External",
            "member_firm": "Test Corp",
            "deployed_region": "US",
            "project_startdate": "2024-01-01",
            "project_enddate": "2024-12-31"
        }
        self.client.post("/api/projects/", json=malicious_project, headers=headers)
    
    @task(1)
    def test_parameter_tampering(self):
        """Test parameter tampering."""
        headers = {"Authorization": "Bearer demo-token"}
        
        # Invalid parameters
        self.client.get("/api/projects/?skip=-1&limit=0", headers=headers)
        self.client.get("/api/projects/?limit=99999", headers=headers)
        self.client.get("/api/projects/?status=invalid_status", headers=headers)