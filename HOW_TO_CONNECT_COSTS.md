# How to Tag Costs to Resource Groups & Connect to Azure Cloud

## Quick Answer

### 1. Tag Costs to Resource Groups

Costs are automatically linked to resource groups when you create them. The relationship is:
- **Project** → **Resource Group** → **Costs**

Each cost entry requires:
- `project_id` - The project it belongs to
- `resource_group_id` - The resource group it's tagged to
- `month` - The month the cost applies to
- `cost` - The cost amount

### 2. Connect to Azure Cloud

You need to set up Azure credentials and use the sync functionality.

---

## Method 1: Add Costs Manually (Via UI)

### Step 1: Go to Costs Page
1. Visit **http://localhost:3000/costs**
2. Click **"Add Cost"** button

### Step 2: Fill in the Form
1. **Select Project** - Choose from existing projects
2. **Select Resource Group** - Choose from resource groups in that project
3. **Select Month** - Pick the month for the cost
4. **Enter Cost Amount** - Enter the cost in dollars
5. Click **"Add Cost"**

The cost is now tagged to that resource group!

---

## Method 2: Add Costs via API

### Create Monthly Cost

```bash
POST http://localhost:8000/api/costs/monthly
Content-Type: application/json

{
  "project_id": 1,
  "resource_group_id": 1,
  "month": "2024-01-01",
  "cost": 5000.00
}
```

This tags $5000 to resource group ID 1 for January 2024.

---

## Method 3: Connect to Azure and Sync Costs Automatically

### Step 1: Set Up Azure Credentials

Create/update `backend/.env`:

```env
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

### Step 2: Create Azure Service Principal

```bash
# Install Azure CLI if not installed
# Then run:
az login

# Create service principal with Cost Management Reader role
az ad sp create-for-rbac --name "operations-dashboard" \
  --role "Cost Management Reader" \
  --scopes /subscriptions/{your-subscription-id}

# Output will give you:
# appId → use as AZURE_CLIENT_ID
# password → use as AZURE_CLIENT_SECRET
# tenant → use as AZURE_TENANT_ID
```

### Step 3: Check Azure Connection

```bash
curl http://localhost:8000/api/azure/configured
```

Should return: `{"configured": true, "message": "Azure credentials configured"}`

### Step 4: Sync Costs from Azure

**Option A: Via API**

```bash
POST http://localhost:8000/api/azure/sync-costs
Content-Type: application/json

{
  "project_id": 1,
  "resource_group_name": "rg-production",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z"
}
```

**Option B: Via UI (Future Enhancement)**
- Go to a project page
- Click "Sync from Azure"
- Enter resource group name and date range
- Click "Sync Costs"

---

## How the Cost-to-Resource Group Tagging Works

### Database Structure

```
project (1) ──┐
              ├── resource_group (many)
resource (1) ──┘      │
                       │
                       ├── monthly_cost (many)
                       │   - project_id
                       │   - resource_group_id  ← This is the "tag"
                       │   - month
                       │   - cost
                       │
                       └── project_cost_summary (1)
                           - project_id
                           - resource_group_id  ← Also tagged here
                           - total_cost_to_date
```

### Example Flow

1. **Create Project**: "Cloud Migration"
   - Gets `project_id = 1`

2. **Create Resource Group**: "rg-production"
   - Gets `resource_group_id = 1`
   - Linked to `project_id = 1`

3. **Add Cost**: $5000 for January 2024
   - Stored in `monthly_cost` table
   - `project_id = 1`
   - `resource_group_id = 1` ← **This is the tag**
   - `month = 2024-01-01`
   - `cost = 5000.00`

The cost is now **tagged** to resource group `rg-production`!

---

## View Tagged Costs

### Via Dashboard
- Visit **http://localhost:3000**
- Costs are aggregated and shown in charts
- Grouped by resource groups automatically

### Via Costs Page
- Visit **http://localhost:3000/costs**
- See all costs in a table
- Each row shows: Project → Resource Group → Month → Cost

### Via API

```bash
# Get all costs
GET http://localhost:8000/api/costs/monthly

# Get costs for specific resource group
GET http://localhost:8000/api/costs/monthly?resource_group_id=1

# Get costs for specific project
GET http://localhost:8000/api/costs/monthly?project_id=1
```

---

## Azure Connection Troubleshooting

### Issue: "Azure credentials not configured"
**Solution**: Add all 4 environment variables to `backend/.env`

### Issue: "Failed to authenticate"
**Solution**: 
1. Verify service principal credentials
2. Check service principal has "Cost Management Reader" role
3. Ensure subscription ID is correct

### Issue: "Resource group not found"
**Solution**: 
1. Verify resource group name matches exactly (case-sensitive)
2. Check resource group exists in the subscription
3. Ensure service principal has Reader role on subscription

### Issue: "No costs returned"
**Solution**:
1. Azure Cost Management API has 24-48 hour delays
2. Verify date range has cost data
3. Check resource group has active resources during the period

---

## Quick Reference

### Cost Tagging Endpoints
- `POST /api/costs/monthly` - Tag a cost to resource group
- `GET /api/costs/monthly` - View tagged costs
- `POST /api/costs/summary` - Update cost summary

### Azure Connection Endpoints
- `GET /api/azure/configured` - Check if Azure is configured
- `GET /api/azure/resource-groups` - List Azure resource groups
- `POST /api/azure/sync-costs` - Sync costs from Azure
- `GET /api/azure/resource-groups/{name}/costs` - Get Azure costs

### Resource Group Endpoints
- `POST /api/resource-groups` - Create resource group
- `GET /api/resource-groups` - List resource groups
- `GET /api/resource-groups?project_id=1` - List by project

---

## Example: Complete Workflow

1. **Create Project**:
   ```bash
   POST /api/projects/
   {
     "project_name": "Production App",
     "project_type": "Internal",
     ...
   }
   # Returns: project_id = 1
   ```

2. **Create Resource Group** (optional, can auto-create):
   ```bash
   POST /api/resource-groups/
   {
     "project_id": 1,
     "resource_group_name": "rg-production",
     "status": "Active"
   }
   # Returns: resource_group_id = 1
   ```

3. **Tag Cost to Resource Group**:
   ```bash
   POST /api/costs/monthly
   {
     "project_id": 1,
     "resource_group_id": 1,  ← Tag here
     "month": "2024-01-01",
     "cost": 5000.00
   }
   ```

4. **Or Sync from Azure**:
   ```bash
   POST /api/azure/sync-costs
   {
     "project_id": 1,
     "resource_group_name": "rg-production",  ← Auto-creates if needed
     "start_date": "2024-01-01T00:00:00Z",
     "end_date": "2024-01-31T23:59:59Z"
   }
   # Automatically tags costs to resource group!
   ```

5. **View Tagged Costs**:
   - Dashboard: http://localhost:3000
   - Costs Page: http://localhost:3000/costs
   - API: `GET /api/costs/monthly?resource_group_id=1`

---

## Summary

**Cost Tagging**: Costs are tagged to resource groups via `resource_group_id` field in the `monthly_cost` table.

**Azure Connection**: 
1. Set up service principal
2. Add credentials to `.env`
3. Use `/api/azure/sync-costs` to import costs
4. Costs are automatically tagged to resource groups!

