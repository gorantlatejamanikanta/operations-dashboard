# Swagger/OpenAPI Documentation Guide

## Overview

The Multi-Cloud Operations Dashboard API provides comprehensive interactive documentation through Swagger UI and ReDoc. This guide explains how to access, use, and customize the API documentation.

## Accessing the Documentation

### Swagger UI (Interactive)
- **URL**: `http://localhost:8000/docs`
- **Features**: Interactive testing, request/response examples, schema exploration
- **Best for**: API testing, development, learning the API

### ReDoc (Documentation)
- **URL**: `http://localhost:8000/redoc`
- **Features**: Clean documentation layout, detailed descriptions, code examples
- **Best for**: API reference, integration planning, documentation sharing

### OpenAPI Schema (JSON)
- **URL**: `http://localhost:8000/openapi.json`
- **Features**: Machine-readable API specification
- **Best for**: Code generation, API tooling, automated testing

## Swagger UI Features

### 1. Interactive Testing
- **Try it out**: Click "Try it out" on any endpoint to test it directly
- **Authentication**: Use the "Authorize" button to set your JWT token
- **Parameters**: Fill in required and optional parameters
- **Execute**: Click "Execute" to send the request and see the response

### 2. Authentication Setup
```
1. Click the "Authorize" button (lock icon) at the top
2. Enter your JWT token in the format: Bearer <your-token>
3. Click "Authorize"
4. All subsequent requests will include the token
```

### 3. Request Examples
Each endpoint includes:
- **Request body examples** with sample data
- **Parameter descriptions** with validation rules
- **Response examples** for different status codes
- **Schema definitions** for all data models

### 4. Response Codes
Documentation includes all possible response codes:
- **2xx Success**: 200 OK, 201 Created, 204 No Content
- **4xx Client Errors**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation Error, 429 Rate Limited
- **5xx Server Errors**: 500 Internal Server Error, 503 Service Unavailable

## API Testing Workflow

### 1. Setup Authentication
```
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: Bearer demo-token (for development)
4. Click "Authorize"
```

### 2. Test Health Endpoints
```
1. Expand "health" section
2. Try GET / (API Root)
3. Try GET /health (Health Check)
4. Verify responses
```

### 3. Test Project Management
```
1. Expand "projects" section
2. Try GET /api/projects/ (Get All Projects)
3. Try POST /api/projects/ (Create Project)
4. Try GET /api/projects/{id} (Get Specific Project)
5. Try PUT /api/projects/{id} (Update Project)
```

### 4. Test AI Chat Interface
```
1. Expand "chat" section
2. Try POST /api/chat/ with message: "Show me all active projects"
3. Review the AI response and generated SQL
4. Try different queries like "What are the total costs by region?"
```

## Common API Testing Scenarios

### Scenario 1: Project Lifecycle
```
1. Create a new project (POST /api/projects/)
2. Get the project details (GET /api/projects/{id})
3. Update project status (PATCH /api/projects/{id}/status)
4. Get updated project (GET /api/projects/{id})
```

### Scenario 2: Data Analysis with AI
```
1. Ask for project summary (POST /api/chat/)
   Message: "How many projects do we have by status?"
2. Ask for cost analysis (POST /api/chat/)
   Message: "What are the total costs by region?"
3. Ask for performance metrics (POST /api/chat/)
   Message: "Which projects are behind schedule?"
```

### Scenario 3: Cost Management
```
1. Get all costs (GET /api/costs/)
2. Filter by project (GET /api/costs/?project_id=1)
3. Get dashboard summary (GET /api/dashboard/summary)
```

## Request/Response Examples

### Create Project Request
```json
{
  "project_name": "API Test Project",
  "project_type": "External",
  "member_firm": "Test Corporation",
  "deployed_region": "US",
  "description": "Project created via Swagger UI",
  "engagement_manager": "John Doe",
  "project_startdate": "2024-01-01",
  "project_enddate": "2024-12-31",
  "budget_allocated": 100000,
  "priority": "medium"
}
```

### Chat Query Request
```json
{
  "message": "Show me all active projects in the US region",
  "conversation_id": "swagger-test-conversation"
}
```

### Project Status Update Request
```json
{
  "status": "active",
  "progress_percentage": 75,
  "health_status": "green",
  "status_notes": "Project is progressing well, milestone 3 completed"
}
```

## Error Handling Examples

### 400 Bad Request
```json
{
  "detail": "Invalid query parameters",
  "type": "validation_error"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "project_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Schema Exploration

### Project Schema
The documentation includes detailed schema definitions:
- **Required fields**: Marked with red asterisk (*)
- **Optional fields**: Clearly indicated
- **Data types**: String, integer, boolean, date, enum
- **Validation rules**: Min/max length, value ranges, format requirements
- **Examples**: Sample values for each field

### Enum Values
Enums are clearly documented with all possible values:
- **ProjectStatus**: planning, active, on_hold, completed, cancelled
- **ProjectPriority**: low, medium, high, critical
- **ProjectHealthStatus**: green, yellow, red
- **Region**: US, EU, APAC
- **ProjectType**: Internal, External, Client Demo

## Advanced Features

### 1. Filtering and Pagination
```
GET /api/projects/?skip=0&limit=10&status=active&region=US
```

### 2. Partial Updates
```
PUT /api/projects/1 (full update)
PATCH /api/projects/1/status (status-only update)
```

### 3. Conversation Context
```json
{
  "message": "What about costs?",
  "conversation_id": "same-conversation-id"
}
```

## Security Testing

### 1. Authentication Testing
- Test without token (should return 401)
- Test with invalid token (should return 401)
- Test with expired token (should return 401)

### 2. Authorization Testing
- Test user role endpoints with user token
- Test admin endpoints with user token (should return 403)
- Test admin endpoints with admin token

### 3. Input Validation Testing
- Test with invalid data types
- Test with values outside allowed ranges
- Test with missing required fields
- Test with overly long strings

## Rate Limiting Testing

### Test Rate Limits
```
1. Make multiple rapid requests to any endpoint
2. Observe rate limit headers in responses:
   - X-RateLimit-Limit: 100
   - X-RateLimit-Remaining: 95
   - X-RateLimit-Reset: 1641902400
3. Exceed limit to see 429 response
```

## Customization Options

### 1. Environment Variables
Set different base URLs for testing:
- Development: `http://localhost:8000`
- Staging: `https://api-staging.yourdomain.com`
- Production: `https://api.yourdomain.com`

### 2. Authentication Tokens
Use different tokens for different environments:
- Development: `demo-token`
- Staging: Your staging JWT token
- Production: Your production JWT token

## Integration with Development Tools

### 1. Postman Integration
```
1. Go to Swagger UI
2. Click on any endpoint
3. Look for "Download" or "Export" options
4. Import into Postman
```

### 2. Code Generation
```
1. Download OpenAPI spec from /openapi.json
2. Use tools like:
   - Swagger Codegen
   - OpenAPI Generator
   - Postman Code Generator
3. Generate client libraries in various languages
```

### 3. API Testing Tools
- **Insomnia**: Import OpenAPI spec
- **Thunder Client**: VS Code extension
- **REST Client**: VS Code extension
- **curl**: Copy curl commands from Swagger UI

## Best Practices

### 1. Documentation Review
- Review all endpoint descriptions
- Understand request/response schemas
- Check validation rules and constraints
- Note authentication requirements

### 2. Testing Strategy
- Start with health endpoints
- Test authentication flow
- Test CRUD operations systematically
- Test error scenarios
- Verify rate limiting

### 3. Development Workflow
- Use Swagger UI for initial API exploration
- Export to Postman for automated testing
- Generate client code for integration
- Document any custom implementations

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
Problem: 401 Unauthorized
Solution: 
- Check token format (Bearer <token>)
- Verify token is not expired
- Ensure Azure AD is configured (production)
```

#### 2. CORS Errors
```
Problem: CORS policy errors in browser
Solution:
- Check CORS_ORIGINS configuration
- Verify request origin is allowed
- Use proper headers
```

#### 3. Validation Errors
```
Problem: 422 Unprocessable Entity
Solution:
- Check required fields are provided
- Verify data types match schema
- Ensure values are within allowed ranges
```

#### 4. Rate Limiting
```
Problem: 429 Too Many Requests
Solution:
- Wait for rate limit reset
- Implement exponential backoff
- Reduce request frequency
```

## Support and Resources

### Documentation Links
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`
- **API Documentation**: `API_DOCUMENTATION.md`
- **Security Guide**: `SECURITY.md`

### Testing Resources
- **Postman Collection**: `postman_collection.json`
- **Example Requests**: Available in Swagger UI
- **Sample Data**: Use seed data scripts

### Development Support
- **GitHub Issues**: Report bugs and feature requests
- **API Support**: Contact development team
- **Security Issues**: Follow responsible disclosure

## Conclusion

The Swagger/OpenAPI documentation provides a comprehensive, interactive way to explore and test the Multi-Cloud Operations Dashboard API. Use it for:

- **Learning**: Understand API capabilities and data models
- **Testing**: Interactive testing of all endpoints
- **Integration**: Generate client code and export to tools
- **Documentation**: Share API specifications with team members

The documentation is automatically generated from the code and stays up-to-date with API changes, ensuring accuracy and reliability for all users.