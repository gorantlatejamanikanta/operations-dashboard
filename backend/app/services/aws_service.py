"""
AWS Integration Service
Handles AWS cost and resource data retrieval
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from decimal import Decimal


class AWSService:
    def __init__(self, credentials: Dict[str, str]):
        """Initialize AWS service with credentials"""
        self.access_key_id = credentials.get('access_key_id')
        self.secret_access_key = credentials.get('secret_access_key')
        self.region = credentials.get('region', 'us-east-1')
        self.account_id = credentials.get('account_id')
        
        # Initialize clients
        self.session = boto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region
        )
    
    def test_connection(self) -> Tuple[bool, str, Dict]:
        """Test AWS connection and return account information"""
        try:
            sts_client = self.session.client('sts')
            identity = sts_client.get_caller_identity()
            
            return True, "AWS connection successful", {
                "account_id": identity.get('Account'),
                "user_id": identity.get('UserId'),
                "arn": identity.get('Arn'),
                "region": self.region
            }
        except NoCredentialsError:
            return False, "Invalid AWS credentials", {}
        except ClientError as e:
            return False, f"AWS connection failed: {e.response['Error']['Message']}", {}
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", {}
    
    def get_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Retrieve cost data from AWS Cost Explorer"""
        try:
            ce_client = self.session.client('ce', region_name='us-east-1')  # Cost Explorer is only in us-east-1
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost', 'UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ]
            )
            
            cost_data = []
            for result in response.get('ResultsByTime', []):
                period_start = result['TimePeriod']['Start']
                period_end = result['TimePeriod']['End']
                
                for group in result.get('Groups', []):
                    service = group['Keys'][0] if len(group['Keys']) > 0 else 'Unknown'
                    region = group['Keys'][1] if len(group['Keys']) > 1 else 'Unknown'
                    
                    blended_cost = float(group['Metrics']['BlendedCost']['Amount'])
                    unblended_cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    if blended_cost > 0:  # Only include services with actual costs
                        cost_data.append({
                            'period_start': period_start,
                            'period_end': period_end,
                            'service': service,
                            'region': region,
                            'blended_cost': blended_cost,
                            'unblended_cost': unblended_cost,
                            'currency': 'USD',
                            'provider': 'aws'
                        })
            
            return cost_data
            
        except ClientError as e:
            raise Exception(f"Failed to retrieve AWS cost data: {e.response['Error']['Message']}")
        except Exception as e:
            raise Exception(f"Unexpected error retrieving AWS costs: {str(e)}")
    
    def get_resources(self) -> List[Dict]:
        """Retrieve AWS resources across multiple services"""
        resources = []
        
        try:
            # Get EC2 instances
            resources.extend(self._get_ec2_instances())
            
            # Get S3 buckets
            resources.extend(self._get_s3_buckets())
            
            # Get RDS instances
            resources.extend(self._get_rds_instances())
            
            # Get Lambda functions
            resources.extend(self._get_lambda_functions())
            
            # Get ELB load balancers
            resources.extend(self._get_load_balancers())
            
            return resources
            
        except Exception as e:
            raise Exception(f"Failed to retrieve AWS resources: {str(e)}")
    
    def _get_ec2_instances(self) -> List[Dict]:
        """Get EC2 instances"""
        try:
            ec2_client = self.session.client('ec2')
            response = ec2_client.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    name = 'Unknown'
                    for tag in instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                    
                    instances.append({
                        'resource_id': instance['InstanceId'],
                        'name': name,
                        'type': 'EC2 Instance',
                        'service': 'Amazon Elastic Compute Cloud - Compute',
                        'region': instance['Placement']['AvailabilityZone'][:-1],
                        'state': instance['State']['Name'],
                        'instance_type': instance['InstanceType'],
                        'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else None,
                        'provider': 'aws',
                        'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    })
            
            return instances
            
        except ClientError as e:
            print(f"Error getting EC2 instances: {e}")
            return []
    
    def _get_s3_buckets(self) -> List[Dict]:
        """Get S3 buckets"""
        try:
            s3_client = self.session.client('s3')
            response = s3_client.list_buckets()
            
            buckets = []
            for bucket in response['Buckets']:
                # Get bucket region
                try:
                    location_response = s3_client.get_bucket_location(Bucket=bucket['Name'])
                    region = location_response['LocationConstraint'] or 'us-east-1'
                except:
                    region = 'us-east-1'
                
                buckets.append({
                    'resource_id': bucket['Name'],
                    'name': bucket['Name'],
                    'type': 'S3 Bucket',
                    'service': 'Amazon Simple Storage Service',
                    'region': region,
                    'state': 'active',
                    'creation_date': bucket['CreationDate'].isoformat(),
                    'provider': 'aws',
                    'tags': {}
                })
            
            return buckets
            
        except ClientError as e:
            print(f"Error getting S3 buckets: {e}")
            return []
    
    def _get_rds_instances(self) -> List[Dict]:
        """Get RDS instances"""
        try:
            rds_client = self.session.client('rds')
            response = rds_client.describe_db_instances()
            
            instances = []
            for db_instance in response['DBInstances']:
                instances.append({
                    'resource_id': db_instance['DBInstanceIdentifier'],
                    'name': db_instance['DBInstanceIdentifier'],
                    'type': 'RDS Instance',
                    'service': 'Amazon Relational Database Service',
                    'region': db_instance['AvailabilityZone'][:-1] if db_instance.get('AvailabilityZone') else self.region,
                    'state': db_instance['DBInstanceStatus'],
                    'instance_class': db_instance['DBInstanceClass'],
                    'engine': db_instance['Engine'],
                    'creation_time': db_instance.get('InstanceCreateTime', '').isoformat() if db_instance.get('InstanceCreateTime') else None,
                    'provider': 'aws',
                    'tags': {}
                })
            
            return instances
            
        except ClientError as e:
            print(f"Error getting RDS instances: {e}")
            return []
    
    def _get_lambda_functions(self) -> List[Dict]:
        """Get Lambda functions"""
        try:
            lambda_client = self.session.client('lambda')
            response = lambda_client.list_functions()
            
            functions = []
            for function in response['Functions']:
                functions.append({
                    'resource_id': function['FunctionArn'],
                    'name': function['FunctionName'],
                    'type': 'Lambda Function',
                    'service': 'AWS Lambda',
                    'region': self.region,
                    'state': function['State'],
                    'runtime': function['Runtime'],
                    'last_modified': function['LastModified'],
                    'provider': 'aws',
                    'tags': {}
                })
            
            return functions
            
        except ClientError as e:
            print(f"Error getting Lambda functions: {e}")
            return []
    
    def _get_load_balancers(self) -> List[Dict]:
        """Get ELB load balancers"""
        try:
            elb_client = self.session.client('elbv2')
            response = elb_client.describe_load_balancers()
            
            load_balancers = []
            for lb in response['LoadBalancers']:
                load_balancers.append({
                    'resource_id': lb['LoadBalancerArn'],
                    'name': lb['LoadBalancerName'],
                    'type': 'Load Balancer',
                    'service': 'Elastic Load Balancing',
                    'region': self.region,
                    'state': lb['State']['Code'],
                    'scheme': lb['Scheme'],
                    'lb_type': lb['Type'],
                    'creation_time': lb.get('CreatedTime', '').isoformat() if lb.get('CreatedTime') else None,
                    'provider': 'aws',
                    'tags': {}
                })
            
            return load_balancers
            
        except ClientError as e:
            print(f"Error getting load balancers: {e}")
            return []
    
    def get_monthly_costs_by_service(self, months: int = 12) -> List[Dict]:
        """Get monthly costs broken down by service"""
        try:
            end_date = datetime.now().replace(day=1)
            start_date = end_date - timedelta(days=30 * months)
            
            ce_client = self.session.client('ce', region_name='us-east-1')
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            
            monthly_costs = []
            for result in response.get('ResultsByTime', []):
                period_start = result['TimePeriod']['Start']
                total_cost = 0
                
                service_costs = {}
                for group in result.get('Groups', []):
                    service = group['Keys'][0] if group['Keys'] else 'Other'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    service_costs[service] = cost
                    total_cost += cost
                
                monthly_costs.append({
                    'month': period_start,
                    'total_cost': total_cost,
                    'service_breakdown': service_costs,
                    'provider': 'aws'
                })
            
            return monthly_costs
            
        except Exception as e:
            raise Exception(f"Failed to get monthly costs: {str(e)}")
    
    def get_cost_forecast(self, days: int = 30) -> Dict:
        """Get cost forecast for the next period"""
        try:
            ce_client = self.session.client('ce', region_name='us-east-1')
            
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            
            response = ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Metric='BLENDED_COST',
                Granularity='MONTHLY'
            )
            
            forecast_data = []
            for result in response.get('ForecastResultsByTime', []):
                forecast_data.append({
                    'period_start': result['TimePeriod']['Start'],
                    'period_end': result['TimePeriod']['End'],
                    'mean_value': float(result['MeanValue']),
                    'prediction_interval_lower': float(result['PredictionIntervalLowerBound']),
                    'prediction_interval_upper': float(result['PredictionIntervalUpperBound'])
                })
            
            return {
                'forecast_period_days': days,
                'forecast_data': forecast_data,
                'provider': 'aws'
            }
            
        except Exception as e:
            raise Exception(f"Failed to get cost forecast: {str(e)}")


def create_aws_service(credentials: Dict[str, str]) -> AWSService:
    """Factory function to create AWS service instance"""
    return AWSService(credentials)