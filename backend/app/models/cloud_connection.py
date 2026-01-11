from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class ConnectionStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class CloudProvider(enum.Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CloudConnection(Base):
    __tablename__ = "cloud_connection"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    provider = Column(Enum(CloudProvider), nullable=False)
    credentials = Column(Text, nullable=False)  # JSON string of encrypted credentials
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.INACTIVE)
    
    # Metadata
    description = Column(Text)
    regions = Column(Text)  # JSON array of regions
    tags = Column(Text)     # JSON object of tags
    
    # Sync information
    last_sync = Column(DateTime(timezone=True))
    sync_frequency = Column(Integer, default=3600)  # Sync frequency in seconds
    auto_sync = Column(String(10), default="true")  # Enable/disable auto sync
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Resource tracking
    resource_count = Column(Integer, default=0)
    last_cost_sync = Column(DateTime(timezone=True))
    monthly_cost = Column(Integer, default=0)  # Cost in cents