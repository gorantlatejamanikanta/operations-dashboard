# Multi-Cloud Operations Dashboard

A comprehensive Multi-Cloud Operations Dashboard built with Next.js 15, FastAPI, Azure PostgreSQL, Azure OpenAI, and Azure Entra ID authentication.

## Architecture

- **Frontend**: Next.js 15 (App Router), Tailwind CSS, Shadcn UI, Recharts
- **Backend**: FastAPI (Python) with SQLAlchemy and Pydantic
- **Database**: Azure Database for PostgreSQL (Flexible Server)
- **Auth**: Azure Entra ID (MSAL) with Role-Based Access Control (RBAC)
- **AI**: Azure OpenAI (GPT-4o) for RAG-based chatbot
- **Deployment**: Dockerized for Azure App Service
- **Infrastructure**: Terraform for Azure resources

## Features

- 📊 **Interactive Dashboard**: Real-time cost trends and regional distribution charts
- 💬 **AI Chatbot**: SQL-Agent powered chatbot that queries the database
- 🎨 **Dark Theme**: Deep navy and slate theme with glassmorphism effects
- 🔐 **Azure Entra ID Authentication**: MSAL-based authentication with RBAC
- 🐳 **Dockerized**: Ready for containerized deployment
- ☁️ **Infrastructure as Code**: Terraform configuration for Azure

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- Azure CLI
- Terraform >= 1.0
- Docker (for containerization)

## Local Development Setup

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
# Edit .env with your configuration
```

5. Run database migrations (if using Alembic):
```bash
alembic upgrade head
```

6. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

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
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Database Schema

The application uses the following main tables:
- `project`: Projects information
- `aiq_consumption`: AI consumption data
- `resource_group`: Resource groups
- `monthly_cost`: Monthly cost data
- `cost_data`: Detailed cost data
- `project_cost_summary`: Cost summaries

See the database models in `backend/app/models/` for detailed schema.

## Docker Deployment

### Backend

```bash
cd backend
docker build -t operations-dashboard-backend .
docker run -p 8000:8000 --env-file .env operations-dashboard-backend
```

### Frontend

```bash
cd frontend
docker build -t operations-dashboard-frontend .
docker run -p 3000:3000 --env-file .env.local operations-dashboard-frontend
```

## Terraform Deployment

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

4. Plan the deployment:
```bash
terraform plan
```

5. Apply the configuration:
```bash
terraform apply
```

## Azure Configuration

### Azure Entra ID Setup

1. Register an application in Azure AD
2. Configure redirect URIs
3. Set up API permissions
4. Create security groups for RBAC
5. Update environment variables with Client ID and Tenant ID

### Azure OpenAI Setup

1. Create an Azure OpenAI resource
2. Deploy GPT-4o model
3. Configure API keys
4. Update environment variables

## Chatbot

The chatbot uses Azure OpenAI with a SQL-Agent approach:
- Generates SQL queries based on user questions
- Executes queries against the PostgreSQL database
- Returns results in natural language
- Prevents hallucinations by only querying the database schema

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration and database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic (chat service)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and MSAL config
│   │   └── page.tsx      # Main dashboard page
│   ├── components/
│   │   └── ui/           # Shadcn UI components
│   ├── Dockerfile
│   └── package.json
└── terraform/
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

## License

MIT
