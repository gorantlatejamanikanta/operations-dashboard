from sqlalchemy import Column, Integer, Numeric, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class ProjectCostSummary(Base):
    __tablename__ = "project_cost_summary"

    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    resource_group_id = Column(Integer, ForeignKey("resource_group.id"), primary_key=True)
    total_cost_to_date = Column(Numeric)
    updated_date = Column(Date)
    costs_passed_back_to_date = Column(Numeric)
    gpt_costs_to_date = Column(Numeric)
    gpt_costs_passed_back_to_date = Column(Numeric)
    remarks = Column(Text)

    project = relationship("Project", back_populates="cost_summaries")
    resource_group = relationship("ResourceGroup", back_populates="cost_summaries")
