# Multi-Cloud Operations Dashboard API Documentation

## Overview

The Multi-Cloud Operations Dashboard API is a comprehensive REST API for managing multi-cloud operations, projects, costs, and resources. It provides secure, authenticated access to project management, cost tracking, AI-powered querying, and cloud provider integration.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

## Interactive Documentation

The API provides interactive documentation through Swagger UI and ReDoc:

- **Swagger UI**: `{BASE_URL}/docs`
- **ReDoc**: `{BASE_URL}/redoc`
- **OpenAPI Schema**: `{BASE_URL}/openapi.json`

## Authentication

### Azure Active Directory (Production)

The API uses Azure Active Directory for authentication in production environments. Include your JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Development Mode

In development mode (when Azure AD is not configured), the API uses a mock authentication system for testing purposes.

### Authentication Flow

1. **Obtain JWT Token**: Authenticate with Azure AD to get a JWT token
2. **Include in Requests**: Add the token to the Authorization header
3. **Token Validation**: The API validates the token with Azure AD JWKS
4. **Role-Based Access**: Different endpoints require different role levels

## Rate Limiting

- **Limit**: 100 requests per minute per IP address
- **Headers**: Rate limit information is included in response headers
- **Exceeded**: Returns HTTP 429 when limit is exceeded

## Security Features

- **Authentication**: Azure AD JWT token validation
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Protection**: Enhanced query validation
- **CORS Protection**: Restricted origins and methods
- **Security Headers**: Comprehensive security headers
- **Rate Limiting**: Protection against abuse

## API Endpoints

### Health & Status

#### GET /
Get basic API information and links to documentation.

**Response:**
```json
{
  "message": "Multi-Cloud Operations Dashboard API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

#### GET /health
Health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-11T10:30:00Z",
  "version": "1.0.0"
}
```

### Projects

#### GET /api/projects/
Retrieve a paginated list of projects with optional filtering.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (1-1000, default: 100)
- `status` (string): Filter by status (planning, active, on-hold, completed, cancelled)
- `region` (string): Filter by region (US, EU, APAC)

**Authentication:** Required (any authenticated user)

**Example Request:**
```http
GET /api/projects/?limit=10&status=active&region=US
Authorization: Bearer <token>
```

**Example Response:**
```json
[
  {
    "id": 1,
    "project_name": "Cloud Migration Project",
    "project_type": "External",
    "member_firm": "Acme Corp",
    "deployed_region": "US",
    "is_active": true,
    "description": "Migrate legacy systems to cloud",
    "engagement_manager": "John Doe",
    "project_startdate": "2024-01-01",
    "project_enddate": "2024-12-31",
    "status": "active",
    "progress_percentage": 45,
    "budget_allocated": 100000,
    "budget_spent": 45000,
    "priority": "high",
    "health_status": "green"
  }
]
```

#### POST /api/projects/
Create a new project.

**Authentication:** Required (user role or higher)

**Request Body:**
```json
{
  "project_name": "New Cloud Project",
  "project_type": "External",
  "member_firm": "Client Corp",
  "deployed_region": "US",
  "description": "New project description",
  "engagement_manager": "Jane Smith",
  "project_startdate": "2024-01-01",
  "project_enddate": "2024-12-31",
  "budget_allocated": 100000,
  "priority": "high"
}
```

#### GET /api/projects/{project_id}
Get a specific project by ID.

**Authentication:** Required (any authenticated user)

#### PUT /api/projects/{project_id}
Update an existing project.

**Authentication:** Required (user role or higher)

#### PATCH /api/projects/{project_id}/status
Update project status and related fields.

**Authentication:** Required (user role or higher)

**Request Body:**
```json
{
  "status": "active",
  "progress_percentage": 75,
  "health_status": "green",
  "status_notes": "Project is progressing well"
}
```

#### DELETE /api/projects/{project_id}
Delete a project.

**Authentication:** Required (admin role)

### AI Chat Interface

#### POST /api/chat/
Send a natural language query to get AI-powered responses with SQL execution.

**Authentication:** Required (any authenticated user)

**Request Body:**
```json
{
  "message": "Show me all active projects in the US region",
  "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**
```json
{
  "response": "I found 3 active projects in the US region:\n\n1. Cloud Migration Project - 75% complete\n2. Infrastructure Modernization - 60% complete\n3. Security Upgrade - 30% complete",
  "sql_query": "SELECT project_name, progress_percentage FROM project WHERE is_active = true AND deployed_region = 'US' ORDER BY progress_percentage DESC;",
  "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000"
}
```

**Example Queries:**
- "Show me all active projects"
- "What's the total cost by region?"
- "Which projects are over budget?"
- "List projects ending this month"
- "Show resource groups with highest costs"

**Security Features:**
- Only SELECT queries allowed
- SQL injection protection
- Query validation and sanitization
- Result size limits (max 1000 rows)
- Query length limits (max 2000 characters)

### Cost Management

#### GET /api/costs/
Retrieve cost data with filtering options.

**Query Parameters:**
- `project_id` (int): Filter by project
- `resource_group_id` (int): Filter by resource group
- `start_date` (date): Start date for cost data
- `end_date` (date): End date for cost data

#### POST /api/costs/
Add new cost data.

**Authentication:** Required (user role or higher)

### Resource Groups

#### GET /api/resource-groups/
Get all resource groups with optional filtering.

#### POST /api/resource-groups/
Create a new resource group.

**Authentication:** Required (user role or higher)

### Dashboard Analytics

#### GET /api/dashboard/summary
Get dashboard summary with key metrics.

**Response:**
```json
{
  "total_projects": 25,
  "active_projects": 18,
  "total_cost": 1250000,
  "monthly_cost": 85000,
  "projects_by_region": {
    "US": 12,
    "EU": 8,
    "APAC": 5
  },
  "projects_by_status": {
    "active": 18,
    "planning": 4,
    "completed": 3
  }
}
```

### Cloud Provider Integration

#### GET /api/cloud-providers/
List configured cloud provider connections.

#### POST /api/cloud-providers/
Add a new cloud provider connection.

**Authentication:** Required (admin role)

#### POST /api/cloud-providers/test-connection
Test cloud provider connection.

**Request Body:**
```json
{
  "provider": "aws",
  "credentials": {
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "region": "us-east-1"
  }
}
```

#### GET /api/cloud-providers/{provider_id}/costs
Retrieve costs from a specific cloud provider.

### Azure Integration

#### POST /api/azure/costs
Get Azure cost data for a specific date range.

**Request Body:**
```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "subscription_id": "12345678-1234-1234-1234-123456789012"
}
```

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses:

### Success Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content returned

### Client Error Codes
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded

### Server Error Codes
- `500 Internal Server Error`: Server error (generic message returned)
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format
```json
{
  "detail": "Error message",
  "type": "error_type",
  "code": "ERROR_CODE"
}
```

## Data Models

### Project Model
```json
{
  "id": 1,
  "project_name": "string",
  "project_type": "External|Internal|Client Demo",
  "member_firm": "string",
  "deployed_region": "US|EU|APAC",
  "is_active": true,
  "description": "string",
  "engagement_code": "string",
  "engagement_partner": "string",
  "opportunity_code": "string",
  "engagement_manager": "string",
  "project_startdate": "2024-01-01",
  "project_enddate": "2024-12-31",
  "status": "planning|active|on_hold|completed|cancelled",
  "progress_percentage": 45,
  "budget_allocated": 100000,
  "budget_spent": 45000,
  "priority": "low|medium|high|critical",
  "health_status": "green|yellow|red",
  "last_status_update": "2024-01-15",
  "status_notes": "string"
}
```

### Chat Message Model
```json
{
  "message": "string (1-1000 chars)",
  "conversation_id": "string (optional)"
}
```

### Chat Response Model
```json
{
  "response": "string",
  "sql_query": "string (optional)",
  "conversation_id": "string"
}
```

## Validation Rules

### Project Validation
- **project_name**: 1-200 characters, must be unique
- **project_type**: Must be "Internal", "External", or "Client Demo"
- **deployed_region**: Must be "US", "EU", or "APAC"
- **project_enddate**: Must be after project_startdate
- **progress_percentage**: 0-100
- **budget_allocated**: Non-negative integer
- **budget_spent**: Non-negative integer

### Chat Validation
- **message**: 1-1000 characters, no HTML/script tags
- **conversation_id**: Alphanumeric, hyphens, underscores only

## Rate Limiting Details

### Limits
- **Global**: 100 requests per minute per IP
- **Chat Endpoint**: Additional AI service limits may apply
- **Burst**: Short bursts allowed up to limit

### Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641902400
```

## Security Best Practices

### For API Consumers
1. **Secure Token Storage**: Store JWT tokens securely
2. **Token Refresh**: Implement token refresh logic
3. **HTTPS Only**: Always use HTTPS in production
4. **Input Validation**: Validate data before sending
5. **Error Handling**: Handle all error responses gracefully

### For API Administrators
1. **Monitor Usage**: Track API usage and patterns
2. **Log Analysis**: Monitor logs for suspicious activity
3. **Rate Limit Tuning**: Adjust limits based on usage
4. **Security Updates**: Keep dependencies updated
5. **Access Reviews**: Regular review of user access

## SDK and Client Libraries

### Python Example
```python
import requests

class DashboardAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_projects(self, status=None, region=None):
        params = {}
        if status:
            params['status'] = status
        if region:
            params['region'] = region
        
        response = requests.get(
            f"{self.base_url}/api/projects/",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def chat_query(self, message, conversation_id=None):
        data = {"message": message}
        if conversation_id:
            data["conversation_id"] = conversation_id
        
        response = requests.post(
            f"{self.base_url}/api/chat/",
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage
api = DashboardAPI("http://localhost:8000", "your-jwt-token")
projects = api.get_projects(status="active", region="US")
chat_response = api.chat_query("Show me all active projects")
```

### JavaScript Example
```javascript
class DashboardAPI {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getProjects(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(
            `${this.baseUrl}/api/projects/?${params}`,
            { headers: this.headers }
        );
        return response.json();
    }
    
    async chatQuery(message, conversationId = null) {
        const data = { message };
        if (conversationId) {
            data.conversation_id = conversationId;
        }
        
        const response = await fetch(
            `${this.baseUrl}/api/chat/`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(data)
            }
        );
        return response.json();
    }
}

// Usage
const api = new DashboardAPI('http://localhost:8000', 'your-jwt-token');
const projects = await api.getProjects({ status: 'active', region: 'US' });
const chatResponse = await api.chatQuery('Show me all active projects');
```

## Testing

### Manual Testing
Access the interactive documentation at `/docs` to test endpoints manually.

### Automated Testing
```bash
# Test health endpoint
curl -X GET "http://localhost:8000/health"

# Test projects endpoint (requires auth)
curl -X GET "http://localhost:8000/api/projects/" \
  -H "Authorization: Bearer your-token"

# Test chat endpoint
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all projects"}'
```

## Support and Contact

- **Documentation**: Available at `/docs` and `/redoc`
- **Issues**: Create issues in the project repository
- **Security**: Follow responsible disclosure for security issues
- **API Support**: Contact the development team

## Changelog

### Version 1.0.0
- Initial API release
- Project management endpoints
- AI chat interface
- Cost management
- Cloud provider integration
- Comprehensive security features
- Interactive documentation