from sqlalchemy import Column, Integer, String, Boolean, Date, Text, Enum
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class ProjectStatus(enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(Text, nullable=False)
    project_type = Column(Text, nullable=False)  # 'Internal', 'External', 'Client Demo'
    member_firm = Column(Text, nullable=False)
    deployed_region = Column(Text, nullable=False)  # 'US', 'EU', 'APAC'
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    engagement_code = Column(Text)
    engagement_partner = Column(Text)
    opportunity_code = Column(Text)
    engagement_manager = Column(Text)
    project_startdate = Column(Date, nullable=False)
    project_enddate = Column(Date, nullable=False)
    
    # New status management fields
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    progress_percentage = Column(Integer, default=0)  # 0-100
    budget_allocated = Column(Integer)  # Budget in cents
    budget_spent = Column(Integer, default=0)  # Spent amount in cents
    
    # Additional project metadata
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    health_status = Column(String(20), default="green")  # green, yellow, red
    last_status_update = Column(Date)
    status_notes = Column(Text)
    
    # Project Intake Form fields
    business_justification = Column(Text)
    business_unit = Column(Text)
    department = Column(Text)
    cost_center = Column(Text)
    project_sponsor = Column(Text)
    project_manager = Column(Text)
    technical_lead = Column(Text)
    budget_source = Column(Text)
    cloud_providers = Column(Text)  # Comma-separated list
    compliance_requirements = Column(Text)  # Comma-separated list
    security_classification = Column(String(50), default="Internal")
    client_name = Column(Text)
    contract_type = Column(Text)
    risk_assessment = Column(String(20), default="Low")
    data_classification = Column(String(50), default="Internal")
    regulatory_requirements = Column(Text)
    success_criteria = Column(Text)
    assumptions = Column(Text)
    dependencies = Column(Text)
    constraints = Column(Text)

    # Relationships
    aiq_consumptions = relationship("AIQConsumption", back_populates="project")
    resource_groups = relationship("ResourceGroup", back_populates="project")
    monthly_costs = relationship("MonthlyCost", back_populates="project")
    cost_summaries = relationship("ProjectCostSummary", back_populates="project")
