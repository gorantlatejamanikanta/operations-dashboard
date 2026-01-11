from sqlalchemy import Column, Integer, String, Boolean, Date, Text
from sqlalchemy.orm import relationship
from ..core.database import Base


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(Text, nullable=False)
    project_type = Column(Text, nullable=False)  # 'Internal', 'External', 'Client Demo'
    member_firm = Column(Text, nullable=False)
    deployed_region = Column(Text, nullable=False)  # 'US', 'EU', 'APAC'
    is_active = Column(Boolean)
    description = Column(Text)
    engagement_code = Column(Text)
    engagement_partner = Column(Text)
    opportunity_code = Column(Text)
    engagement_manager = Column(Text)
    project_startdate = Column(Date, nullable=False)
    project_enddate = Column(Date, nullable=False)

    # Relationships
    aiq_consumptions = relationship("AIQConsumption", back_populates="project")
    resource_groups = relationship("ResourceGroup", back_populates="project")
    monthly_costs = relationship("MonthlyCost", back_populates="project")
    cost_summaries = relationship("ProjectCostSummary", back_populates="project")
