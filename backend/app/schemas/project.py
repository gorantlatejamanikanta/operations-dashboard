from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class ProjectBase(BaseModel):
    project_name: str
    project_type: str
    member_firm: str
    deployed_region: str
    is_active: Optional[bool] = True
    description: Optional[str] = None
    engagement_code: Optional[str] = None
    engagement_partner: Optional[str] = None
    opportunity_code: Optional[str] = None
    engagement_manager: Optional[str] = None
    project_startdate: date
    project_enddate: date


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_type: Optional[str] = None
    member_firm: Optional[str] = None
    deployed_region: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    engagement_code: Optional[str] = None
    engagement_partner: Optional[str] = None
    opportunity_code: Optional[str] = None
    engagement_manager: Optional[str] = None
    project_startdate: Optional[date] = None
    project_enddate: Optional[date] = None


class Project(ProjectBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
