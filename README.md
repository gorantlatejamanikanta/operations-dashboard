# Multi-Cloud Operations Dashboard

A comprehensive Multi-Cloud Operations Dashboard built with Next.js 15, FastAPI, Azure PostgreSQL, Azure OpenAI, and Azure Entra ID authentication.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and start all services
git clone <repository-url>
cd multi-cloud-operations-dashboard
docker-compose up -d

# Seed the database with sample data
docker-compose exec backend python seed_comprehensive_data.py

# Access the application
# Frontend: http://localhost:3001
# Backend API: http://localhost:8000/docs
# Database: localhost:5432
```

### Option 2: Manual Setup

See the [Local Development Setup](#local-development-setup) section below.

## 🏗️ Architecture

- **Frontend**: Next.js 15 (App Router), Tailwind CSS, Shadcn UI, Recharts
- **Backend**: FastAPI (Python) with SQLAlchemy and Pydantic
- **Database**: PostgreSQL 15+ (Azure Database for PostgreSQL in production)
- **Auth**: Azure Entra ID (MSAL) with Role-Based Access Control (RBAC)
- **AI**: Azure OpenAI (GPT-4o) for RAG-based chatbot
- **Deployment**: Dockerized for Azure App Service
- **Infrastructure**: Terraform for Azure resources
- **CI/CD**: GitHub Actions with comprehensive testing and security scanning

## ✨ Features

- 📊 **Interactive Dashboard**: Real-time cost trends and regional distribution charts
- 📋 **Project Management**: Complete project lifecycle with intake forms and status tracking
- 💰 **Cost Management**: Multi-cloud cost tracking and analysis
- ☁️ **Cloud Onboarding**: AWS, Azure, and GCP integration
- 💬 **AI Chatbot**: SQL-Agent powered chatbot that queries the database
- 🎨 **Theme System**: Light/dark theme with smooth transitions
- 🔐 **Security**: Azure Entra ID authentication with RBAC
- 🧪 **Testing**: Comprehensive unit, integration, and E2E tests
- 🐳 **Containerized**: Ready for production deployment
- 📚 **API Documentation**: Interactive Swagger/OpenAPI docs

## 📋 Prerequisites

- **Node.js 20+** and npm
- **Python 3.11+**
- **PostgreSQL 15+** (or use Docker)
- **Docker & Docker Compose** (recommended)
- **Azure CLI** (optional, for Azure integration)
- **Terraform >= 1.0** (for infrastructure deployment)

## 🛠️ Local Development Setup

### Environment Variables

Create the following environment files:

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/operationsdb

# Security
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development

# Azure Entra ID (Optional - for authentication)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# Azure OpenAI (Optional - for chatbot)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# CORS
CORS_ORIGINS=["http://localhost:3001"]
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id
```

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
# Edit .env with your configuration (see Environment Variables above)
```

5. Set up the database:
```bash
# Create tables and seed with sample data
python create_tables.py
python seed_comprehensive_data.py
```

6. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with docs at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```bash
cp .env.local.example .env.local
# Edit .env.local with your configuration (see Environment Variables above)
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3001`

**Note**: The frontend runs on port 3001 by default to avoid conflicts.

## 🧪 Testing

The project includes comprehensive testing with multiple test types:

```bash
# Run all tests
python run_tests.py --all

# Run specific test types
python run_tests.py --unit          # Unit tests
python run_tests.py --integration   # Integration tests
python run_tests.py --frontend      # E2E tests with Playwright
python run_tests.py --load          # Load tests with Locust
python run_tests.py --security      # Security scans

# Backend tests only
cd backend
python -m pytest tests/ -v --cov=app

# Frontend E2E tests only
cd frontend
npx playwright test
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing documentation.

## 🔒 Security

The application implements comprehensive security measures:

- **Authentication**: Azure Entra ID with JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Protection**: Parameterized queries and validation
- **Rate Limiting**: 100 requests/minute per IP
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Container Security**: Non-root users, health checks
- **Dependency Scanning**: Automated vulnerability detection

See [SECURITY.md](SECURITY.md) for detailed security documentation.

## 📚 Documentation

**📁 [Complete Documentation](docs/)** - All guides and references

### Quick Links
- **[Cloud Integration Guide](docs/CLOUD_INTEGRATION.md)**: Complete guide for AWS, Azure, and GCP integration
- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete API reference
- **[Testing Guide](docs/TESTING_GUIDE.md)**: Comprehensive testing documentation
- **[Security Guide](docs/SECURITY.md)**: Security best practices and configuration
- **[Architecture](docs/ARCHITECTURE.md)**: System architecture and design
- **Interactive API Docs**: Available at `http://localhost:8000/docs`

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Container Builds

#### Backend
```bash
cd backend
docker build -t operations-dashboard-backend .
docker run -p 8000:8000 --env-file .env operations-dashboard-backend
```

#### Frontend
```bash
cd frontend
docker build -t operations-dashboard-frontend .
docker run -p 3001:3000 --env-file .env.local operations-dashboard-frontend
```

## ☁️ Production Deployment

### Azure Deployment with Terraform

1. Navigate to the terraform directory:
```bash
cd terraform
```

2. Initialize Terraform:
```bash
terraform init
```

3. Create a `terraform.tfvars` file:
```hcl
resource_group_name = "rg-operations-dashboard"
location            = "East US"
postgres_admin_username = "psqladmin"
postgres_admin_password = "your-secure-password"
```

4. Plan and apply the deployment:
```bash
terraform plan
terraform apply
```

### CI/CD Pipeline

The project includes comprehensive GitHub Actions workflows:

- **CI Pipeline**: Code quality, testing, security scanning
- **Deployment Pipeline**: Automated staging and production deployment
- **Security Scanning**: Daily security scans and vulnerability detection
- **Performance Testing**: Load testing and performance monitoring

Configure repository secrets for full automation:
- `AZURE_CREDENTIALS`
- `STAGING_DB_PASSWORD`
- `PRODUCTION_DB_PASSWORD`
- `AZURE_OPENAI_API_KEY`
- And more (see `.github/workflows/` for complete list)

## 🔧 Configuration

### Authentication Modes

1. **Development Mode** (Default)
   - Uses mock authentication with `demo-token`
   - No Azure AD configuration required
   - All features accessible for testing

2. **Production Mode**
   - Requires Azure Entra ID configuration
   - JWT token validation enforced
   - Role-based access control active

### Azure Integration

1. **Mock Mode** (Default)
   - Uses sample data for development
   - No Azure credentials required
   - Perfect for testing and demos

2. **Live Azure Mode**
   - Requires Azure service principal
   - Real cost data from Azure APIs
   - Full cloud provider integration

## 📁 Project Structure

```
.
├── .github/
│   └── workflows/        # GitHub Actions CI/CD pipelines
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Configuration and database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic (chat, cloud services)
│   ├── tests/            # Backend tests (unit, integration, load)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── components/   # React components
│   │   ├── contexts/     # React contexts (theme, auth)
│   │   ├── lib/          # Utilities and configurations
│   │   └── (pages)/      # Next.js app router pages
│   ├── components/
│   │   └── ui/           # Shadcn UI components
│   ├── tests/            # Frontend E2E tests (Playwright)
│   ├── Dockerfile
│   └── package.json
├── terraform/            # Infrastructure as Code
├── docs/                 # Documentation files
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   ├── CLASS_DIAGRAMS.md
│   ├── CLOUD_INTEGRATION.md
│   ├── SECURITY.md
│   ├── SWAGGER_GUIDE.md
│   └── TESTING_GUIDE.md
├── docker-compose.yml    # Local development setup
└── run_tests.py         # Test runner script
```

## 🚨 Troubleshooting

### Common Issues

1. **Frontend can't connect to backend**
   - Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`
   - Check that backend is running on port 8000

2. **Database connection errors**
   - Ensure PostgreSQL is running (or use Docker Compose)
   - Check `DATABASE_URL` in backend `.env` file

3. **Authentication issues**
   - For development, use mock auth (leave Azure credentials empty)
   - For production, verify Azure AD configuration

4. **Port conflicts**
   - Frontend runs on port 3001 by default
   - Backend runs on port 8000
   - Database runs on port 5432

5. **Docker issues**
   - Run `docker-compose down && docker-compose up -d` to restart
   - Check logs with `docker-compose logs -f`

### Getting Help

1. Check the [API documentation](http://localhost:8000/docs) when backend is running
2. Review the comprehensive guides in the `docs/` folder
3. Check browser console and server logs for error messages
4. Ensure all environment variables are properly configured

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python run_tests.py --all`
5. Submit a pull request

The CI pipeline will automatically run tests, security scans, and code quality checks.

## 📄 License

MIT License - see LICENSE file for details.

---

**🚀 Ready to get started? Run `docker-compose up -d` and visit http://localhost:3001**
