from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..schemas.monthly_cost import MonthlyCost, MonthlyCostCreate
from ..schemas.project_cost_summary import ProjectCostSummary, ProjectCostSummaryCreate
from ..schemas.cost_data import CostData, CostDataCreate
from ..models.monthly_cost import MonthlyCost as MonthlyCostModel
from ..models.project_cost_summary import ProjectCostSummary as ProjectCostSummaryModel
from ..models.cost_data import CostData as CostDataModel
from ..models.resource_group import ResourceGroup
from ..core.database import get_db
from ..core.auth import get_current_user
from decimal import Decimal

router = APIRouter(prefix="/api/costs", tags=["costs"])


@router.post("/monthly", response_model=MonthlyCost)
def create_monthly_cost(
    cost: MonthlyCostCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a monthly cost entry for a project and resource group"""
    # Verify resource group exists
    resource_group = db.query(ResourceGroup).filter(
        ResourceGroup.id == cost.resource_group_id
    ).first()
    if not resource_group:
        raise HTTPException(status_code=404, detail="Resource group not found")
    
    # Validate cost is not negative
    if cost.cost is not None and cost.cost < 0:
        raise HTTPException(status_code=400, detail="Cost cannot be negative")
    
    # Check if cost already exists for this month
    existing = db.query(MonthlyCostModel).filter(
        MonthlyCostModel.project_id == cost.project_id,
        MonthlyCostModel.resource_group_id == cost.resource_group_id,
        MonthlyCostModel.month == cost.month
    ).first()
    
    if existing:
        # Update existing cost
        existing.cost = cost.cost
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new cost entry
    db_cost = MonthlyCostModel(**cost.model_dump())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost


@router.get("/monthly", response_model=List[MonthlyCost])
def get_monthly_costs(
    project_id: Optional[int] = None,
    resource_group_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get monthly costs, optionally filtered by project or resource group"""
    query = db.query(MonthlyCostModel)
    
    if project_id:
        query = query.filter(MonthlyCostModel.project_id == project_id)
    if resource_group_id:
        query = query.filter(MonthlyCostModel.resource_group_id == resource_group_id)
    
    return query.order_by(MonthlyCostModel.month.desc()).offset(skip).limit(limit).all()


@router.post("/summary", response_model=ProjectCostSummary)
def create_or_update_cost_summary(
    summary: ProjectCostSummaryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create or update a cost summary for a project and resource group"""
    existing = db.query(ProjectCostSummaryModel).filter(
        ProjectCostSummaryModel.project_id == summary.project_id,
        ProjectCostSummaryModel.resource_group_id == summary.resource_group_id
    ).first()
    
    if existing:
        # Update existing summary
        update_data = summary.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new summary
    db_summary = ProjectCostSummaryModel(**summary.model_dump())
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary


@router.get("/summary/{project_id}/{resource_group_id}", response_model=ProjectCostSummary)
def get_cost_summary(
    project_id: int,
    resource_group_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cost summary for a specific project and resource group"""
    summary = db.query(ProjectCostSummaryModel).filter(
        ProjectCostSummaryModel.project_id == project_id,
        ProjectCostSummaryModel.resource_group_id == resource_group_id
    ).first()
    
    if not summary:
        raise HTTPException(status_code=404, detail="Cost summary not found")
    return summary


@router.post("/data", response_model=CostData)
def create_cost_data(
    cost_data: CostDataCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a cost data entry"""
    db_cost_data = CostDataModel(**cost_data.model_dump())
    db.add(db_cost_data)
    db.commit()
    db.refresh(db_cost_data)
    return db_cost_data
