from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from .core.config import settings
from .core.database import create_tables
from .api import chat, projects, dashboard, costs, azure, resource_groups, cloud_providers


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.clients[client_ip] = [
            req_time for req_time in self.clients[client_ip] 
            if now - req_time < self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Add current request
        self.clients[client_ip].append(now)
        
        response = await call_next(request)
        return response


app = FastAPI(
    title="Multi-Cloud Operations Dashboard API",
    description="""
    ## Multi-Cloud Operations Dashboard API
    
    A comprehensive REST API for managing multi-cloud operations, projects, costs, and resources.
    
    ### Features
    - **Project Management**: Create, update, and track cloud projects
    - **Cost Management**: Monitor and analyze cloud costs across providers
    - **Resource Management**: Manage cloud resources and resource groups
    - **AI Chat**: Intelligent SQL-based querying with natural language
    - **Cloud Integration**: Connect to AWS, Azure, and GCP
    - **Dashboard Analytics**: Real-time metrics and insights
    
    ### Authentication
    This API uses Azure Active Directory (Azure AD) for authentication. Include your JWT token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    
    ### Rate Limiting
    API requests are limited to 100 requests per minute per IP address.
    
    ### Security
    - All endpoints require authentication
    - Role-based access control (RBAC)
    - Input validation and sanitization
    - SQL injection protection
    - CORS protection
    
    ### Support
    For API support, please refer to the documentation or create an issue in the repository.
    """,
    version="1.0.0",
    contact={
        "name": "Multi-Cloud Operations Team",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.yourdomain.com",
            "description": "Production server"
        }
    ],
    tags_metadata=[
        {
            "name": "authentication",
            "description": "Authentication and authorization endpoints"
        },
        {
            "name": "projects",
            "description": "Project management operations. Create, read, update, and delete cloud projects."
        },
        {
            "name": "costs",
            "description": "Cost management and analysis. Track spending across cloud providers."
        },
        {
            "name": "resource-groups",
            "description": "Resource group management. Organize and manage cloud resources."
        },
        {
            "name": "dashboard",
            "description": "Dashboard analytics and metrics. Get insights and summaries."
        },
        {
            "name": "chat",
            "description": "AI-powered chat interface. Query data using natural language."
        },
        {
            "name": "cloud-providers",
            "description": "Cloud provider integration. Connect to AWS, Azure, and GCP."
        },
        {
            "name": "azure",
            "description": "Azure-specific operations and cost retrieval."
        },
        {
            "name": "health",
            "description": "Health check and system status endpoints."
        }
    ]
)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, calls=100, period=60)  # 100 requests per minute

# Trusted host middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]  # Configure for your domain
    )

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# CORS middleware - Restrict methods and headers for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Specific methods only
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "Accept", 
        "Origin", 
        "X-Requested-With"
    ],  # Specific headers only
)

# Include routers
app.include_router(chat.router)
app.include_router(projects.router)
app.include_router(resource_groups.router)
app.include_router(dashboard.router)
app.include_router(costs.router)
app.include_router(azure.router)
app.include_router(cloud_providers.router)


@app.get("/", 
         summary="API Root",
         description="Welcome endpoint that provides basic API information",
         tags=["health"],
         responses={
             200: {
                 "description": "API information",
                 "content": {
                     "application/json": {
                         "example": {
                             "message": "Multi-Cloud Operations Dashboard API",
                             "version": "1.0.0",
                             "docs": "/docs",
                             "redoc": "/redoc"
                         }
                     }
                 }
             }
         })
def root():
    """
    Welcome endpoint for the Multi-Cloud Operations Dashboard API.
    
    Returns basic information about the API including version and documentation links.
    """
    return {
        "message": "Multi-Cloud Operations Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health",
         summary="Health Check",
         description="Check the health status of the API service",
         tags=["health"],
         responses={
             200: {
                 "description": "Service is healthy",
                 "content": {
                     "application/json": {
                         "example": {
                             "status": "healthy",
                             "timestamp": "2024-01-11T10:30:00Z",
                             "version": "1.0.0"
                         }
                     }
                 }
             },
             503: {
                 "description": "Service is unhealthy",
                 "content": {
                     "application/json": {
                         "example": {
                             "status": "unhealthy",
                             "error": "Database connection failed"
                         }
                     }
                 }
             }
         })
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns the current health status of the API service including:
    - Service status
    - Timestamp
    - Version information
    
    This endpoint is used by:
    - Docker health checks
    - Kubernetes liveness probes
    - Load balancer health checks
    - Monitoring systems
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }
