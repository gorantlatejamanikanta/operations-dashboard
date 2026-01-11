from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class MonthlyCost(Base):
    __tablename__ = "monthly_cost"

    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    resource_group_id = Column(Integer, ForeignKey("resource_group.id"), primary_key=True)
    month = Column(Date, primary_key=True)
    cost = Column(Numeric)

    project = relationship("Project", back_populates="monthly_costs")
    resource_group = relationship("ResourceGroup", back_populates="monthly_costs")
