# Azure Cloud Connection Guide

## Quick Start: Connecting to Azure

This guide explains how to connect your dashboard to Azure and sync costs from Azure Cost Management API.

## Step 1: Create Azure Service Principal

A service principal is an identity that your application uses to access Azure resources.

### Option A: Using Azure CLI (Recommended)

1. **Install Azure CLI** (if not already installed):
```bash
# macOS
brew install azure-cli

# Or download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

2. **Login to Azure**:
```bash
az login
```

3. **Set your subscription** (if you have multiple):
```bash
az account list --output table
az account set --subscription "Your-Subscription-Name"
```

4. **Create Service Principal**:
```bash
# Replace with your subscription ID
SUBSCRIPTION_ID=$(az account show --query id --output tsv)

# Create service principal with Cost Management Reader role
az ad sp create-for-rbac \
  --name "operations-dashboard-sp" \
  --role "Cost Management Reader" \
  --scopes /subscriptions/$SUBSCRIPTION_ID
```

**Output will look like:**
```json
{
  "appId": "xxxx-xxxx-xxxx-xxxx",     # This is AZURE_CLIENT_ID
  "password": "xxxx-xxxx-xxxx-xxxx",  # This is AZURE_CLIENT_SECRET
  "tenant": "xxxx-xxxx-xxxx-xxxx"     # This is AZURE_TENANT_ID
}
```

5. **Save these credentials securely!** The password won't be shown again.

### Option B: Using Azure Portal

1. Go to Azure Portal → **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Name: `operations-dashboard`
4. Click **Register**
5. Note the **Application (client) ID** (this is `AZURE_CLIENT_ID`)
6. Note the **Directory (tenant) ID** (this is `AZURE_TENANT_ID`)
7. Go to **Certificates & secrets** → **New client secret**
8. Create a secret and **copy it immediately** (this is `AZURE_CLIENT_SECRET`)
9. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions**
10. Add **User.Read** permission
11. Go to **Subscriptions** → Select your subscription → **Access control (IAM)**
12. Click **Add** → **Add role assignment**
13. Role: **Cost Management Reader**
14. Assign access to: **User, group, or service principal**
15. Select your app registration

## Step 2: Get Your Subscription ID

```bash
# Using Azure CLI
az account show --query id --output tsv

# Or from Azure Portal:
# Subscriptions → Your Subscription → Overview → Subscription ID
```

## Step 3: Configure Environment Variables

Edit `backend/.env` file and add:

```env
# Azure Entra ID / Service Principal
AZURE_CLIENT_ID=your-app-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_TENANT_ID=your-tenant-id-here
AZURE_SUBSCRIPTION_ID=your-subscription-id-here
```

**Important:** Never commit `.env` file to git! It contains sensitive credentials.

## Step 4: Test the Connection

### Check if Azure is configured:

```bash
# Via API
curl http://localhost:8000/api/azure/configured

# Expected response:
{
  "configured": true,
  "message": "Azure credentials configured"
}
```

### List Azure Resource Groups:

```bash
curl http://localhost:8000/api/azure/resource-groups

# Expected response:
{
  "resource_groups": [
    {
      "name": "rg-production",
      "location": "eastus",
      "id": "/subscriptions/.../resourceGroups/rg-production",
      "tags": {}
    }
  ]
}
```

## Step 5: How Costs Are Tagged to Resource Groups

### Database Structure

Costs are linked to resource groups through these relationships:

```
Project (1) ──→ (Many) Resource Groups
                ↓
            (Many) Monthly Costs
```

### Key Tables:

1. **`resource_group`** table:
   - `id` - Unique identifier
   - `resource_group_name` - Azure resource group name
   - `project_id` - Links to project

2. **`monthly_cost`** table:
   - `project_id` - Project this cost belongs to
   - `resource_group_id` - Resource group this cost is for
   - `month` - Date of the cost
   - `cost` - Cost amount

3. **`project_cost_summary`** table:
   - `project_id` + `resource_group_id` - Composite key
   - `total_cost_to_date` - Aggregated total cost
   - `gpt_costs_to_date` - AI-related costs

### How to Tag Costs to Resource Groups

#### Method 1: Sync from Azure (Automated)

1. **Create a Project** (if not exists):
```bash
POST http://localhost:8000/api/projects/
{
  "project_name": "Cloud Migration",
  "project_type": "Internal",
  "member_firm": "US Office",
  "deployed_region": "US",
  "project_startdate": "2024-01-01",
  "project_enddate": "2024-12-31"
}
```

2. **Sync Costs from Azure**:
```bash
POST http://localhost:8000/api/azure/sync-costs
{
  "project_id": 1,
  "resource_group_name": "rg-production",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z"
}
```

**What happens:**
- System checks if resource group exists for this project
- If not, creates a new resource group record
- Fetches costs from Azure Cost Management API
- Creates `monthly_cost` entries linked to the resource group
- Updates `project_cost_summary` automatically

#### Method 2: Manual Cost Entry

1. **Create Resource Group** (if not exists):
```bash
POST http://localhost:8000/api/resource-groups/
{
  "resource_group_name": "rg-production",
  "project_id": 1,
  "status": "Active"
}
```

2. **Add Monthly Cost**:
```bash
POST http://localhost:8000/api/costs/monthly
{
  "project_id": 1,
  "resource_group_id": 1,
  "month": "2024-01-01",
  "cost": 5000.00
}
```

**This creates a cost entry linked to:**
- Project ID: 1
- Resource Group ID: 1
- Month: January 2024
- Cost: $5,000.00

## Step 6: Sync Costs via UI

### Using the Dashboard:

1. Go to **Dashboard** (`http://localhost:3000`)
2. Click **"Add New Project"** button (if project doesn't exist)
3. Fill in project details
4. Click **"Sync from Azure"** button (if implemented in UI)
5. Enter Azure resource group name
6. Select date range
7. Click **"Sync Costs"**

### Using the Costs Page:

1. Go to **Costs** page (`http://localhost:3000/costs`)
2. Click **"Add Cost"**
3. Select Project
4. Select Resource Group (filtered by project)
5. Enter month and cost amount
6. Click **"Add Cost"**

## Step 7: View Tagged Costs

### Via Dashboard:

- **Cost Trends Chart**: Shows monthly costs aggregated by all resource groups
- **Regional Distribution**: Shows costs grouped by project region
- **Statistics Cards**: Shows total cost across all projects/resource groups

### Via API:

```bash
# Get all monthly costs
GET http://localhost:8000/api/costs/monthly

# Get costs for specific project
GET http://localhost:8000/api/costs/monthly?project_id=1

# Get costs for specific resource group
GET http://localhost:8000/api/costs/monthly?resource_group_id=1

# Get cost summary for project + resource group
GET http://localhost:8000/api/costs/summary/1/1
```

## Troubleshooting

### Error: "Azure credentials not configured"

**Solution:**
1. Check that all 4 environment variables are set in `backend/.env`
2. Restart the backend server
3. Verify credentials are correct

### Error: "Failed to authenticate with Azure"

**Solution:**
1. Verify service principal credentials are correct
2. Check service principal has "Cost Management Reader" role
3. Ensure subscription ID is correct
4. Verify tenant ID matches the subscription tenant

### Error: "Resource group not found" (during sync)

**Solution:**
1. Verify resource group name matches exactly (case-sensitive)
2. Check resource group exists in the specified subscription
3. Ensure service principal has Reader role on subscription

### Error: "No costs returned"

**Solution:**
1. Azure Cost Management API has delays (costs available after 24-48 hours)
2. Verify date range has actual cost data
3. Check resource group has active resources during the period
4. Ensure resources are generating costs

### Cost sync returns 0 records

**Possible reasons:**
1. Date range has no cost data
2. Resource group doesn't exist
3. Resources in resource group haven't generated costs
4. Azure Cost Management API delay (wait 24-48 hours)

## Required Azure Permissions

Your service principal needs:

1. **Cost Management Reader**
   - Role ID: `72fafb9e-0641-4937-9268-a91bfd8191a3`
   - Scope: Subscription or Resource Group
   - Purpose: Read cost data

2. **Reader** (optional but recommended)
   - Scope: Subscription
   - Purpose: List resource groups

### Grant permissions via Azure CLI:

```bash
# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id --output tsv)

# Get service principal object ID
SP_OBJECT_ID=$(az ad sp show --id $AZURE_CLIENT_ID --query id --output tsv)

# Grant Cost Management Reader role
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role "Cost Management Reader" \
  --scope /subscriptions/$SUBSCRIPTION_ID

# Grant Reader role (optional)
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role "Reader" \
  --scope /subscriptions/$SUBSCRIPTION_ID
```

## Cost Tagging Workflow

### Complete Workflow:

```
1. Create Project
   └─> POST /api/projects/
       ↓
2. (Optional) Create Resource Group manually
   └─> POST /api/resource-groups/
       ↓
3. Sync Costs from Azure OR Add Manual Cost
   ├─> POST /api/azure/sync-costs (from Azure)
   └─> POST /api/costs/monthly (manual)
       ↓
4. Costs are automatically tagged to:
   ├─> project_id
   ├─> resource_group_id
   └─> month
       ↓
5. View in Dashboard
   ├─> Cost Trends Chart
   ├─> Regional Distribution
   └─> Statistics Cards
```

## Best Practices

1. **Security**:
   - Never commit `.env` files
   - Use Azure Key Vault for production
   - Rotate service principal secrets regularly

2. **Cost Management**:
   - Sync costs daily/weekly (Azure API has delays)
   - Tag Azure resources properly in Azure
   - Use resource group naming conventions

3. **Organization**:
   - One project per business unit/client
   - Resource groups aligned with projects
   - Consistent naming: `rg-{project}-{environment}`

## Next Steps

1. ✅ Set up Azure Service Principal
2. ✅ Configure environment variables
3. ✅ Test connection: `GET /api/azure/configured`
4. ✅ List resource groups: `GET /api/azure/resource-groups`
5. ✅ Create a project
6. ✅ Sync costs: `POST /api/azure/sync-costs`
7. ✅ View in dashboard

## Additional Resources

- [Azure Cost Management API Documentation](https://learn.microsoft.com/en-us/rest/api/cost-management/)
- [Azure Service Principal Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
- [Azure RBAC Roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles)
