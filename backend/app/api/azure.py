"""
Azure Integration API endpoints
For connecting to Azure and syncing cost data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..services.azure_cost_service import azure_cost_service
from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.resource_group import ResourceGroup
from ..models.project import Project
from ..models.monthly_cost import MonthlyCost as MonthlyCostModel
from ..schemas.monthly_cost import MonthlyCostCreate
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/api/azure", tags=["azure"])


class AzureSyncRequest(BaseModel):
    project_id: int
    resource_group_name: str
    start_date: str  # ISO format date
    end_date: str    # ISO format date
    subscription_id: Optional[str] = None


@router.get("/configured")
def check_azure_configured(current_user: dict = Depends(get_current_user)):
    """Check if Azure credentials are configured"""
    return {
        "configured": azure_cost_service.is_configured(),
        "message": "Azure credentials configured" if azure_cost_service.is_configured() 
                   else "Azure credentials not configured. Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, and AZURE_SUBSCRIPTION_ID"
    }


@router.get("/resource-groups")
def list_azure_resource_groups(
    subscription_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all resource groups from Azure subscription"""
    try:
        resource_groups = azure_cost_service.list_resource_groups(subscription_id)
        return {"resource_groups": resource_groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-costs")
def sync_azure_costs(
    request: AzureSyncRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Sync costs from Azure for a resource group and import into the database
    
    This endpoint:
    1. Fetches costs from Azure Cost Management API
    2. Links them to the project's resource group
    3. Creates monthly cost entries in the database
    """
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Find or create resource group
        resource_group = db.query(ResourceGroup).filter(
            ResourceGroup.project_id == request.project_id,
            ResourceGroup.resource_group_name == request.resource_group_name
        ).first()
        
        if not resource_group:
            # Create resource group if it doesn't exist
            resource_group = ResourceGroup(
                resource_group_name=request.resource_group_name,
                project_id=request.project_id,
                status="Active"
            )
            db.add(resource_group)
            db.commit()
            db.refresh(resource_group)
        
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
        
        # Fetch costs from Azure
        azure_costs = azure_cost_service.get_resource_group_costs(
            resource_group_name=request.resource_group_name,
            start_date=start_date,
            end_date=end_date,
            subscription_id=request.subscription_id
        )
        
        # Import costs into database
        imported_count = 0
        for cost_record in azure_costs:
            # Check if cost already exists
            existing = db.query(MonthlyCostModel).filter(
                MonthlyCostModel.project_id == request.project_id,
                MonthlyCostModel.resource_group_id == resource_group.id,
                MonthlyCostModel.month == cost_record['date'].date()
            ).first()
            
            if existing:
                existing.cost = Decimal(str(cost_record['cost']))
            else:
                db_cost = MonthlyCostModel(
                    project_id=request.project_id,
                    resource_group_id=resource_group.id,
                    month=cost_record['date'].date(),
                    cost=Decimal(str(cost_record['cost']))
                )
                db.add(db_cost)
            imported_count += 1
        
        db.commit()
        
        return {
            "message": f"Successfully synced {imported_count} cost records",
            "resource_group_id": resource_group.id,
            "records_imported": imported_count
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource-groups/{resource_group_name}/costs")
def get_azure_resource_group_costs(
    resource_group_name: str,
    start_date: str,
    end_date: str,
    subscription_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Fetch costs for a specific Azure resource group"""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        costs = azure_cost_service.get_resource_group_costs(
            resource_group_name=resource_group_name,
            start_date=start,
            end_date=end,
            subscription_id=subscription_id
        )
        
        return {"costs": costs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
