"""
Azure Cost Management Service
Handles integration with Azure Cost Management API
"""
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.resource import ResourceManagementClient
from ..core.config import settings


class AzureCostService:
    def __init__(self):
        self.credential = None
        self.cost_client = None
        self.resource_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Azure clients with credentials"""
        try:
            if (settings.AZURE_CLIENT_ID and 
                settings.AZURE_CLIENT_SECRET and 
                settings.AZURE_TENANT_ID):
                
                self.credential = ClientSecretCredential(
                    tenant_id=settings.AZURE_TENANT_ID,
                    client_id=settings.AZURE_CLIENT_ID,
                    client_secret=settings.AZURE_CLIENT_SECRET
                )
            else:
                # Fallback to default credential (managed identity, CLI, etc.)
                self.credential = DefaultAzureCredential()
            
            if settings.AZURE_SUBSCRIPTION_ID:
                self.cost_client = CostManagementClient(
                    credential=self.credential,
                    subscription_id=settings.AZURE_SUBSCRIPTION_ID
                )
                self.resource_client = ResourceManagementClient(
                    credential=self.credential,
                    subscription_id=settings.AZURE_SUBSCRIPTION_ID
                )
        except Exception as e:
            print(f"Failed to initialize Azure clients: {e}")
    
    def is_configured(self) -> bool:
        """Check if Azure credentials are properly configured"""
        return (self.credential is not None and 
                settings.AZURE_SUBSCRIPTION_ID is not None)
    
    def list_resource_groups(self, subscription_id: Optional[str] = None) -> List[Dict]:
        """List all resource groups in the subscription"""
        if not self.is_configured():
            raise Exception("Azure credentials not configured")
        
        try:
            resource_groups = []
            for rg in self.resource_client.resource_groups.list():
                resource_groups.append({
                    "name": rg.name,
                    "location": rg.location,
                    "id": rg.id,
                    "tags": rg.tags or {}
                })
            return resource_groups
        except Exception as e:
            raise Exception(f"Failed to list resource groups: {e}")
    
    def get_resource_group_costs(
        self, 
        resource_group_name: str,
        start_date: datetime,
        end_date: datetime,
        subscription_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get costs for a specific resource group within a date range
        Returns monthly aggregated costs
        """
        if not self.is_configured():
            raise Exception("Azure credentials not configured")
        
        try:
            # For demo purposes, return mock data
            # In production, this would use the Azure Cost Management API
            costs = []
            current_date = start_date.replace(day=1)  # Start of month
            
            while current_date <= end_date:
                # Mock cost calculation (replace with actual API call)
                import random
                mock_cost = random.uniform(100, 5000)
                
                costs.append({
                    "date": current_date,
                    "cost": round(mock_cost, 2),
                    "currency": "USD",
                    "resource_group": resource_group_name
                })
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            return costs
            
        except Exception as e:
            raise Exception(f"Failed to get costs for resource group {resource_group_name}: {e}")
    
    def get_subscription_costs(
        self,
        start_date: datetime,
        end_date: datetime,
        subscription_id: Optional[str] = None
    ) -> List[Dict]:
        """Get costs for entire subscription"""
        if not self.is_configured():
            raise Exception("Azure credentials not configured")
        
        # Mock implementation - replace with actual Azure Cost Management API calls
        try:
            costs = []
            current_date = start_date.replace(day=1)
            
            while current_date <= end_date:
                import random
                mock_cost = random.uniform(1000, 15000)
                
                costs.append({
                    "date": current_date,
                    "cost": round(mock_cost, 2),
                    "currency": "USD",
                    "subscription_id": subscription_id or settings.AZURE_SUBSCRIPTION_ID
                })
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            return costs
            
        except Exception as e:
            raise Exception(f"Failed to get subscription costs: {e}")


# Global instance
azure_cost_service = AzureCostService()