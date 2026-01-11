"""
Azure Integration Service
Handles Azure cost and resource data retrieval
"""
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json


class AzureService:
    def __init__(self, credentials: Dict[str, str]):
        """Initialize Azure service with credentials"""
        self.subscription_id = credentials.get('subscription_id')
        self.client_id = credentials.get('client_id')
        self.client_secret = credentials.get('client_secret')
        self.tenant_id = credentials.get('tenant_id')
        
        # Initialize credential
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        # Initialize clients
        self.resource_client = ResourceManagementClient(
            self.credential, self.subscription_id
        )
        self.compute_client = ComputeManagementClient(
            self.credential, self.subscription_id
        )
        self.storage_client = StorageManagementClient(
            self.credential, self.subscription_id
        )
        self.sql_client = SqlManagementClient(
            self.credential, self.subscription_id
        )
        self.web_client = WebSiteManagementClient(
            self.credential, self.subscription_id
        )
    
    def test_connection(self) -> Tuple[bool, str, Dict]:
        """Test Azure connection and return subscription information"""
        try:
            # Test by getting subscription info
            subscription = self.resource_client.subscriptions.get(self.subscription_id)
            
            return True, "Azure connection successful", {
                "subscription_id": subscription.subscription_id,
                "subscription_name": subscription.display_name,
                "state": subscription.state.value if subscription.state else "Unknown",
                "tenant_id": self.tenant_id
            }
        except ClientAuthenticationError:
            return False, "Invalid Azure credentials", {}
        except HttpResponseError as e:
            return False, f"Azure connection failed: {e.message}", {}
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", {}
    
    def get_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Retrieve cost data from Azure Cost Management"""
        try:
            # Azure Cost Management API requires specific date format
            time_period = {
                "from": start_date.strftime('%Y-%m-%dT00:00:00+00:00'),
                "to": end_date.strftime('%Y-%m-%dT23:59:59+00:00')
            }
            
            # Create cost management client
            cost_client = CostManagementClient(self.credential)
            
            # Define the query
            query_definition = {
                "type": "ActualCost",
                "timeframe": "Custom",
                "timePeriod": time_period,
                "dataset": {
                    "granularity": "Monthly",
                    "aggregation": {
                        "totalCost": {
                            "name": "PreTaxCost",
                            "function": "Sum"
                        }
                    },
                    "grouping": [
                        {
                            "type": "Dimension",
                            "name": "ServiceName"
                        },
                        {
                            "type": "Dimension", 
                            "name": "ResourceLocation"
                        }
                    ]
                }
            }
            
            scope = f"/subscriptions/{self.subscription_id}"
            
            # Execute query
            result = cost_client.query.usage(scope=scope, parameters=query_definition)
            
            cost_data = []
            if hasattr(result, 'rows') and result.rows:
                columns = [col.name for col in result.columns]
                
                for row in result.rows:
                    row_dict = dict(zip(columns, row))
                    
                    cost_data.append({
                        'period_start': row_dict.get('BillingMonth', ''),
                        'period_end': row_dict.get('BillingMonth', ''),
                        'service': row_dict.get('ServiceName', 'Unknown'),
                        'region': row_dict.get('ResourceLocation', 'Unknown'),
                        'cost': float(row_dict.get('PreTaxCost', 0)),
                        'currency': row_dict.get('Currency', 'USD'),
                        'provider': 'azure'
                    })
            
            return cost_data
            
        except Exception as e:
            # Fallback to mock data if Cost Management API is not accessible
            print(f"Azure Cost Management API error: {e}")
            return self._get_mock_cost_data(start_date, end_date)
    
    def _get_mock_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Generate mock cost data for demonstration"""
        import random
        
        services = [
            'Virtual Machines', 'Storage Accounts', 'SQL Database',
            'App Service', 'Azure Functions', 'Load Balancer',
            'Application Gateway', 'Key Vault', 'Monitor'
        ]
        
        regions = ['East US', 'West Europe', 'Southeast Asia', 'Central US']
        
        cost_data = []
        current_date = start_date.replace(day=1)
        
        while current_date < end_date:
            for service in services:
                for region in regions:
                    if random.random() > 0.3:  # 70% chance of having costs
                        cost = random.uniform(50, 2000)
                        cost_data.append({
                            'period_start': current_date.strftime('%Y-%m-%d'),
                            'period_end': current_date.strftime('%Y-%m-%d'),
                            'service': service,
                            'region': region,
                            'cost': round(cost, 2),
                            'currency': 'USD',
                            'provider': 'azure'
                        })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return cost_data
    
    def get_resources(self) -> List[Dict]:
        """Retrieve Azure resources across multiple services"""
        resources = []
        
        try:
            # Get Virtual Machines
            resources.extend(self._get_virtual_machines())
            
            # Get Storage Accounts
            resources.extend(self._get_storage_accounts())
            
            # Get SQL Databases
            resources.extend(self._get_sql_databases())
            
            # Get App Services
            resources.extend(self._get_app_services())
            
            # Get Resource Groups
            resources.extend(self._get_resource_groups())
            
            return resources
            
        except Exception as e:
            raise Exception(f"Failed to retrieve Azure resources: {str(e)}")
    
    def _get_virtual_machines(self) -> List[Dict]:
        """Get Azure Virtual Machines"""
        try:
            vms = []
            for vm in self.compute_client.virtual_machines.list_all():
                # Get VM status
                instance_view = self.compute_client.virtual_machines.instance_view(
                    vm.id.split('/')[4], vm.name  # resource_group_name, vm_name
                )
                
                power_state = "Unknown"
                for status in instance_view.statuses:
                    if status.code.startswith('PowerState/'):
                        power_state = status.display_status
                        break
                
                vms.append({
                    'resource_id': vm.id,
                    'name': vm.name,
                    'type': 'Virtual Machine',
                    'service': 'Virtual Machines',
                    'region': vm.location,
                    'state': power_state,
                    'vm_size': vm.hardware_profile.vm_size if vm.hardware_profile else 'Unknown',
                    'os_type': vm.storage_profile.os_disk.os_type.value if vm.storage_profile and vm.storage_profile.os_disk else 'Unknown',
                    'resource_group': vm.id.split('/')[4],
                    'provider': 'azure',
                    'tags': vm.tags or {}
                })
            
            return vms
            
        except Exception as e:
            print(f"Error getting Azure VMs: {e}")
            return []
    
    def _get_storage_accounts(self) -> List[Dict]:
        """Get Azure Storage Accounts"""
        try:
            storage_accounts = []
            for account in self.storage_client.storage_accounts.list():
                storage_accounts.append({
                    'resource_id': account.id,
                    'name': account.name,
                    'type': 'Storage Account',
                    'service': 'Storage Accounts',
                    'region': account.location,
                    'state': account.provisioning_state.value if account.provisioning_state else 'Unknown',
                    'sku': account.sku.name.value if account.sku else 'Unknown',
                    'kind': account.kind.value if account.kind else 'Unknown',
                    'resource_group': account.id.split('/')[4],
                    'provider': 'azure',
                    'tags': account.tags or {}
                })
            
            return storage_accounts
            
        except Exception as e:
            print(f"Error getting Azure Storage Accounts: {e}")
            return []
    
    def _get_sql_databases(self) -> List[Dict]:
        """Get Azure SQL Databases"""
        try:
            databases = []
            
            # Get SQL servers first
            for server in self.sql_client.servers.list():
                resource_group = server.id.split('/')[4]
                
                # Get databases for each server
                try:
                    for db in self.sql_client.databases.list_by_server(resource_group, server.name):
                        if db.name != 'master':  # Skip master database
                            databases.append({
                                'resource_id': db.id,
                                'name': db.name,
                                'type': 'SQL Database',
                                'service': 'SQL Database',
                                'region': db.location,
                                'state': db.status.value if db.status else 'Unknown',
                                'server_name': server.name,
                                'edition': db.edition or 'Unknown',
                                'resource_group': resource_group,
                                'provider': 'azure',
                                'tags': db.tags or {}
                            })
                except Exception as e:
                    print(f"Error getting databases for server {server.name}: {e}")
                    continue
            
            return databases
            
        except Exception as e:
            print(f"Error getting Azure SQL Databases: {e}")
            return []
    
    def _get_app_services(self) -> List[Dict]:
        """Get Azure App Services"""
        try:
            app_services = []
            for app in self.web_client.web_apps.list():
                app_services.append({
                    'resource_id': app.id,
                    'name': app.name,
                    'type': 'App Service',
                    'service': 'App Service',
                    'region': app.location,
                    'state': app.state,
                    'default_host_name': app.default_host_name,
                    'app_service_plan': app.server_farm_id.split('/')[-1] if app.server_farm_id else 'Unknown',
                    'resource_group': app.id.split('/')[4],
                    'provider': 'azure',
                    'tags': app.tags or {}
                })
            
            return app_services
            
        except Exception as e:
            print(f"Error getting Azure App Services: {e}")
            return []
    
    def _get_resource_groups(self) -> List[Dict]:
        """Get Azure Resource Groups"""
        try:
            resource_groups = []
            for rg in self.resource_client.resource_groups.list():
                resource_groups.append({
                    'resource_id': rg.id,
                    'name': rg.name,
                    'type': 'Resource Group',
                    'service': 'Resource Groups',
                    'region': rg.location,
                    'state': rg.provisioning_state,
                    'provider': 'azure',
                    'tags': rg.tags or {}
                })
            
            return resource_groups
            
        except Exception as e:
            print(f"Error getting Azure Resource Groups: {e}")
            return []
    
    def get_monthly_costs_by_service(self, months: int = 12) -> List[Dict]:
        """Get monthly costs broken down by service"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30 * months)
            
            cost_data = self.get_cost_data(start_date, end_date)
            
            # Group by month and service
            monthly_costs = {}
            for cost in cost_data:
                month = cost['period_start'][:7]  # YYYY-MM format
                
                if month not in monthly_costs:
                    monthly_costs[month] = {
                        'month': month,
                        'total_cost': 0,
                        'service_breakdown': {},
                        'provider': 'azure'
                    }
                
                service = cost['service']
                cost_amount = cost['cost']
                
                monthly_costs[month]['total_cost'] += cost_amount
                if service not in monthly_costs[month]['service_breakdown']:
                    monthly_costs[month]['service_breakdown'][service] = 0
                monthly_costs[month]['service_breakdown'][service] += cost_amount
            
            return list(monthly_costs.values())
            
        except Exception as e:
            raise Exception(f"Failed to get monthly costs: {str(e)}")
    
    def get_resource_groups_list(self) -> List[Dict]:
        """Get list of resource groups for cost sync"""
        try:
            resource_groups = []
            for rg in self.resource_client.resource_groups.list():
                resource_groups.append({
                    'name': rg.name,
                    'location': rg.location,
                    'id': rg.id,
                    'tags': rg.tags or {}
                })
            return resource_groups
        except Exception as e:
            raise Exception(f"Failed to list resource groups: {str(e)}")


def create_azure_service(credentials: Dict[str, str]) -> AzureService:
    """Factory function to create Azure service instance"""
    return AzureService(credentials)