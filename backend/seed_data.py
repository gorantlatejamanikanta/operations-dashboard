"""Script to seed the database with sample data"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import (
    Project,
    ResourceGroup,
    MonthlyCost,
    ProjectCostSummary,
    AIQConsumption,
)
from datetime import date, timedelta
from decimal import Decimal

def seed_data():
    db: Session = SessionLocal()
    try:
        # Create sample projects
        project1 = Project(
            project_name="Cloud Migration Initiative",
            project_type="Internal",
            member_firm="US Office",
            deployed_region="US",
            is_active=True,
            description="Migrating legacy systems to cloud",
            engagement_code="ENG-001",
            engagement_partner="John Smith",
            opportunity_code="OPP-001",
            engagement_manager="Jane Doe",
            project_startdate=date(2024, 1, 1),
            project_enddate=date(2024, 12, 31)
        )
        
        project2 = Project(
            project_name="Client Analytics Platform",
            project_type="Client Demo",
            member_firm="EU Office",
            deployed_region="EU",
            is_active=True,
            description="Data analytics platform for client",
            engagement_code="ENG-002",
            engagement_partner="Mike Johnson",
            opportunity_code="OPP-002",
            engagement_manager="Sarah Wilson",
            project_startdate=date(2024, 3, 1),
            project_enddate=date(2025, 2, 28)
        )
        
        project3 = Project(
            project_name="APAC Digital Transformation",
            project_type="External",
            member_firm="APAC Office",
            deployed_region="APAC",
            is_active=True,
            description="Digital transformation project",
            engagement_code="ENG-003",
            engagement_partner="David Lee",
            opportunity_code="OPP-003",
            engagement_manager="Lisa Chen",
            project_startdate=date(2024, 6, 1),
            project_enddate=date(2025, 5, 31)
        )
        
        db.add_all([project1, project2, project3])
        db.commit()
        db.refresh(project1)
        db.refresh(project2)
        db.refresh(project3)
        
        # Create resource groups
        rg1 = ResourceGroup(
            resource_group_name="rg-migration-prod",
            project_id=project1.id,
            status="Active"
        )
        rg2 = ResourceGroup(
            resource_group_name="rg-migration-dev",
            project_id=project1.id,
            status="Active"
        )
        rg3 = ResourceGroup(
            resource_group_name="rg-analytics-prod",
            project_id=project2.id,
            status="Active"
        )
        rg4 = ResourceGroup(
            resource_group_name="rg-digital-prod",
            project_id=project3.id,
            status="Active"
        )
        
        db.add_all([rg1, rg2, rg3, rg4])
        db.commit()
        db.refresh(rg1)
        db.refresh(rg2)
        db.refresh(rg3)
        db.refresh(rg4)
        
        # Create monthly costs
        base_date = date(2024, 1, 1)
        monthly_costs = []
        for month_offset in range(12):
            month = base_date + timedelta(days=30 * month_offset)
            monthly_costs.extend([
                MonthlyCost(
                    project_id=project1.id,
                    resource_group_id=rg1.id,
                    month=month,
                    cost=Decimal("5000.00") + Decimal(month_offset * 100)
                ),
                MonthlyCost(
                    project_id=project1.id,
                    resource_group_id=rg2.id,
                    month=month,
                    cost=Decimal("2000.00") + Decimal(month_offset * 50)
                ),
                MonthlyCost(
                    project_id=project2.id,
                    resource_group_id=rg3.id,
                    month=month,
                    cost=Decimal("8000.00") + Decimal(month_offset * 150)
                ),
                MonthlyCost(
                    project_id=project3.id,
                    resource_group_id=rg4.id,
                    month=month,
                    cost=Decimal("6000.00") + Decimal(month_offset * 200)
                ),
            ])
        
        db.add_all(monthly_costs)
        
        # Create cost summaries
        summaries = [
            ProjectCostSummary(
                project_id=project1.id,
                resource_group_id=rg1.id,
                total_cost_to_date=Decimal("72000.00"),
                updated_date=date.today(),
                costs_passed_back_to_date=Decimal("65000.00"),
                gpt_costs_to_date=Decimal("5000.00"),
                gpt_costs_passed_back_to_date=Decimal("4500.00"),
                remarks="On track"
            ),
            ProjectCostSummary(
                project_id=project1.id,
                resource_group_id=rg2.id,
                total_cost_to_date=Decimal("27000.00"),
                updated_date=date.today(),
                costs_passed_back_to_date=Decimal("25000.00"),
                gpt_costs_to_date=Decimal("2000.00"),
                gpt_costs_passed_back_to_date=Decimal("1800.00"),
                remarks="Under budget"
            ),
            ProjectCostSummary(
                project_id=project2.id,
                resource_group_id=rg3.id,
                total_cost_to_date=Decimal("114000.00"),
                updated_date=date.today(),
                costs_passed_back_to_date=Decimal("100000.00"),
                gpt_costs_to_date=Decimal("8000.00"),
                gpt_costs_passed_back_to_date=Decimal("7500.00"),
                remarks="Within budget"
            ),
            ProjectCostSummary(
                project_id=project3.id,
                resource_group_id=rg4.id,
                total_cost_to_date=Decimal("84000.00"),
                updated_date=date.today(),
                costs_passed_back_to_date=Decimal("70000.00"),
                gpt_costs_to_date=Decimal("6000.00"),
                gpt_costs_passed_back_to_date=Decimal("5500.00"),
                remarks="Slightly over budget"
            ),
        ]
        
        db.add_all(summaries)
        
        # Create AI consumption data
        aiq_data = []
        for day_offset in range(30):
            consumption_day = date.today() - timedelta(days=day_offset)
            aiq_data.extend([
                AIQConsumption(
                    project_id=project1.id,
                    aiq_assumption_name="GPT-4 Usage",
                    consumption_amount=Decimal("150.00") + Decimal(day_offset * 2),
                    consumption_day=consumption_day
                ),
                AIQConsumption(
                    project_id=project2.id,
                    aiq_assumption_name="GPT-4 Usage",
                    consumption_amount=Decimal("200.00") + Decimal(day_offset * 3),
                    consumption_day=consumption_day
                ),
            ])
        
        db.add_all(aiq_data)
        
        db.commit()
        print("✅ Sample data seeded successfully!")
        print(f"   - Created {3} projects")
        print(f"   - Created {4} resource groups")
        print(f"   - Created {48} monthly cost records")
        print(f"   - Created {4} cost summaries")
        print(f"   - Created {60} AI consumption records")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
