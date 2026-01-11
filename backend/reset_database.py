"""Script to reset database tables"""
from app.core.database import engine, Base, drop_tables, create_tables
from app.models import (
    Project,
    AIQConsumption,
    ResourceGroup,
    ProjectResourceGroup,
    MonthlyCost,
    CostData,
    ProjectCostSummary,
    CloudConnection,
)

if __name__ == "__main__":
    print("Dropping existing database tables...")
    drop_tables()
    print("✅ Database tables dropped successfully!")
    
    print("Creating new database tables...")
    create_tables()
    print("✅ Database tables created successfully!")
    
    print("Database reset complete!")