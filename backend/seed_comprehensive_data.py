"""
Comprehensive seed data script for Multi-Cloud Operations Dashboard
Creates realistic sample data for all components
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import (
    Project,
    ResourceGroup,
    ProjectResourceGroup,
    MonthlyCost,
    CostData,
    ProjectCostSummary,
    AIQConsumption,
    CloudConnection
)
from app.models.project import ProjectStatus
from app.models.cloud_connection import CloudProvider, ConnectionStatus
import random
import json
import math

def create_sample_data():
    db = SessionLocal()
    
    try:
        print("🚀 Creating comprehensive sample data...")
        
        # Clear existing data
        print("Clearing existing data...")
        db.query(AIQConsumption).delete()
        db.query(ProjectCostSummary).delete()
        db.query(CostData).delete()
        db.query(MonthlyCost).delete()
        db.query(ProjectResourceGroup).delete()
        db.query(ResourceGroup).delete()
        db.query(CloudConnection).delete()
        db.query(Project).delete()
        db.commit()
        
        # Create Projects
        print("Creating projects...")
        projects_data = [
            {
                "project_name": "E-Commerce Platform Migration",
                "project_type": "External",
                "member_firm": "Deloitte US",
                "deployed_region": "US",
                "description": "Migration of legacy e-commerce platform to cloud-native architecture",
                "engagement_code": "ENG-2024-001",
                "engagement_partner": "Sarah Johnson",
                "opportunity_code": "OPP-EC-2024",
                "engagement_manager": "Michael Chen",
                "project_startdate": date(2024, 1, 15),
                "project_enddate": date(2024, 8, 30),
                "status": ProjectStatus.ACTIVE,
                "progress_percentage": 65,
                "budget_allocated": 250000000,  # $2.5M in cents
                "budget_spent": 162500000,      # $1.625M in cents
                "priority": "high",
                "health_status": "green",
                "business_justification": "Modernize legacy systems to improve scalability and reduce operational costs",
                "business_unit": "Digital Commerce",
                "department": "Technology",
                "cost_center": "CC-2024-001",
                "project_sponsor": "Jennifer Williams",
                "project_manager": "David Rodriguez",
                "technical_lead": "Emily Zhang",
                "budget_source": "Client Funded",
                "cloud_providers": "AWS,Azure",
                "compliance_requirements": "SOX,PCI-DSS",
                "security_classification": "Confidential",
                "client_name": "RetailCorp Inc.",
                "contract_type": "Fixed Price",
                "risk_assessment": "Medium"
            },
            {
                "project_name": "Financial Data Analytics Platform",
                "project_type": "Internal",
                "member_firm": "Deloitte UK",
                "deployed_region": "EU",
                "description": "Advanced analytics platform for financial data processing and reporting",
                "engagement_code": "ENG-2024-002",
                "engagement_partner": "James Thompson",
                "opportunity_code": "OPP-FIN-2024",
                "engagement_manager": "Lisa Anderson",
                "project_startdate": date(2024, 2, 1),
                "project_enddate": date(2024, 10, 15),
                "status": ProjectStatus.ACTIVE,
                "progress_percentage": 45,
                "budget_allocated": 180000000,  # $1.8M in cents
                "budget_spent": 81000000,       # $810K in cents
                "priority": "high",
                "health_status": "yellow",
                "business_justification": "Enhance financial reporting capabilities and regulatory compliance",
                "business_unit": "Financial Services",
                "department": "Analytics",
                "cost_center": "CC-2024-002",
                "project_sponsor": "Robert Taylor",
                "project_manager": "Amanda Foster",
                "technical_lead": "Kevin Liu",
                "budget_source": "Internal Investment",
                "cloud_providers": "Azure,GCP",
                "compliance_requirements": "GDPR,SOX",
                "security_classification": "Restricted",
                "client_name": "Internal",
                "contract_type": "Internal Project",
                "risk_assessment": "High"
            },
            {
                "project_name": "Supply Chain Optimization",
                "project_type": "External",
                "member_firm": "Deloitte APAC",
                "deployed_region": "APAC",
                "description": "AI-powered supply chain optimization and predictive analytics",
                "engagement_code": "ENG-2024-003",
                "engagement_partner": "Hiroshi Tanaka",
                "opportunity_code": "OPP-SC-2024",
                "engagement_manager": "Priya Sharma",
                "project_startdate": date(2024, 3, 1),
                "project_enddate": date(2024, 12, 31),
                "status": ProjectStatus.ACTIVE,
                "progress_percentage": 30,
                "budget_allocated": 320000000,  # $3.2M in cents
                "budget_spent": 96000000,       # $960K in cents
                "priority": "critical",
                "health_status": "green",
                "business_justification": "Optimize supply chain efficiency and reduce costs by 15%",
                "business_unit": "Supply Chain",
                "department": "Operations",
                "cost_center": "CC-2024-003",
                "project_sponsor": "Maria Santos",
                "project_manager": "Alex Kim",
                "technical_lead": "Raj Patel",
                "budget_source": "Client Funded",
                "cloud_providers": "AWS,GCP",
                "compliance_requirements": "ISO27001",
                "security_classification": "Internal",
                "client_name": "GlobalManufacturing Ltd.",
                "contract_type": "Time & Materials",
                "risk_assessment": "Medium"
            },
            {
                "project_name": "Healthcare Data Platform",
                "project_type": "External",
                "member_firm": "Deloitte US",
                "deployed_region": "US",
                "description": "HIPAA-compliant healthcare data platform for patient analytics",
                "engagement_code": "ENG-2024-004",
                "engagement_partner": "Dr. Patricia Moore",
                "opportunity_code": "OPP-HC-2024",
                "engagement_manager": "Thomas Wilson",
                "project_startdate": date(2024, 1, 1),
                "project_enddate": date(2024, 9, 30),
                "status": ProjectStatus.COMPLETED,
                "progress_percentage": 100,
                "budget_allocated": 150000000,  # $1.5M in cents
                "budget_spent": 145000000,      # $1.45M in cents
                "priority": "high",
                "health_status": "green",
                "business_justification": "Improve patient outcomes through advanced data analytics",
                "business_unit": "Healthcare",
                "department": "Technology",
                "cost_center": "CC-2024-004",
                "project_sponsor": "Dr. Susan Clark",
                "project_manager": "Brian Martinez",
                "technical_lead": "Rachel Green",
                "budget_source": "Client Funded",
                "cloud_providers": "Azure",
                "compliance_requirements": "HIPAA,SOC2",
                "security_classification": "Highly Confidential",
                "client_name": "MedCenter Health System",
                "contract_type": "Fixed Price",
                "risk_assessment": "High"
            },
            {
                "project_name": "Digital Transformation Initiative",
                "project_type": "Internal",
                "member_firm": "Deloitte Global",
                "deployed_region": "US",
                "description": "Internal digital transformation and process automation",
                "engagement_code": "ENG-2024-005",
                "engagement_partner": "Mark Davis",
                "opportunity_code": "OPP-DT-2024",
                "engagement_manager": "Catherine Lee",
                "project_startdate": date(2024, 4, 1),
                "project_enddate": date(2025, 3, 31),
                "status": ProjectStatus.PLANNING,
                "progress_percentage": 15,
                "budget_allocated": 500000000,  # $5M in cents
                "budget_spent": 75000000,       # $750K in cents
                "priority": "critical",
                "health_status": "yellow",
                "business_justification": "Modernize internal processes and improve operational efficiency",
                "business_unit": "Operations",
                "department": "Digital Innovation",
                "cost_center": "CC-2024-005",
                "project_sponsor": "Executive Committee",
                "project_manager": "Daniel Brown",
                "technical_lead": "Sophie Turner",
                "budget_source": "Internal Investment",
                "cloud_providers": "AWS,Azure,GCP",
                "compliance_requirements": "SOX,ISO27001",
                "security_classification": "Internal",
                "client_name": "Internal",
                "contract_type": "Internal Project",
                "risk_assessment": "Medium"
            }
        ]
        
        projects = []
        for project_data in projects_data:
            project = Project(**project_data)
            db.add(project)
            projects.append(project)
        
        db.commit()
        print(f"✅ Created {len(projects)} projects")
        
        # Create Resource Groups
        print("Creating resource groups...")
        resource_groups_data = [
            # E-Commerce Platform Migration
            {"resource_group_name": "ecom-frontend-prod", "project_id": projects[0].id, "status": "active"},
            {"resource_group_name": "ecom-backend-prod", "project_id": projects[0].id, "status": "active"},
            {"resource_group_name": "ecom-database-prod", "project_id": projects[0].id, "status": "active"},
            {"resource_group_name": "ecom-cdn-global", "project_id": projects[0].id, "status": "active"},
            
            # Financial Data Analytics Platform
            {"resource_group_name": "findata-analytics-prod", "project_id": projects[1].id, "status": "active"},
            {"resource_group_name": "findata-storage-prod", "project_id": projects[1].id, "status": "active"},
            {"resource_group_name": "findata-compute-prod", "project_id": projects[1].id, "status": "active"},
            
            # Supply Chain Optimization
            {"resource_group_name": "supply-ml-prod", "project_id": projects[2].id, "status": "active"},
            {"resource_group_name": "supply-api-prod", "project_id": projects[2].id, "status": "active"},
            {"resource_group_name": "supply-data-prod", "project_id": projects[2].id, "status": "active"},
            
            # Healthcare Data Platform
            {"resource_group_name": "health-secure-prod", "project_id": projects[3].id, "status": "completed"},
            {"resource_group_name": "health-analytics-prod", "project_id": projects[3].id, "status": "completed"},
            
            # Digital Transformation Initiative
            {"resource_group_name": "digital-core-prod", "project_id": projects[4].id, "status": "planning"},
            {"resource_group_name": "digital-integration-prod", "project_id": projects[4].id, "status": "planning"},
            {"resource_group_name": "digital-monitoring-prod", "project_id": projects[4].id, "status": "planning"}
        ]
        
        resource_groups = []
        for rg_data in resource_groups_data:
            rg = ResourceGroup(**rg_data)
            db.add(rg)
            resource_groups.append(rg)
        
        db.commit()
        print(f"✅ Created {len(resource_groups)} resource groups")
        
        # Create Project-ResourceGroup relationships
        print("Creating project-resource group relationships...")
        for rg in resource_groups:
            project_rg = ProjectResourceGroup(
                project_id=rg.project_id,
                resource_group_id=rg.id
            )
            db.add(project_rg)
        
        db.commit()
        print("✅ Created project-resource group relationships")
        
        # Create Monthly Costs (last 12 months)
        print("Creating monthly cost data...")
        monthly_costs = []
        
        # Generate costs for the last 12 months
        for month_offset in range(12):
            cost_date = date.today().replace(day=1) - timedelta(days=30 * month_offset)
            
            for rg in resource_groups:
                # Base cost varies by project and resource group
                base_cost = random.uniform(5000, 25000)
                
                # Add some seasonal variation
                seasonal_factor = 1 + 0.2 * math.sin(month_offset * 3.14159 / 6)
                
                # Add project-specific multipliers
                if rg.project_id == 1:  # E-commerce - higher costs
                    base_cost *= 1.5
                elif rg.project_id == 5:  # Digital transformation - very high costs
                    base_cost *= 2.0
                
                final_cost = base_cost * seasonal_factor
                
                monthly_cost = MonthlyCost(
                    project_id=rg.project_id,
                    resource_group_id=rg.id,
                    month=cost_date,
                    cost=final_cost
                )
                db.add(monthly_cost)
                monthly_costs.append(monthly_cost)
        
        db.commit()
        print(f"✅ Created {len(monthly_costs)} monthly cost records")
        
        # Create Cost Data (detailed breakdown)
        print("Creating detailed cost data...")
        cost_categories = [
            "Compute", "Storage", "Network", "Database", "Security", 
            "Monitoring", "Backup", "CDN", "Load Balancer", "API Gateway"
        ]
        
        cost_data_records = []
        for monthly_cost in monthly_costs:
            # Create 3-5 cost breakdown items per monthly cost
            num_items = random.randint(3, 5)
            selected_categories = random.sample(cost_categories, num_items)
            
            total_cost = float(monthly_cost.cost)
            remaining_cost = total_cost
            
            for i, category in enumerate(selected_categories):
                if i == len(selected_categories) - 1:
                    # Last item gets remaining cost
                    item_cost = remaining_cost
                else:
                    # Random portion of remaining cost
                    item_cost = remaining_cost * random.uniform(0.1, 0.4)
                    remaining_cost -= item_cost
                
                cost_data = CostData(
                    key=f"{monthly_cost.resource_group_id}_{category}_{monthly_cost.month}",
                    period=monthly_cost.month,
                    month_year=monthly_cost.month.strftime("%Y-%m"),
                    resource_group_id=monthly_cost.resource_group_id,
                    cost=item_cost
                )
                db.add(cost_data)
                cost_data_records.append(cost_data)
        
        db.commit()
        print(f"✅ Created {len(cost_data_records)} detailed cost records")
        
        # Create Project Cost Summaries
        print("Creating project cost summaries...")
        for project in projects:
            # Get resource groups for this project
            project_resource_groups = [rg for rg in resource_groups if rg.project_id == project.id]
            
            for rg in project_resource_groups:
                # Calculate total costs for this project-resource group combination
                rg_monthly_costs = [mc for mc in monthly_costs if mc.project_id == project.id and mc.resource_group_id == rg.id]
                total_cost = sum(float(mc.cost) for mc in rg_monthly_costs)
                
                cost_summary = ProjectCostSummary(
                    project_id=project.id,
                    resource_group_id=rg.id,
                    total_cost_to_date=total_cost,
                    updated_date=date.today(),
                    costs_passed_back_to_date=total_cost * 0.8,  # 80% passed back
                    gpt_costs_to_date=total_cost * 0.1,  # 10% GPT costs
                    gpt_costs_passed_back_to_date=total_cost * 0.08,  # 8% GPT passed back
                    remarks=f"Cost summary for {project.project_name} - {rg.resource_group_name}"
                )
                db.add(cost_summary)
        
        db.commit()
        print("✅ Created project cost summaries")
        
        # Create AIQ Consumption data
        print("Creating AIQ consumption data...")
        aiq_services = [
            "GPT-4", "Claude", "Gemini", "Code Copilot", "Data Analysis AI", 
            "Document AI", "Translation AI", "Vision AI", "Speech AI"
        ]
        
        for project in projects:
            # Each project uses 2-4 AI services
            num_services = random.randint(2, 4)
            selected_services = random.sample(aiq_services, num_services)
            
            for service in selected_services:
                # Generate consumption for last 6 months
                for month_offset in range(6):
                    consumption_date = date.today().replace(day=1) - timedelta(days=30 * month_offset)
                    
                    aiq_consumption = AIQConsumption(
                        project_id=project.id,
                        aiq_assumption_name=service,
                        consumption_amount=random.randint(10000, 500000),
                        consumption_day=consumption_date
                    )
                    db.add(aiq_consumption)
        
        db.commit()
        print("✅ Created AIQ consumption data")
        
        # Create Cloud Connections
        print("Creating cloud connections...")
        cloud_connections = [
            {
                "name": "Production AWS Account",
                "provider": CloudProvider.AWS,
                "credentials": json.dumps({
                    "access_key_id": "AKIA***EXAMPLE",
                    "secret_access_key": "***MASKED***",
                    "region": "us-east-1",
                    "account_id": "123456789012"
                }),
                "status": ConnectionStatus.ACTIVE,
                "description": "Main production AWS account for US operations",
                "regions": json.dumps(["us-east-1", "us-west-2", "eu-west-1"]),
                "last_sync": datetime.utcnow() - timedelta(hours=2),
                "resource_count": 156,
                "monthly_cost": 2850000  # $28,500 in cents
            },
            {
                "name": "Azure Europe Environment",
                "provider": CloudProvider.AZURE,
                "credentials": json.dumps({
                    "subscription_id": "12345678-1234-1234-1234-123456789012",
                    "client_id": "87654321-4321-4321-4321-210987654321",
                    "client_secret": "***MASKED***",
                    "tenant_id": "11111111-2222-3333-4444-555555555555"
                }),
                "status": ConnectionStatus.ACTIVE,
                "description": "Azure subscription for European operations",
                "regions": json.dumps(["West Europe", "North Europe", "UK South"]),
                "last_sync": datetime.utcnow() - timedelta(hours=1),
                "resource_count": 89,
                "monthly_cost": 1920000  # $19,200 in cents
            },
            {
                "name": "GCP Analytics Platform",
                "provider": CloudProvider.GCP,
                "credentials": json.dumps({
                    "project_id": "deloitte-analytics-prod",
                    "service_account_key": "***MASKED***",
                    "region": "us-central1"
                }),
                "status": ConnectionStatus.ACTIVE,
                "description": "Google Cloud Platform for analytics workloads",
                "regions": json.dumps(["us-central1", "us-east1", "europe-west1"]),
                "last_sync": datetime.utcnow() - timedelta(minutes=30),
                "resource_count": 67,
                "monthly_cost": 1340000  # $13,400 in cents
            }
        ]
        
        for conn_data in cloud_connections:
            cloud_conn = CloudConnection(**conn_data)
            db.add(cloud_conn)
        
        db.commit()
        print("✅ Created cloud connections")
        
        print("\n🎉 Sample data creation completed successfully!")
        print("\n📊 Summary:")
        print(f"   • {len(projects)} Projects created")
        print(f"   • {len(resource_groups)} Resource Groups created")
        print(f"   • {len(monthly_costs)} Monthly Cost records created")
        print(f"   • {len(cost_data_records)} Detailed Cost records created")
        print(f"   • 3 Cloud Connections created")
        print(f"   • AIQ Consumption data for 6 months")
        print(f"   • Project Cost Summaries with trends")
        
        print("\n🚀 You can now:")
        print("   • View the dashboard with real data and charts")
        print("   • Test all project management features")
        print("   • Explore cost analytics and trends")
        print("   • See cloud provider integrations")
        print("   • Test the complete application workflow")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()