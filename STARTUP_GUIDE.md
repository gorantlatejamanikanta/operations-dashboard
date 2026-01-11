# Multi-Cloud Operations Dashboard - Startup Guide

This guide will help you get the Multi-Cloud Operations Dashboard up and running quickly.

## Prerequisites

- **Node.js 20+** and npm
- **Python 3.11+**
- **PostgreSQL 15+** (or use Docker)
- **Azure CLI** (optional, for Azure integration)

## Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
# Clone and navigate to the project
cd multi-cloud-operations-dashboard

# Start all services
docker-compose up -d

# Wait for services to start, then seed the database
docker-compose exec backend python seed_data.py

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Database: localhost:5433
```

## Manual Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration (see Environment Variables section)

# Create database tables and seed data
python create_tables.py
python seed_data.py

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Start the development server
npm run dev
```

### 3. Database Setup (PostgreSQL)

If not using Docker, set up PostgreSQL manually:

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE operationsdb;
CREATE USER dbuser WITH PASSWORD 'dbpassword';
GRANT ALL PRIVILEGES ON DATABASE operationsdb TO dbuser;
\q
```

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://dbuser:dbpassword@localhost:5432/operationsdb

# Azure Entra ID (Optional - for authentication)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id

# Azure OpenAI (Optional - for chatbot)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id
```

## Features Overview

### ✅ Implemented Features

1. **Dashboard**
   - Real-time statistics (total projects, active projects, total cost)
   - Cost trends chart (monthly aggregation)
   - Regional distribution chart (pie chart)
   - Responsive design with glassmorphism effects

2. **Project Management**
   - Create, read, update, delete projects
   - Project types: Internal, External, Client Demo
   - Regions: US, EU, APAC
   - Full project lifecycle tracking

3. **Cost Management**
   - Monthly cost tracking per project/resource group
   - Cost summaries and aggregations
   - Manual cost entry with validation
   - Azure cost sync integration (with mock data)

4. **AI Chatbot**
   - SQL-Agent powered by Azure OpenAI
   - Natural language queries about data
   - SQL query generation and execution
   - Conversation history

5. **Azure Integration**
   - Resource group listing
   - Cost sync from Azure Cost Management API (mock implementation)
   - Azure Entra ID authentication setup

6. **Backend API**
   - FastAPI with automatic OpenAPI documentation
   - SQLAlchemy ORM with PostgreSQL
   - JWT authentication (Azure Entra ID)
   - Comprehensive error handling

### 🔧 Configuration Options

#### Authentication Modes

1. **Development Mode** (No Azure AD)
   - Leave Azure credentials empty in .env
   - Uses mock authentication
   - All API endpoints accessible

2. **Production Mode** (Azure AD Required)
   - Configure Azure Entra ID credentials
   - JWT token validation enforced
   - Role-based access control

#### Azure Integration

1. **Mock Mode** (Default)
   - Uses generated sample data
   - No Azure credentials required
   - Good for development and testing

2. **Live Azure Mode**
   - Requires Azure service principal
   - Real cost data from Azure Cost Management API
   - Requires proper Azure permissions

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create new project
- `GET /api/costs/monthly` - Monthly cost data
- `POST /api/chat/` - AI chatbot interface
- `POST /api/azure/sync-costs` - Sync costs from Azure

## Sample Data

The application comes with sample data including:
- 4 sample projects across different regions and types
- 8 resource groups (prod/dev for each project)
- 6 months of monthly cost data
- Cost summaries and AI consumption data

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```
   Solution: Check DATABASE_URL in .env and ensure PostgreSQL is running
   ```

2. **Frontend Can't Connect to Backend**
   ```
   Solution: Verify NEXT_PUBLIC_API_URL in .env.local points to http://localhost:8000
   ```

3. **Authentication Errors**
   ```
   Solution: For development, leave Azure credentials empty. For production, verify Azure AD configuration.
   ```

4. **Chatbot Not Working**
   ```
   Solution: Configure Azure OpenAI credentials in backend .env file
   ```

5. **Charts Not Displaying**
   ```
   Solution: Ensure sample data is seeded and backend API is accessible
   ```

### Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload during development
2. **Database Reset**: Run `python create_tables.py` to reset and recreate tables
3. **API Testing**: Use the Swagger UI at http://localhost:8000/docs
4. **Logs**: Check browser console and terminal for error messages

## Production Deployment

For production deployment:

1. **Use the Terraform configuration** in `/terraform` directory
2. **Set up Azure resources** (PostgreSQL, App Services, OpenAI)
3. **Configure environment variables** with production values
4. **Build and deploy** using Docker containers
5. **Set up monitoring** with Application Insights

## Next Steps

1. **Configure Azure Integration**: Set up real Azure Cost Management API
2. **Customize Branding**: Update colors, logos, and styling
3. **Add More Features**: Implement additional cost analytics and reporting
4. **Set Up CI/CD**: Automate deployment with GitHub Actions or Azure DevOps
5. **Add Monitoring**: Set up logging, metrics, and alerting

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Check the browser console and server logs for error messages

---

**Happy coding! 🚀**