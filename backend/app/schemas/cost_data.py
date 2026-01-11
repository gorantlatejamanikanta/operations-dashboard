from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from decimal import Decimal


class CostDataBase(BaseModel):
    key: str
    period: date
    month_year: str
    resource_group_id: Optional[int] = None
    cost: Optional[Decimal] = None


class CostDataCreate(CostDataBase):
    pass


class CostData(CostDataBase):
    model_config = ConfigDict(from_attributes=True)
