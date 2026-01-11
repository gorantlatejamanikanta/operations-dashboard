# Multi-Cloud Operations Dashboard - Architecture Documentation

## System Overview

The Multi-Cloud Operations Dashboard is a full-stack web application designed to manage multi-cloud operations, projects, costs, and resources. It follows a modern microservices-inspired architecture with clear separation of concerns.

## Architecture Diagrams

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile Browser]
    end
    
    subgraph "Frontend Layer"
        NEXTJS[Next.js Frontend]
        REACT[React Components]
        TAILWIND[Tailwind CSS]
    end
    
    subgraph "API Gateway Layer"
        LB[Load Balancer]
        CORS[CORS Middleware]
        AUTH[Auth Middleware]
        RATE[Rate Limiting]
    end
    
    subgraph "Backend Services"
        API[FastAPI Backend]
        CHAT[Chat Service]
        CLOUD[Cloud Services]
        AUTH_SVC[Auth Service]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
    end
    
    subgraph "External Services"
        AZURE_AD[Azure AD]
        AZURE_OPENAI[Azure OpenAI]
        AWS[AWS APIs]
        AZURE_CLOUD[Azure APIs]
        GCP[GCP APIs]
    end
    
    WEB --> NEXTJS
    MOBILE --> NEXTJS
    NEXTJS --> LB
    LB --> CORS
    CORS --> AUTH
    AUTH --> RATE
    RATE --> API
    
    API --> CHAT
    API --> CLOUD
    API --> AUTH_SVC
    
    API --> DB
    API --> CACHE
    
    AUTH_SVC --> AZURE_AD
    CHAT --> AZURE_OPENAI
    CLOUD --> AWS
    CLOUD --> AZURE_CLOUD
    CLOUD --> GCP
```

### Component Architecture

```mermaid
graph TB
    subgraph "Frontend Components"
        APP[App Component]
        LAYOUT[Layout Component]
        PAGES[Page Components]
        UI[UI Components]
        HOOKS[Custom Hooks]
        CONTEXT[Context Providers]
    end
    
    subgraph "Backend Components"
        MAIN[Main Application]
        ROUTERS[API Routers]
        SERVICES[Business Services]
        MODELS[Data Models]
        SCHEMAS[Pydantic Schemas]
        MIDDLEWARE[Middleware]
    end
    
    subgraph "Database Layer"
        TABLES[Database Tables]
        MIGRATIONS[Migrations]
        INDEXES[Indexes]
    end
    
    APP --> LAYOUT
    LAYOUT --> PAGES
    PAGES --> UI
    PAGES --> HOOKS
    HOOKS --> CONTEXT
    
    MAIN --> ROUTERS
    ROUTERS --> SERVICES
    SERVICES --> MODELS
    MODELS --> SCHEMAS
    MAIN --> MIDDLEWARE
    
    MODELS --> TABLES
    TABLES --> MIGRATIONS
    TABLES --> INDEXES
```

### Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Gateway
    participant B as Backend
    participant D as Database
    participant E as External APIs
    
    U->>F: User Action
    F->>A: HTTP Request
    A->>A: Authentication
    A->>A: Rate Limiting
    A->>B: Validated Request
    B->>D: Query/Update Data
    D-->>B: Data Response
    B->>E: External API Call (if needed)
    E-->>B: External Data
    B-->>A: Processed Response
    A-->>F: JSON Response
    F-->>U: Updated UI
```

## Technology Stack

### Frontend Stack
- **Framework**: Next.js 15.0.0
- **UI Library**: React 18.2.0
- **Styling**: Tailwind CSS 3.3.6
- **State Management**: React Context + Hooks
- **Authentication**: Azure MSAL
- **Charts**: Recharts 2.10.3
- **Icons**: Lucide React 0.294.0
- **HTTP Client**: Fetch API
- **Build Tool**: Next.js built-in

### Backend Stack
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11
- **Database ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Authentication**: JWT + Azure AD
- **Database**: PostgreSQL 15
- **AI Integration**: Azure OpenAI
- **Cloud SDKs**: AWS SDK, Azure SDK, GCP SDK
- **Testing**: Pytest 7.4.3

### Infrastructure Stack
- **Containerization**: Docker + Docker Compose
- **Database**: PostgreSQL 15
- **Caching**: Redis (optional)
- **Cloud Deployment**: Azure Container Instances
- **Infrastructure as Code**: Terraform
- **CI/CD**: GitHub Actions
- **Monitoring**: Azure Monitor

## Security Architecture

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant AD as Azure AD
    participant B as Backend
    
    U->>F: Login Request
    F->>AD: Redirect to Azure AD
    AD->>U: Login Form
    U->>AD: Credentials
    AD->>F: JWT Token
    F->>B: API Request + JWT
    B->>AD: Validate JWT (JWKS)
    AD-->>B: Token Valid
    B-->>F: Authorized Response
```

### Security Layers

```mermaid
graph TB
    subgraph "Security Layers"
        WAF[Web Application Firewall]
        TLS[TLS/HTTPS Encryption]
        CORS[CORS Protection]
        AUTH[Authentication Layer]
        AUTHZ[Authorization Layer]
        INPUT[Input Validation]
        SQL[SQL Injection Protection]
        XSS[XSS Protection]
        RATE[Rate Limiting]
        AUDIT[Audit Logging]
    end
    
    WAF --> TLS
    TLS --> CORS
    CORS --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> INPUT
    INPUT --> SQL
    SQL --> XSS
    XSS --> RATE
    RATE --> AUDIT
```

## Database Architecture

### Entity Relationship Diagram

```mermaid
erDiagram
    PROJECT {
        int id PK
        string project_name
        string project_type
        string member_firm
        string deployed_region
        boolean is_active
        text description
        string engagement_manager
        date project_startdate
        date project_enddate
        string status
        int progress_percentage
        int budget_allocated
        int budget_spent
    }
    
    RESOURCE_GROUP {
        int id PK
        string resource_group_name
        int project_id FK
        string status
    }
    
    COST_DATA {
        string key PK
        date period
        string month_year
        int resource_group_id FK
        decimal cost
    }
    
    MONTHLY_COST {
        int project_id FK
        int resource_group_id FK
        date month
        decimal cost
    }
    
    PROJECT_COST_SUMMARY {
        int project_id FK
        int resource_group_id FK
        decimal total_cost_to_date
        date updated_date
        decimal costs_passed_back_to_date
        decimal gpt_costs_to_date
    }
    
    AIQ_CONSUMPTION {
        int id PK
        int project_id FK
        string aiq_assumption_name
        decimal consumption_amount
        date consumption_day
    }
    
    CLOUD_CONNECTION {
        int id PK
        string provider
        string connection_name
        json credentials
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    PROJECT ||--o{ RESOURCE_GROUP : "has"
    PROJECT ||--o{ MONTHLY_COST : "incurs"
    PROJECT ||--o{ PROJECT_COST_SUMMARY : "summarizes"
    PROJECT ||--o{ AIQ_CONSUMPTION : "consumes"
    RESOURCE_GROUP ||--o{ COST_DATA : "generates"
    RESOURCE_GROUP ||--o{ MONTHLY_COST : "incurs"
    RESOURCE_GROUP ||--o{ PROJECT_COST_SUMMARY : "summarizes"
```

## API Architecture

### REST API Design

```mermaid
graph TB
    subgraph "API Endpoints"
        HEALTH["/health - Health Check"]
        AUTH["/auth - Authentication"]
        PROJECTS["/api/projects - Project CRUD"]
        COSTS["/api/costs - Cost Management"]
        CHAT["/api/chat - AI Chat"]
        CLOUD["/api/cloud-providers - Cloud Integration"]
        DASHBOARD["/api/dashboard - Analytics"]
        RESOURCES["/api/resource-groups - Resource Management"]
    end
    
    subgraph "HTTP Methods"
        GET[GET - Read Operations]
        POST[POST - Create Operations]
        PUT[PUT - Update Operations]
        PATCH[PATCH - Partial Updates]
        DELETE[DELETE - Delete Operations]
    end
    
    subgraph "Response Formats"
        JSON[JSON Responses]
        ERRORS[Error Responses]
        PAGINATION[Paginated Results]
    end
    
    PROJECTS --> GET
    PROJECTS --> POST
    PROJECTS --> PUT
    PROJECTS --> PATCH
    PROJECTS --> DELETE
    
    GET --> JSON
    POST --> JSON
    PUT --> JSON
    PATCH --> JSON
    DELETE --> JSON
    
    JSON --> ERRORS
    JSON --> PAGINATION
```

### Middleware Stack

```mermaid
graph TB
    REQUEST[Incoming Request]
    
    subgraph "Middleware Pipeline"
        SECURITY[Security Headers]
        RATE_LIMIT[Rate Limiting]
        CORS_MW[CORS Middleware]
        AUTH_MW[Authentication]
        VALIDATION[Input Validation]
        LOGGING[Request Logging]
    end
    
    RESPONSE[Response]
    
    REQUEST --> SECURITY
    SECURITY --> RATE_LIMIT
    RATE_LIMIT --> CORS_MW
    CORS_MW --> AUTH_MW
    AUTH_MW --> VALIDATION
    VALIDATION --> LOGGING
    LOGGING --> RESPONSE
```

## Deployment Architecture

### Container Architecture

```mermaid
graph TB
    subgraph "Docker Containers"
        FRONTEND_C[Frontend Container]
        BACKEND_C[Backend Container]
        DB_C[Database Container]
        REDIS_C[Redis Container]
    end
    
    subgraph "Docker Networks"
        APP_NET[app-network]
    end
    
    subgraph "Volumes"
        DB_VOL[postgres_data]
        REDIS_VOL[redis_data]
    end
    
    FRONTEND_C --> APP_NET
    BACKEND_C --> APP_NET
    DB_C --> APP_NET
    REDIS_C --> APP_NET
    
    DB_C --> DB_VOL
    REDIS_C --> REDIS_VOL
```

### Cloud Deployment

```mermaid
graph TB
    subgraph "Azure Cloud"
        subgraph "Resource Group"
            ACI[Azure Container Instances]
            ACR[Azure Container Registry]
            PSQL[Azure Database for PostgreSQL]
            REDIS_AZURE[Azure Cache for Redis]
            STORAGE[Azure Storage Account]
            MONITOR[Azure Monitor]
        end
        
        subgraph "Networking"
            VNET[Virtual Network]
            NSG[Network Security Group]
            LB_AZURE[Load Balancer]
        end
        
        subgraph "Security"
            KV[Key Vault]
            AD[Azure Active Directory]
        end
    end
    
    ACI --> ACR
    ACI --> PSQL
    ACI --> REDIS_AZURE
    ACI --> STORAGE
    ACI --> MONITOR
    
    ACI --> VNET
    VNET --> NSG
    VNET --> LB_AZURE
    
    ACI --> KV
    ACI --> AD
```

## Performance Architecture

### Caching Strategy

```mermaid
graph TB
    CLIENT[Client Browser]
    CDN[Content Delivery Network]
    FRONTEND[Frontend Server]
    API[API Server]
    REDIS[Redis Cache]
    DATABASE[PostgreSQL]
    
    CLIENT --> CDN
    CDN --> FRONTEND
    FRONTEND --> API
    API --> REDIS
    REDIS --> DATABASE
    
    subgraph "Cache Layers"
        BROWSER_CACHE[Browser Cache]
        CDN_CACHE[CDN Cache]
        API_CACHE[API Response Cache]
        DB_CACHE[Database Query Cache]
    end
    
    CLIENT --> BROWSER_CACHE
    CDN --> CDN_CACHE
    API --> API_CACHE
    DATABASE --> DB_CACHE
```

### Scalability Patterns

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        LB[Load Balancer]
        API1[API Instance 1]
        API2[API Instance 2]
        API3[API Instance 3]
    end
    
    subgraph "Database Scaling"
        MASTER[Master DB]
        REPLICA1[Read Replica 1]
        REPLICA2[Read Replica 2]
    end
    
    subgraph "Caching Layer"
        REDIS_CLUSTER[Redis Cluster]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> MASTER
    API2 --> REPLICA1
    API3 --> REPLICA2
    
    API1 --> REDIS_CLUSTER
    API2 --> REDIS_CLUSTER
    API3 --> REDIS_CLUSTER
```

## Monitoring Architecture

### Observability Stack

```mermaid
graph TB
    subgraph "Application"
        FRONTEND_APP[Frontend App]
        BACKEND_APP[Backend App]
        DATABASE_APP[Database]
    end
    
    subgraph "Monitoring Tools"
        METRICS[Metrics Collection]
        LOGS[Log Aggregation]
        TRACES[Distributed Tracing]
        ALERTS[Alerting System]
    end
    
    subgraph "Dashboards"
        GRAFANA[Grafana Dashboards]
        AZURE_DASH[Azure Dashboards]
        CUSTOM_DASH[Custom Dashboards]
    end
    
    FRONTEND_APP --> METRICS
    BACKEND_APP --> METRICS
    DATABASE_APP --> METRICS
    
    FRONTEND_APP --> LOGS
    BACKEND_APP --> LOGS
    DATABASE_APP --> LOGS
    
    BACKEND_APP --> TRACES
    
    METRICS --> ALERTS
    LOGS --> ALERTS
    
    METRICS --> GRAFANA
    LOGS --> AZURE_DASH
    TRACES --> CUSTOM_DASH
```

## Development Architecture

### Development Workflow

```mermaid
graph TB
    DEV[Developer]
    
    subgraph "Development Environment"
        LOCAL[Local Development]
        DOCKER_DEV[Docker Compose]
        HOT_RELOAD[Hot Reload]
    end
    
    subgraph "Version Control"
        GIT[Git Repository]
        BRANCHES[Feature Branches]
        PR[Pull Requests]
    end
    
    subgraph "CI/CD Pipeline"
        BUILD[Build & Test]
        SECURITY_SCAN[Security Scan]
        DEPLOY_STAGING[Deploy to Staging]
        DEPLOY_PROD[Deploy to Production]
    end
    
    DEV --> LOCAL
    LOCAL --> DOCKER_DEV
    DOCKER_DEV --> HOT_RELOAD
    
    DEV --> GIT
    GIT --> BRANCHES
    BRANCHES --> PR
    
    PR --> BUILD
    BUILD --> SECURITY_SCAN
    SECURITY_SCAN --> DEPLOY_STAGING
    DEPLOY_STAGING --> DEPLOY_PROD
```

## Quality Assurance Architecture

### Testing Strategy

```mermaid
graph TB
    subgraph "Testing Pyramid"
        E2E[End-to-End Tests]
        INTEGRATION[Integration Tests]
        UNIT[Unit Tests]
    end
    
    subgraph "Testing Tools"
        PLAYWRIGHT[Playwright E2E]
        PYTEST[Pytest Backend]
        JEST[Jest Frontend]
        POSTMAN[Postman API]
    end
    
    subgraph "Quality Gates"
        COVERAGE[Code Coverage]
        LINTING[Code Linting]
        SECURITY_TEST[Security Testing]
        PERFORMANCE[Performance Testing]
    end
    
    E2E --> PLAYWRIGHT
    INTEGRATION --> PYTEST
    UNIT --> PYTEST
    UNIT --> JEST
    
    INTEGRATION --> POSTMAN
    
    PLAYWRIGHT --> COVERAGE
    PYTEST --> COVERAGE
    JEST --> COVERAGE
    
    COVERAGE --> LINTING
    LINTING --> SECURITY_TEST
    SECURITY_TEST --> PERFORMANCE
```

## Configuration Management

### Environment Configuration

```mermaid
graph TB
    subgraph "Configuration Sources"
        ENV_VARS[Environment Variables]
        CONFIG_FILES[Configuration Files]
        SECRETS[Secret Management]
        DEFAULTS[Default Values]
    end
    
    subgraph "Environment Types"
        DEVELOPMENT[Development]
        STAGING[Staging]
        PRODUCTION[Production]
    end
    
    subgraph "Configuration Validation"
        SCHEMA[Schema Validation]
        REQUIRED[Required Fields]
        TYPES[Type Checking]
    end
    
    ENV_VARS --> DEVELOPMENT
    CONFIG_FILES --> STAGING
    SECRETS --> PRODUCTION
    DEFAULTS --> DEVELOPMENT
    
    DEVELOPMENT --> SCHEMA
    STAGING --> REQUIRED
    PRODUCTION --> TYPES
```

This architecture documentation provides a comprehensive overview of the Multi-Cloud Operations Dashboard system design, covering all major architectural aspects from high-level system design to detailed component interactions.