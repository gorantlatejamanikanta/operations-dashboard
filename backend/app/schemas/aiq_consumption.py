from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from decimal import Decimal


class AIQConsumptionBase(BaseModel):
    project_id: int
    aiq_assumption_name: Optional[str] = None
    consumption_amount: Decimal
    consumption_day: date


class AIQConsumptionCreate(AIQConsumptionBase):
    pass


class AIQConsumption(AIQConsumptionBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
