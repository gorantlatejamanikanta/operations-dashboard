"""Script to create database tables"""
from app.core.database import engine, Base
from app.models import (
    Project,
    AIQConsumption,
    ResourceGroup,
    ProjectResourceGroup,
    MonthlyCost,
    CostData,
    ProjectCostSummary,
)

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
