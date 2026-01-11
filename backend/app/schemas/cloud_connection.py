from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum


class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CloudConnectionBase(BaseModel):
    name: str
    provider: CloudProvider
    description: Optional[str] = None
    regions: Optional[List[str]] = None
    tags: Optional[Dict[str, str]] = None
    auto_sync: Optional[bool] = True
    sync_frequency: Optional[int] = 3600


class CloudConnectionCreate(CloudConnectionBase):
    credentials: Dict[str, str]


class CloudConnectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    regions: Optional[List[str]] = None
    tags: Optional[Dict[str, str]] = None
    auto_sync: Optional[bool] = None
    sync_frequency: Optional[int] = None
    status: Optional[ConnectionStatus] = None


class CloudConnection(CloudConnectionBase):
    id: int
    status: ConnectionStatus
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    resource_count: Optional[int] = 0
    last_cost_sync: Optional[datetime] = None
    monthly_cost: Optional[float] = 0.0
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def credentials_masked(self) -> Dict[str, str]:
        """Return credentials with sensitive values masked"""
        # This would be implemented to return masked credentials for display
        return {"status": "configured"}


class CloudConnectionSummary(BaseModel):
    """Summary view of cloud connection for listings"""
    id: int
    name: str
    provider: CloudProvider
    status: ConnectionStatus
    last_sync: Optional[datetime] = None
    resource_count: Optional[int] = 0
    monthly_cost: Optional[float] = 0.0
    
    model_config = ConfigDict(from_attributes=True)