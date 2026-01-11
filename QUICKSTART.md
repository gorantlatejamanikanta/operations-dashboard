# Quick Start Guide

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (or use Docker Compose)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database and Azure credentials
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API URL and Azure credentials
npm run dev
```

### Using Docker Compose

```bash
docker-compose up -d
```

This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000
- PostgreSQL on localhost:5432

## Azure Deployment

### 1. Configure Azure Resources

Update `terraform/terraform.tfvars`:

```hcl
resource_group_name = "rg-operations-dashboard"
location            = "East US"
postgres_admin_username = "psqladmin"
postgres_admin_password = "your-secure-password"
```

### 2. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 3. Build and Push Docker Images

```bash
# Build backend
cd backend
docker build -t your-registry.azurecr.io/backend:latest .

# Build frontend
cd ../frontend
docker build -t your-registry.azurecr.io/frontend:latest .

# Push to Azure Container Registry
az acr login --name your-registry
docker push your-registry.azurecr.io/backend:latest
docker push your-registry.azurecr.io/frontend:latest
```

### 4. Update App Service Settings

Update the Docker image references in `terraform/main.tf` with your ACR registry name, then run `terraform apply` again.

## Database Schema

The application uses the following schema:

- **project**: Core project information
- **aiq_consumption**: AI consumption metrics
- **resource_group**: Azure resource groups
- **monthly_cost**: Monthly cost tracking
- **cost_data**: Detailed cost data
- **project_cost_summary**: Cost summaries

Run the SQL schema from the README to create the tables in your PostgreSQL database.

## Features

✅ Dark theme with glassmorphism effects
✅ Interactive charts (cost trends, regional distribution)
✅ AI-powered chatbot with SQL-Agent approach
✅ Azure Entra ID authentication (MSAL)
✅ RESTful API with FastAPI
✅ Dockerized deployment ready
✅ Terraform infrastructure as code

## Troubleshooting

### Backend won't start
- Check database connection string in `.env`
- Verify Azure OpenAI credentials are set
- Ensure PostgreSQL is running

### Frontend build fails
- Run `npm install` again
- Clear `.next` folder: `rm -rf .next`
- Check Node.js version (requires 20+)

### Chatbot not working
- Verify Azure OpenAI endpoint and API key
- Check deployment name matches configuration
- Ensure the model (gpt-4o) is deployed in Azure OpenAI
