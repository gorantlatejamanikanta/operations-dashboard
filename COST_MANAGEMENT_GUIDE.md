# Cost Management and Azure Integration Guide

## Overview

This guide explains how to:
1. **Tag costs to resource groups** - Associate costs with resource groups
2. **Connect to Azure Cloud** - Sync costs from Azure Cost Management API
3. **Import cloud costs** - Automatically import costs from Azure into the dashboard

## Cost-to-Resource Group Mapping

Costs in the system are linked to resource groups through three main tables:

### 1. Monthly Costs (`monthly_cost`)
Links costs to projects and resource groups by month:
- `project_id` - The project this cost belongs to
- `resource_group_id` - The resource group this cost is for
- `month` - The month this cost applies to
- `cost` - The cost amount

### 2. Cost Summary (`project_cost_summary`)
Aggregated cost summary for project-resource group pairs:
- `project_id` + `resource_group_id` - Composite key
- `total_cost_to_date` - Total accumulated cost
- `gpt_costs_to_date` - GPT/AI-related costs
- `costs_passed_back_to_date` - Costs passed back to client
- `updated_date` - Last update timestamp

### 3. Cost Data (`cost_data`)
Detailed cost data entries:
- `key` - Unique identifier
- `resource_group_id` - Linked resource group
- `period` - Cost period
- `cost` - Cost amount

## Adding Costs via API

### Create Monthly Cost

```bash
POST /api/costs/monthly
Content-Type: application/json

{
  "project_id": 1,
  "resource_group_id": 1,
  "month": "2024-01-01",
  "cost": 5000.00
}
```

### Update Cost Summary

```bash
POST /api/costs/summary
Content-Type: application/json

{
  "project_id": 1,
  "resource_group_id": 1,
  "total_cost_to_date": 60000.00,
  "updated_date": "2024-01-15",
  "gpt_costs_to_date": 5000.00,
  "costs_passed_back_to_date": 55000.00
}
```

## Azure Cloud Integration

### Prerequisites

1. **Azure Service Principal** with Cost Management Reader permissions
2. **Subscription ID** - Your Azure subscription ID
3. **Environment Variables** - Set in `backend/.env`:

```env
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

### Setting Up Azure Service Principal

1. **Create Service Principal**:
```bash
az ad sp create-for-rbac --name "operations-dashboard" \
  --role "Cost Management Reader" \
  --scopes /subscriptions/{subscription-id}
```

2. **Get Credentials**:
```bash
# Output will contain:
# appId (use as AZURE_CLIENT_ID)
# password (use as AZURE_CLIENT_SECRET)
# tenant (use as AZURE_TENANT_ID)
```

3. **Grant Permissions**:
```bash
# Ensure the service principal has:
# - Cost Management Reader role
# - Reader role on subscription or resource groups
```

### Azure API Endpoints

#### 1. Check Azure Configuration

```bash
GET /api/azure/configured

# Response:
{
  "configured": true,
  "message": "Azure credentials configured"
}
```

#### 2. List Azure Resource Groups

```bash
GET /api/azure/resource-groups?subscription_id={optional-sub-id}

# Response:
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

#### 3. Sync Costs from Azure

```bash
POST /api/azure/sync-costs
Content-Type: application/json

{
  "project_id": 1,
  "resource_group_name": "rg-production",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "subscription_id": "optional-sub-id"
}

# Response:
{
  "message": "Successfully synced 31 cost records",
  "resource_group_id": 1,
  "records_imported": 31
}
```

#### 4. Get Costs for Resource Group

```bash
GET /api/azure/resource-groups/{resource-group-name}/costs?start_date=2024-01-01&end_date=2024-01-31

# Response:
{
  "costs": [
    {
      "date": "2024-01-01",
      "cost": 150.00
    }
  ]
}
```

## Workflow: Syncing Azure Costs

1. **Create a Project** (if not exists):
```bash
POST /api/projects/
{
  "project_name": "Cloud Migration",
  "project_type": "Internal",
  "member_firm": "US Office",
  "deployed_region": "US",
  ...
}
```

2. **Create Resource Group** (or use existing):
```bash
POST /api/resource-groups/
{
  "resource_group_name": "rg-production",
  "project_id": 1,
  "status": "Active"
}
```

3. **Sync Costs from Azure**:
```bash
POST /api/azure/sync-costs
{
  "project_id": 1,
  "resource_group_name": "rg-production",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z"
}
```

4. **View Costs in Dashboard**:
   - The dashboard will automatically show the synced costs
   - Monthly costs will appear in the cost trends chart
   - Cost summaries will be updated

## Manual Cost Entry

If you don't have Azure integration set up, you can manually add costs:

1. **Via API**:
```bash
POST /api/costs/monthly
{
  "project_id": 1,
  "resource_group_id": 1,
  "month": "2024-01-01",
  "cost": 5000.00
}
```

2. **Via Database** (for bulk imports):
```sql
INSERT INTO monthly_cost (project_id, resource_group_id, month, cost)
VALUES (1, 1, '2024-01-01', 5000.00);
```

## Cost Tags and Metadata

Resource groups can be tagged with metadata in Azure. These tags are useful for:
- Cost allocation
- Reporting
- Filtering

To see resource group tags:
```bash
GET /api/azure/resource-groups
```

Tags from Azure resource groups will be displayed in the API response.

## Troubleshooting

### Azure Authentication Issues

**Error**: "Azure credentials not configured"
- Solution: Set all required environment variables in `backend/.env`

**Error**: "Failed to authenticate with Azure"
- Solution: Verify service principal credentials and permissions
- Check: Service principal has "Cost Management Reader" role

### Cost Sync Issues

**Error**: "Resource group not found"
- Solution: Ensure the resource group name matches exactly (case-sensitive)
- Check: Resource group exists in the specified subscription

**Error**: "No costs returned"
- Solution: Verify date range has cost data
- Check: Resource group has active resources during the period
- Note: Azure Cost Management API may have delays (costs available after 24-48 hours)

### Permission Issues

Ensure the service principal has:
1. **Cost Management Reader** - To read cost data
2. **Reader** - To list resource groups
3. Scope: Subscription or Resource Group level

## Next Steps

1. Set up Azure Service Principal
2. Configure environment variables
3. Test connection: `GET /api/azure/configured`
4. List resource groups: `GET /api/azure/resource-groups`
5. Sync costs: `POST /api/azure/sync-costs`
6. View in dashboard: Refresh http://localhost:3000
