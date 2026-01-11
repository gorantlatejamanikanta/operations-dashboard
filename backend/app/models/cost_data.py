from sqlalchemy import Column, Integer, Numeric, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class CostData(Base):
    __tablename__ = "cost_data"

    key = Column(Text, primary_key=True)
    period = Column(Date, nullable=False)
    month_year = Column(Text, nullable=False)
    resource_group_id = Column(Integer, ForeignKey("resource_group.id"))
    cost = Column(Numeric)

    resource_group = relationship("ResourceGroup", back_populates="cost_data")
