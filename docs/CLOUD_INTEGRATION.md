# Cloud Integration Guide

This comprehensive guide covers connecting AWS, Azure, and Google Cloud Platform (GCP) to your Multi-Cloud Operations Dashboard, including cost management and resource synchronization.

## 🚀 Quick Access

Visit the **Cloud Onboarding** page at: `http://localhost:3001/cloud-onboarding`

## ☁️ Supported Cloud Providers

### Amazon Web Services (AWS)
- **Services**: Cost and Billing API, EC2, S3, RDS
- **Authentication**: IAM Access Keys
- **Features**: Cost tracking, resource monitoring, automated sync

### Microsoft Azure
- **Services**: Cost Management API, Resource Manager
- **Authentication**: Service Principal (App Registration)
- **Features**: Cost tracking, resource group monitoring, subscription management

### Google Cloud Platform (GCP)
- **Services**: Cloud Billing API, Resource Manager API
- **Authentication**: Service Account Key
- **Features**: Cost tracking, project monitoring, resource discovery

## 🔧 Setup Instructions

### AWS Setup

#### Step 1: Create IAM User
1. Go to AWS Console → IAM → Users
2. Click "Add user" → Enter username (e.g., "operations-dashboard")
3. Select "Programmatic access"
4. Attach policies:
   - `ReadOnlyAccess`
   - `AWSBillingReadOnlyAccess`
   - `AWSCostAndBillingReadOnlyAccess`

#### Step 2: Get Credentials
1. Download the CSV file with Access Key ID and Secret Access Key
2. Note your AWS Account ID (found in top-right corner)

#### Step 3: Configure Environment Variables
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id
```

### Azure Setup

#### Step 1: Create Service Principal
```bash
# Using Azure CLI (Recommended)
az login
SUBSCRIPTION_ID=$(az account show --query id --output tsv)

# Create service principal with Cost Management Reader role
az ad sp create-for-rbac \
  --name "operations-dashboard-sp" \
  --role "Cost Management Reader" \
  --scopes /subscriptions/$SUBSCRIPTION_ID
```

**Output:**
```json
{
  "appId": "xxxx-xxxx-xxxx-xxxx",     # AZURE_CLIENT_ID
  "password": "xxxx-xxxx-xxxx-xxxx",  # AZURE_CLIENT_SECRET
  "tenant": "xxxx-xxxx-xxxx-xxxx"     # AZURE_TENANT_ID
}
```

#### Step 2: Configure Environment Variables
```env
# Azure Configuration
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

#### Step 3: Test Connection
```bash
# Check if Azure is configured
curl http://localhost:8000/api/azure/configured

# List Azure resource groups
curl http://localhost:8000/api/azure/resource-groups
```

### GCP Setup

#### Step 1: Create Service Account
1. Go to GCP Console → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Enter name: "operations-dashboard"
4. Assign roles:
   - `Billing Account Viewer`
   - `Cloud Asset Viewer`
   - `Compute Viewer`
   - `Project Viewer`

#### Step 2: Create Key
1. Click on your service account
2. Go to "Keys" tab → "Add Key" → "Create new key"
3. Select "JSON" format and download

#### Step 3: Configure Environment Variables
```env
# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GCP_PROJECT_ID=your-project-id
GCP_DEFAULT_REGION=us-central1
```

## 💰 Cost Management

### Cost-to-Resource Group Mapping

Costs are linked to resource groups through these relationships:

```
Project (1) ──→ (Many) Resource Groups
                ↓
            (Many) Monthly Costs
```

#### Key Tables:
- **`resource_group`**: Links resource groups to projects
- **`monthly_cost`**: Monthly cost data tagged to resource groups
- **`project_cost_summary`**: Aggregated cost summaries

### Adding Costs

#### Method 1: Manual Entry via API
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

#### Method 2: Azure Cost Sync
```bash
POST /api/azure/sync-costs
Content-Type: application/json

{
  "project_id": 1,
  "resource_group_name": "rg-production",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z"
}
```

#### Method 3: UI Cost Entry
1. Go to **Costs** page (`http://localhost:3001/costs`)
2. Click **"Add Cost"**
3. Select Project and Resource Group
4. Enter month and cost amount
5. Click **"Add Cost"**

### Viewing Costs

#### Dashboard View
- **Cost Trends Chart**: Monthly costs aggregated by resource groups
- **Regional Distribution**: Costs grouped by project region
- **Statistics Cards**: Total cost across all projects/resource groups

#### API Endpoints
```bash
# Get all monthly costs
GET /api/costs/monthly

# Get costs for specific project
GET /api/costs/monthly?project_id=1

# Get costs for specific resource group
GET /api/costs/monthly?resource_group_id=1

# Get cost summary
GET /api/costs/summary/1/1
```

## 🔄 Automated Sync Workflows

### Complete Azure Workflow

1. **Create Project**:
```bash
POST /api/projects/
{
  "project_name": "Cloud Migration",
  "project_type": "Internal",
  "member_firm": "US Office",
  "deployed_region": "US"
}
```

2. **Sync Costs from Azure**:
```bash
POST /api/azure/sync-costs
{
  "project_id": 1,
  "resource_group_name": "rg-production",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z"
}
```

3. **View Results**:
   - System creates resource group if it doesn't exist
   - Fetches costs from Azure Cost Management API
   - Creates monthly cost entries linked to resource group
   - Updates project cost summary automatically

## 🔒 Security Best Practices

### Credential Management
- **Never commit credentials** to version control
- **Use environment variables** for all sensitive data
- **Rotate credentials regularly** (every 90 days)
- **Use least privilege** access policies
- **Monitor access logs** for unusual activity

### Required Permissions

#### AWS Permissions
- `ReadOnlyAccess`
- `AWSBillingReadOnlyAccess`
- `AWSCostAndBillingReadOnlyAccess`

#### Azure Permissions
- `Cost Management Reader` (required)
- `Reader` (recommended for resource group listing)

#### GCP Permissions
- `Billing Account Viewer`
- `Cloud Asset Viewer`
- `Compute Viewer`
- `Project Viewer`

## 🛠️ Troubleshooting

### Common Issues

#### Azure Authentication Errors
```
Error: "Azure credentials not configured"
Solution: Set all 4 environment variables in backend/.env
```

```
Error: "Failed to authenticate with Azure"
Solution: 
- Verify service principal credentials
- Check "Cost Management Reader" role assignment
- Ensure subscription ID is correct
```

#### Cost Sync Issues
```
Error: "Resource group not found"
Solution:
- Verify resource group name matches exactly (case-sensitive)
- Check resource group exists in subscription
- Ensure service principal has Reader role
```

```
Error: "No costs returned"
Solution:
- Azure Cost Management API has 24-48 hour delays
- Verify date range has actual cost data
- Check resource group has active resources
```

#### Connection Testing
```bash
# Test Azure connection
curl http://localhost:8000/api/azure/configured

# Test AWS connection (if implemented)
curl http://localhost:8000/api/aws/configured

# Test GCP connection (if implemented)
curl http://localhost:8000/api/gcp/configured
```

## 📊 Monitoring and Alerts

### Dashboard Metrics
- **Connection health** status for each provider
- **Last sync time** and success rate
- **Resource count** and cost summaries
- **Error rates** and performance metrics

### Alert Configuration
- **Cost threshold alerts** (e.g., >$1000/month)
- **Connection failure** notifications
- **Resource compliance** violations
- **Security** and access alerts

## 🔄 Maintenance

### Regular Tasks
- **Monthly credential review** and rotation
- **Quarterly access audit** and cleanup
- **Cost optimization** reviews
- **Security assessment** and updates

### Automated Sync Schedule
- **Hourly sync** of cost and resource data
- **Daily aggregation** of cost summaries
- **Weekly reporting** and analysis
- **Monthly cost optimization** reviews

## 📚 API Reference

### Azure Endpoints
- `GET /api/azure/configured` - Check Azure configuration
- `GET /api/azure/resource-groups` - List Azure resource groups
- `POST /api/azure/sync-costs` - Sync costs from Azure
- `GET /api/azure/resource-groups/{name}/costs` - Get Azure costs

### Cost Management Endpoints
- `POST /api/costs/monthly` - Add monthly cost
- `GET /api/costs/monthly` - List monthly costs
- `POST /api/costs/summary` - Update cost summary
- `GET /api/costs/summary/{project_id}/{resource_group_id}` - Get cost summary

### Resource Group Endpoints
- `POST /api/resource-groups` - Create resource group
- `GET /api/resource-groups` - List resource groups
- `GET /api/resource-groups?project_id=1` - List by project

## 📞 Support Resources

### Documentation Links
- [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/)
- [Azure App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [GCP Service Account Documentation](https://cloud.google.com/iam/docs/service-accounts)
- [Azure Cost Management API](https://learn.microsoft.com/en-us/rest/api/cost-management/)

### Getting Help
1. Check the [API documentation](http://localhost:8000/docs) when backend is running
2. Review error messages in browser console and server logs
3. Verify all environment variables are properly configured
4. Test individual cloud connections to isolate issues

---

**Ready to connect your clouds? Visit the [Cloud Onboarding](http://localhost:3001/cloud-onboarding) page to get started! 🚀**