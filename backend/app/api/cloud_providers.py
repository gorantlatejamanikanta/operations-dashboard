"""
Cloud Provider Management API
Handles AWS, Azure, and GCP integrations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.cloud_connection import CloudConnection as CloudConnectionModel
from ..schemas.cloud_connection import CloudConnection, CloudConnectionCreate, CloudConnectionUpdate
import json
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/cloud-providers", tags=["cloud-providers"])


class CloudProviderStatus(BaseModel):
    provider: str
    status: str
    connection_count: int
    last_sync: Optional[str] = None
    resource_count: Optional[int] = 0
    monthly_cost: Optional[float] = 0.0


class ConnectionTestResult(BaseModel):
    success: bool
    message: str
    details: Optional[Dict] = None


@router.get("/status")
def get_providers_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get status overview of all cloud providers"""
    
    # Get connection counts by provider
    connections = db.query(CloudConnectionModel).all()
    
    provider_stats = {}
    for conn in connections:
        if conn.provider not in provider_stats:
            provider_stats[conn.provider] = {
                "count": 0,
                "active": 0,
                "last_sync": None,
                "total_cost": 0.0
            }
        
        provider_stats[conn.provider]["count"] += 1
        if conn.status == "active":
            provider_stats[conn.provider]["active"] += 1
        
        if conn.last_sync and (not provider_stats[conn.provider]["last_sync"] or 
                              conn.last_sync > provider_stats[conn.provider]["last_sync"]):
            provider_stats[conn.provider]["last_sync"] = conn.last_sync
    
    # Build response for each provider
    providers = ["aws", "azure", "gcp"]
    result = []
    
    for provider in providers:
        stats = provider_stats.get(provider, {"count": 0, "active": 0, "last_sync": None})
        
        status = "disconnected"
        if stats["active"] > 0:
            status = "connected"
        elif stats["count"] > 0:
            status = "error"
        
        result.append(CloudProviderStatus(
            provider=provider,
            status=status,
            connection_count=stats["count"],
            last_sync=stats["last_sync"].isoformat() if stats["last_sync"] else None,
            resource_count=0,  # TODO: Implement resource counting
            monthly_cost=0.0   # TODO: Implement cost aggregation
        ))
    
    return result


@router.get("/connections", response_model=List[CloudConnection])
def get_connections(
    provider: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all cloud connections, optionally filtered by provider"""
    query = db.query(CloudConnectionModel)
    
    if provider:
        query = query.filter(CloudConnectionModel.provider == provider)
    
    return query.all()


@router.post("/connections", response_model=CloudConnection)
def create_connection(
    connection: CloudConnectionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new cloud provider connection"""
    
    # Validate provider
    if connection.provider not in ["aws", "azure", "gcp"]:
        raise HTTPException(status_code=400, detail="Invalid cloud provider")
    
    # Check if connection name already exists
    existing = db.query(CloudConnectionModel).filter(
        CloudConnectionModel.name == connection.name,
        CloudConnectionModel.provider == connection.provider
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Connection name already exists for this provider")
    
    # Create connection
    db_connection = CloudConnectionModel(
        name=connection.name,
        provider=connection.provider,
        credentials=json.dumps(connection.credentials),
        status="inactive",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    
    return db_connection


@router.get("/connections/{connection_id}", response_model=CloudConnection)
def get_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific cloud connection"""
    connection = db.query(CloudConnectionModel).filter(
        CloudConnectionModel.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return connection


@router.put("/connections/{connection_id}", response_model=CloudConnection)
def update_connection(
    connection_id: int,
    connection_update: CloudConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a cloud connection"""
    db_connection = db.query(CloudConnectionModel).filter(
        CloudConnectionModel.id == connection_id
    ).first()
    
    if not db_connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    update_data = connection_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "credentials" and value:
            setattr(db_connection, field, json.dumps(value))
        else:
            setattr(db_connection, field, value)
    
    db_connection.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_connection)
    
    return db_connection


@router.delete("/connections/{connection_id}")
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a cloud connection"""
    db_connection = db.query(CloudConnectionModel).filter(
        CloudConnectionModel.id == connection_id
    ).first()
    
    if not db_connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    db.delete(db_connection)
    db.commit()
    
    return {"message": "Connection deleted successfully"}


@router.post("/connections/{connection_id}/test")
def test_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Test a cloud provider connection"""
    connection = db.query(CloudConnectionModel).filter(
        CloudConnectionModel.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    try:
        # Parse credentials
        credentials = json.loads(connection.credentials)
        
        # Test connection based on provider
        if connection.provider == "aws":
            result = _test_aws_connection(credentials)
        elif connection.provider == "azure":
            result = _test_azure_connection(credentials)
        elif connection.provider == "gcp":
            result = _test_gcp_connection(credentials)
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
        
        # Update connection status based on test result
        if result.success:
            connection.status = "active"
            connection.last_sync = datetime.utcnow()
        else:
            connection.status = "error"
        
        connection.updated_at = datetime.utcnow()
        db.commit()
        
        return result
        
    except Exception as e:
        connection.status = "error"
        connection.updated_at = datetime.utcnow()
        db.commit()
        
        return ConnectionTestResult(
            success=False,
            message=f"Connection test failed: {str(e)}"
        )


@router.post("/connections/{connection_id}/sync")
def sync_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Sync resources and costs from cloud provider"""
    connection = db.query(CloudConnectionModel).filter(
        CloudConnectionModel.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    if connection.status != "active":
        raise HTTPException(status_code=400, detail="Connection is not active")
    
    try:
        # Parse credentials
        credentials = json.loads(connection.credentials)
        
        # Sync based on provider
        if connection.provider == "aws":
            result = _sync_aws_resources(credentials)
        elif connection.provider == "azure":
            result = _sync_azure_resources(credentials)
        elif connection.provider == "gcp":
            result = _sync_gcp_resources(credentials)
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
        
        # Update last sync time
        connection.last_sync = datetime.utcnow()
        connection.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": "Sync completed successfully",
            "resources_synced": result.get("resources", 0),
            "costs_synced": result.get("costs", 0)
        }
        
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


# Helper functions for testing connections
def _test_aws_connection(credentials: Dict) -> ConnectionTestResult:
    """Test AWS connection"""
    try:
        from ..services.aws_service import create_aws_service
        
        required_fields = ["access_key_id", "secret_access_key", "region"]
        
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                return ConnectionTestResult(
                    success=False,
                    message=f"Missing required field: {field}"
                )
        
        # Test connection using AWS service
        aws_service = create_aws_service(credentials)
        success, message, details = aws_service.test_connection()
        
        return ConnectionTestResult(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        return ConnectionTestResult(
            success=False,
            message=f"AWS connection failed: {str(e)}"
        )


def _test_azure_connection(credentials: Dict) -> ConnectionTestResult:
    """Test Azure connection"""
    try:
        from ..services.azure_service import create_azure_service
        
        required_fields = ["subscription_id", "client_id", "client_secret", "tenant_id"]
        
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                return ConnectionTestResult(
                    success=False,
                    message=f"Missing required field: {field}"
                )
        
        # Test connection using Azure service
        azure_service = create_azure_service(credentials)
        success, message, details = azure_service.test_connection()
        
        return ConnectionTestResult(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        return ConnectionTestResult(
            success=False,
            message=f"Azure connection failed: {str(e)}"
        )


def _test_gcp_connection(credentials: Dict) -> ConnectionTestResult:
    """Test GCP connection"""
    try:
        from ..services.gcp_service import create_gcp_service
        
        required_fields = ["project_id", "service_account_key"]
        
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                return ConnectionTestResult(
                    success=False,
                    message=f"Missing required field: {field}"
                )
        
        # Test connection using GCP service
        gcp_service = create_gcp_service(credentials)
        success, message, details = gcp_service.test_connection()
        
        return ConnectionTestResult(
            success=success,
            message=message,
            details=details
        )
        
    except Exception as e:
        return ConnectionTestResult(
            success=False,
            message=f"GCP connection failed: {str(e)}"
        )


# Helper functions for syncing resources
def _sync_aws_resources(credentials: Dict) -> Dict:
    """Sync AWS resources"""
    try:
        from ..services.aws_service import create_aws_service
        
        aws_service = create_aws_service(credentials)
        
        # Get resources and costs
        resources = aws_service.get_resources()
        
        # Get cost data for the last month
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        costs = aws_service.get_cost_data(start_date, end_date)
        
        return {
            "resources": len(resources),
            "costs": len(costs)
        }
        
    except Exception as e:
        print(f"Error syncing AWS resources: {e}")
        return {"resources": 0, "costs": 0}


def _sync_azure_resources(credentials: Dict) -> Dict:
    """Sync Azure resources"""
    try:
        from ..services.azure_service import create_azure_service
        
        azure_service = create_azure_service(credentials)
        
        # Get resources and costs
        resources = azure_service.get_resources()
        
        # Get cost data for the last month
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        costs = azure_service.get_cost_data(start_date, end_date)
        
        return {
            "resources": len(resources),
            "costs": len(costs)
        }
        
    except Exception as e:
        print(f"Error syncing Azure resources: {e}")
        return {"resources": 0, "costs": 0}


def _sync_gcp_resources(credentials: Dict) -> Dict:
    """Sync GCP resources"""
    try:
        from ..services.gcp_service import create_gcp_service
        
        gcp_service = create_gcp_service(credentials)
        
        # Get resources and costs
        resources = gcp_service.get_resources()
        
        # Get cost data for the last month
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        costs = gcp_service.get_cost_data(start_date, end_date)
        
        return {
            "resources": len(resources),
            "costs": len(costs)
        }
        
    except Exception as e:
        print(f"Error syncing GCP resources: {e}")
        return {"resources": 0, "costs": 0}