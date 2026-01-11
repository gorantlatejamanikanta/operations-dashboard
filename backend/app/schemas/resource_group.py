from pydantic import BaseModel, ConfigDict
from typing import Optional


class ResourceGroupBase(BaseModel):
    resource_group_name: str
    project_id: int
    status: Optional[str] = None


class ResourceGroupCreate(ResourceGroupBase):
    pass


class ResourceGroup(ResourceGroupBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
