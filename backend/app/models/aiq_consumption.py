from sqlalchemy import Column, Integer, Numeric, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class AIQConsumption(Base):
    __tablename__ = "aiq_consumption"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    aiq_assumption_name = Column(Text)
    consumption_amount = Column(Numeric, nullable=False)
    consumption_day = Column(Date, nullable=False)

    project = relationship("Project", back_populates="aiq_consumptions")
