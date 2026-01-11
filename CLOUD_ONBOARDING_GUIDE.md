# Cloud Onboarding Guide

This guide will help you connect AWS, Azure, and Google Cloud Platform (GCP) to your Multi-Cloud Operations Dashboard.

## 🚀 Quick Access

Visit the **Cloud Onboarding** page at: `http://localhost:3001/cloud-onboarding`

## ☁️ Supported Cloud Providers

### 1. **Amazon Web Services (AWS)**
- **Service**: AWS Cost and Billing API, EC2, S3, RDS
- **Authentication**: IAM Access Keys
- **Regions**: All AWS regions supported
- **Features**: Cost tracking, resource monitoring, automated sync

### 2. **Microsoft Azure**
- **Service**: Azure Cost Management API, Resource Manager
- **Authentication**: Service Principal (App Registration)
- **Regions**: All Azure regions supported
- **Features**: Cost tracking, resource group monitoring, subscription management

### 3. **Google Cloud Platform (GCP)**
- **Service**: Cloud Billing API, Resource Manager API
- **Authentication**: Service Account Key
- **Regions**: All GCP regions supported
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

#### Step 3: Add to Dashboard
1. Go to Cloud Onboarding page
2. Click "Add Connection"
3. Select "Amazon Web Services"
4. Fill in:
   - **Connection Name**: "My AWS Production"
   - **Access Key ID**: From CSV file
   - **Secret Access Key**: From CSV file
   - **Default Region**: Your primary region (e.g., us-east-1)
   - **Account ID**: Your AWS account ID

### Azure Setup

#### Step 1: Create App Registration
1. Go to Azure Portal → Azure Active Directory → App registrations
2. Click "New registration"
3. Enter name: "Operations Dashboard"
4. Select "Accounts in this organizational directory only"
5. Click "Register"

#### Step 2: Create Client Secret
1. In your app registration → Certificates & secrets
2. Click "New client secret"
3. Add description and expiration
4. **Copy the secret value immediately** (you won't see it again)

#### Step 3: Assign Permissions
1. Go to Subscriptions → Select your subscription
2. Click "Access control (IAM)" → "Add role assignment"
3. Select "Cost Management Reader" role
4. Assign to your app registration

#### Step 4: Get Required IDs
- **Subscription ID**: From Subscriptions page
- **Client ID**: From app registration Overview page (Application ID)
- **Tenant ID**: From app registration Overview page (Directory ID)
- **Client Secret**: From step 2

#### Step 5: Add to Dashboard
1. Go to Cloud Onboarding page
2. Click "Add Connection"
3. Select "Microsoft Azure"
4. Fill in all the IDs and secret from above steps

### GCP Setup

#### Step 1: Create Service Account
1. Go to GCP Console → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Enter name: "operations-dashboard"
4. Add description and click "Create and Continue"

#### Step 2: Assign Roles
Add these roles to the service account:
- `Billing Account Viewer`
- `Cloud Asset Viewer`
- `Compute Viewer`
- `Project Viewer`

#### Step 3: Create Key
1. Click on your service account
2. Go to "Keys" tab → "Add Key" → "Create new key"
3. Select "JSON" format
4. Download the JSON file

#### Step 4: Add to Dashboard
1. Go to Cloud Onboarding page
2. Click "Add Connection"
3. Select "Google Cloud Platform"
4. Fill in:
   - **Connection Name**: "My GCP Project"
   - **Project ID**: From GCP console or JSON file
   - **Service Account Key**: Copy and paste the entire JSON content
   - **Default Region**: Your primary region (e.g., us-central1)

## 🔒 Security Best Practices

### Credential Management
- **Never share credentials** in plain text
- **Use least privilege** - only grant necessary permissions
- **Rotate credentials regularly** (every 90 days recommended)
- **Monitor access logs** for unusual activity

### Network Security
- **Use HTTPS only** for all API communications
- **Implement IP whitelisting** if possible
- **Enable MFA** on all cloud accounts
- **Use VPN** for accessing cloud resources

### Access Control
- **Create dedicated service accounts** for the dashboard
- **Don't use personal accounts** for automation
- **Document all permissions** granted
- **Regular access reviews** and cleanup

## 📊 Features After Connection

### Cost Monitoring
- **Real-time cost tracking** across all connected clouds
- **Budget alerts** and spending notifications
- **Cost breakdown** by service, region, and project
- **Historical cost analysis** and trends

### Resource Discovery
- **Automatic resource scanning** across all clouds
- **Resource inventory** with metadata
- **Compliance monitoring** and reporting
- **Resource optimization** recommendations

### Automated Sync
- **Hourly sync** of cost and resource data
- **Real-time alerts** for cost spikes
- **Automated reporting** and dashboards
- **Integration** with existing tools

## 🛠️ Troubleshooting

### Common Issues

#### AWS Connection Failed
```
Error: "Access Denied"
Solution: Check IAM permissions, ensure billing access is enabled
```

#### Azure Authentication Error
```
Error: "Invalid client secret"
Solution: Regenerate client secret, check expiration date
```

#### GCP Permission Denied
```
Error: "Insufficient permissions"
Solution: Verify service account roles, check project permissions
```

### Testing Connections
1. Use the "Test" button on each connection
2. Check the connection status indicators
3. Review error messages in the dashboard
4. Verify credentials in cloud provider console

### Sync Issues
- **Check internet connectivity**
- **Verify API quotas** aren't exceeded
- **Review cloud provider service status**
- **Check dashboard logs** for detailed errors

## 📈 Monitoring and Alerts

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

### Updates and Patches
- **Keep dashboard updated** to latest version
- **Monitor cloud provider** API changes
- **Update permissions** as needed
- **Test connections** after updates

## 📞 Support

### Getting Help
1. **Check system status** page first
2. **Review error messages** in detail
3. **Test individual connections** to isolate issues
4. **Check cloud provider** service status pages

### Documentation Links
- [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/)
- [Azure App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [GCP Service Account Documentation](https://cloud.google.com/iam/docs/service-accounts)

---

**Ready to connect your clouds? Visit the [Cloud Onboarding](http://localhost:3001/cloud-onboarding) page to get started! 🚀**