"""
Azure Cost Management Service
Connects to Azure to fetch cost data from Azure Cost Management API
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.resource import ResourceManagementClient
from ..core.config import settings


class AzureCostService:
    """Service to fetch costs from Azure Cost Management API"""
    
    def __init__(self):
        self.credential = None
        if settings.AZURE_CLIENT_ID and settings.AZURE_CLIENT_SECRET and settings.AZURE_TENANT_ID:
            self.credential = ClientSecretCredential(
                tenant_id=settings.AZURE_TENANT_ID,
                client_id=settings.AZURE_CLIENT_ID,
                client_secret=settings.AZURE_CLIENT_SECRET
            )
        else:
            # Try default credential (for local dev with Azure CLI)
            try:
                self.credential = DefaultAzureCredential()
            except Exception:
                pass
        
        self.subscription_id = getattr(settings, 'AZURE_SUBSCRIPTION_ID', None)
    
    def is_configured(self) -> bool:
        """Check if Azure credentials are configured"""
        return self.credential is not None and self.subscription_id is not None
    
    def get_resource_group_costs(
        self,
        resource_group_name: str,
        start_date: datetime,
        end_date: datetime,
        subscription_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch costs for a specific resource group from Azure Cost Management API
        
        Args:
            resource_group_name: Name of the Azure resource group
            start_date: Start date for cost query
            end_date: End date for cost query
            subscription_id: Azure subscription ID (optional, uses default if not provided)
        
        Returns:
            List of cost records with date and amount
        """
        if not self.is_configured():
            raise ValueError("Azure credentials not configured. Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, and AZURE_SUBSCRIPTION_ID")
        
        sub_id = subscription_id or self.subscription_id
        if not sub_id:
            raise ValueError("Azure subscription ID not configured")
        
        try:
            cost_client = CostManagementClient(self.credential)
            resource_client = ResourceManagementClient(self.credential, sub_id)
            
            # Get resource group details
            resource_group = resource_client.resource_groups.get(resource_group_name)
            
            # Query cost data
            # Note: Azure Cost Management API requires specific scope and query format
            scope = f"/subscriptions/{sub_id}/resourceGroups/{resource_group_name}"
            
            # This is a simplified example - actual implementation would use Query API
            # For production, you'd use the actual Azure Cost Management Query API
            costs = []
            
            # Placeholder - actual implementation would call Azure Cost Management API
            # Example structure:
            # query_definition = {
            #     "type": "ActualCost",
            #     "timeframe": "Custom",
            #     "timePeriod": {
            #         "from": start_date.isoformat(),
            #         "to": end_date.isoformat()
            #     },
            #     "dataset": {
            #         "granularity": "Daily",
            #         "aggregation": {
            #             "totalCost": {"name": "PreTaxCost", "function": "Sum"}
            #         },
            #         "grouping": []
            #     }
            # }
            # result = cost_client.query.usage(scope=scope, parameters=query_definition)
            
            return costs
            
        except Exception as e:
            raise Exception(f"Failed to fetch Azure costs: {str(e)}")
    
    def list_resource_groups(self, subscription_id: Optional[str] = None) -> List[Dict]:
        """
        List all resource groups in a subscription
        
        Returns:
            List of resource group dictionaries with name and metadata
        """
        if not self.is_configured():
            raise ValueError("Azure credentials not configured")
        
        sub_id = subscription_id or self.subscription_id
        if not sub_id:
            raise ValueError("Azure subscription ID not configured")
        
        try:
            resource_client = ResourceManagementClient(self.credential, sub_id)
            resource_groups = resource_client.resource_groups.list()
            
            return [
                {
                    "name": rg.name,
                    "location": rg.location,
                    "id": rg.id,
                    "tags": rg.tags or {}
                }
                for rg in resource_groups
            ]
        except Exception as e:
            raise Exception(f"Failed to list resource groups: {str(e)}")


# Global instance
azure_cost_service = AzureCostService()
