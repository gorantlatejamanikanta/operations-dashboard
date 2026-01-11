from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class ResourceGroup(Base):
    __tablename__ = "resource_group"

    id = Column(Integer, primary_key=True, index=True)
    resource_group_name = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    status = Column(Text)

    project = relationship("Project", back_populates="resource_groups")
    monthly_costs = relationship("MonthlyCost", back_populates="resource_group")
    cost_data = relationship("CostData", back_populates="resource_group")
    cost_summaries = relationship("ProjectCostSummary", back_populates="resource_group")
