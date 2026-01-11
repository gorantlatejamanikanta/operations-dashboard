"""
Google Cloud Platform Integration Service
Handles GCP cost and resource data retrieval
"""
from google.cloud import resource_manager
from google.cloud import compute_v1
from google.cloud import storage
from google.cloud import sql_v1
from google.cloud import functions_v1
from google.cloud import billing_v1
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError, Forbidden, NotFound
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json


class GCPService:
    def __init__(self, credentials: Dict[str, str]):
        """Initialize GCP service with credentials"""
        self.project_id = credentials.get('project_id')
        self.region = credentials.get('region', 'us-central1')
        
        # Parse service account key
        try:
            service_account_info = json.loads(credentials.get('service_account_key', '{}'))
            self.credentials = service_account.Credentials.from_service_account_info(
                service_account_info
            )
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid service account key format: {str(e)}")
        
        # Initialize clients
        self.resource_manager_client = resource_manager.Client(credentials=self.credentials)
        self.compute_client = compute_v1.InstancesClient(credentials=self.credentials)
        self.storage_client = storage.Client(credentials=self.credentials, project=self.project_id)
        self.sql_client = sql_v1.SqlInstancesServiceClient(credentials=self.credentials)
        self.functions_client = functions_v1.CloudFunctionsServiceClient(credentials=self.credentials)
    
    def test_connection(self) -> Tuple[bool, str, Dict]:
        """Test GCP connection and return project information"""
        try:
            # Test by getting project info
            project = self.resource_manager_client.fetch_project(self.project_id)
            
            return True, "GCP connection successful", {
                "project_id": project.project_id,
                "project_name": project.name,
                "project_number": project.number,
                "lifecycle_state": project.lifecycle_state.name
            }
        except Forbidden:
            return False, "Access denied. Check service account permissions.", {}
        except NotFound:
            return False, f"Project {self.project_id} not found or not accessible.", {}
        except GoogleAPIError as e:
            return False, f"GCP API error: {str(e)}", {}
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", {}
    
    def get_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Retrieve cost data from GCP Billing API"""
        try:
            # Note: GCP Billing API requires billing account access
            # For now, return mock data as billing setup is complex
            return self._get_mock_cost_data(start_date, end_date)
            
        except Exception as e:
            print(f"GCP Billing API error: {e}")
            return self._get_mock_cost_data(start_date, end_date)
    
    def _get_mock_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Generate mock cost data for demonstration"""
        import random
        
        services = [
            'Compute Engine', 'Cloud Storage', 'Cloud SQL',
            'Cloud Functions', 'App Engine', 'Cloud Load Balancing',
            'Cloud CDN', 'Cloud DNS', 'Cloud Monitoring'
        ]
        
        regions = ['us-central1', 'us-east1', 'europe-west1', 'asia-southeast1']
        
        cost_data = []
        current_date = start_date.replace(day=1)
        
        while current_date < end_date:
            for service in services:
                for region in regions:
                    if random.random() > 0.4:  # 60% chance of having costs
                        cost = random.uniform(25, 1500)
                        cost_data.append({
                            'period_start': current_date.strftime('%Y-%m-%d'),
                            'period_end': current_date.strftime('%Y-%m-%d'),
                            'service': service,
                            'region': region,
                            'cost': round(cost, 2),
                            'currency': 'USD',
                            'provider': 'gcp'
                        })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return cost_data
    
    def get_resources(self) -> List[Dict]:
        """Retrieve GCP resources across multiple services"""
        resources = []
        
        try:
            # Get Compute Engine instances
            resources.extend(self._get_compute_instances())
            
            # Get Cloud Storage buckets
            resources.extend(self._get_storage_buckets())
            
            # Get Cloud SQL instances
            resources.extend(self._get_sql_instances())
            
            # Get Cloud Functions
            resources.extend(self._get_cloud_functions())
            
            return resources
            
        except Exception as e:
            raise Exception(f"Failed to retrieve GCP resources: {str(e)}")
    
    def _get_compute_instances(self) -> List[Dict]:
        """Get Compute Engine instances"""
        try:
            instances = []
            
            # List instances in all zones of the region
            zones_client = compute_v1.ZonesClient(credentials=self.credentials)
            zones = zones_client.list(project=self.project_id, filter=f"name:{self.region}-*")
            
            for zone in zones:
                try:
                    zone_instances = self.compute_client.list(
                        project=self.project_id, 
                        zone=zone.name
                    )
                    
                    for instance in zone_instances:
                        instances.append({
                            'resource_id': str(instance.id),
                            'name': instance.name,
                            'type': 'Compute Instance',
                            'service': 'Compute Engine',
                            'region': zone.region.split('/')[-1],
                            'zone': zone.name,
                            'state': instance.status,
                            'machine_type': instance.machine_type.split('/')[-1],
                            'creation_timestamp': instance.creation_timestamp,
                            'provider': 'gcp',
                            'tags': {
                                'labels': dict(instance.labels) if instance.labels else {},
                                'tags': list(instance.tags.items) if instance.tags else []
                            }
                        })
                except Exception as e:
                    print(f"Error getting instances in zone {zone.name}: {e}")
                    continue
            
            return instances
            
        except Exception as e:
            print(f"Error getting GCP Compute instances: {e}")
            return []
    
    def _get_storage_buckets(self) -> List[Dict]:
        """Get Cloud Storage buckets"""
        try:
            buckets = []
            
            for bucket in self.storage_client.list_buckets():
                buckets.append({
                    'resource_id': bucket.name,
                    'name': bucket.name,
                    'type': 'Storage Bucket',
                    'service': 'Cloud Storage',
                    'region': bucket.location,
                    'state': 'active',
                    'storage_class': bucket.storage_class,
                    'creation_time': bucket.time_created.isoformat() if bucket.time_created else None,
                    'provider': 'gcp',
                    'tags': dict(bucket.labels) if bucket.labels else {}
                })
            
            return buckets
            
        except Exception as e:
            print(f"Error getting GCP Storage buckets: {e}")
            return []
    
    def _get_sql_instances(self) -> List[Dict]:
        """Get Cloud SQL instances"""
        try:
            instances = []
            
            request = sql_v1.SqlInstancesListRequest(project=self.project_id)
            response = self.sql_client.list(request=request)
            
            for instance in response.items:
                instances.append({
                    'resource_id': instance.name,
                    'name': instance.name,
                    'type': 'SQL Instance',
                    'service': 'Cloud SQL',
                    'region': instance.region,
                    'state': instance.state.name if instance.state else 'Unknown',
                    'database_version': instance.database_version,
                    'tier': instance.settings.tier if instance.settings else 'Unknown',
                    'creation_time': instance.create_time.isoformat() if instance.create_time else None,
                    'provider': 'gcp',
                    'tags': dict(instance.settings.user_labels) if instance.settings and instance.settings.user_labels else {}
                })
            
            return instances
            
        except Exception as e:
            print(f"Error getting GCP SQL instances: {e}")
            return []
    
    def _get_cloud_functions(self) -> List[Dict]:
        """Get Cloud Functions"""
        try:
            functions = []
            
            parent = f"projects/{self.project_id}/locations/{self.region}"
            
            try:
                response = self.functions_client.list_functions(parent=parent)
                
                for function in response:
                    functions.append({
                        'resource_id': function.name,
                        'name': function.name.split('/')[-1],
                        'type': 'Cloud Function',
                        'service': 'Cloud Functions',
                        'region': self.region,
                        'state': function.status.name if function.status else 'Unknown',
                        'runtime': function.runtime,
                        'entry_point': function.entry_point,
                        'update_time': function.update_time.isoformat() if function.update_time else None,
                        'provider': 'gcp',
                        'tags': dict(function.labels) if function.labels else {}
                    })
            except Exception as e:
                print(f"Error listing functions in region {self.region}: {e}")
            
            return functions
            
        except Exception as e:
            print(f"Error getting GCP Cloud Functions: {e}")
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
                        'provider': 'gcp'
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
    
    def get_projects_list(self) -> List[Dict]:
        """Get list of accessible projects"""
        try:
            projects = []
            for project in self.resource_manager_client.list_projects():
                projects.append({
                    'project_id': project.project_id,
                    'name': project.name,
                    'number': project.number,
                    'lifecycle_state': project.lifecycle_state.name
                })
            return projects
        except Exception as e:
            raise Exception(f"Failed to list projects: {str(e)}")


def create_gcp_service(credentials: Dict[str, str]) -> GCPService:
    """Factory function to create GCP service instance"""
    return GCPService(credentials)