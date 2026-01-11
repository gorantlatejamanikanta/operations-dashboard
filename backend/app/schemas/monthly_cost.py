from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from decimal import Decimal


class MonthlyCostBase(BaseModel):
    project_id: int
    resource_group_id: int
    month: date
    cost: Optional[Decimal] = None


class MonthlyCostCreate(MonthlyCostBase):
    pass


class MonthlyCost(MonthlyCostBase):
    model_config = ConfigDict(from_attributes=True)
