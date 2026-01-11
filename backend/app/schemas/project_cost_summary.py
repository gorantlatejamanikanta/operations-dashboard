from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from decimal import Decimal


class ProjectCostSummaryBase(BaseModel):
    project_id: int
    resource_group_id: int
    total_cost_to_date: Optional[Decimal] = None
    updated_date: Optional[date] = None
    costs_passed_back_to_date: Optional[Decimal] = None
    gpt_costs_to_date: Optional[Decimal] = None
    gpt_costs_passed_back_to_date: Optional[Decimal] = None
    remarks: Optional[str] = None


class ProjectCostSummaryCreate(ProjectCostSummaryBase):
    pass


class ProjectCostSummary(ProjectCostSummaryBase):
    model_config = ConfigDict(from_attributes=True)
