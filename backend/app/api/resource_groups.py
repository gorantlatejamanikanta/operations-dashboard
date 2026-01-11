from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..schemas.resource_group import ResourceGroup, ResourceGroupCreate
from ..models.resource_group import ResourceGroup as ResourceGroupModel
from ..core.database import get_db
from ..core.auth import get_current_user

router = APIRouter(prefix="/api/resource-groups", tags=["resource-groups"])


@router.get("/", response_model=List[ResourceGroup])
def get_resource_groups(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all resource groups, optionally filtered by project"""
    query = db.query(ResourceGroupModel)
    
    if project_id:
        query = query.filter(ResourceGroupModel.project_id == project_id)
    
    resource_groups = query.offset(skip).limit(limit).all()
    return resource_groups


@router.get("/{resource_group_id}", response_model=ResourceGroup)
def get_resource_group(
    resource_group_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific resource group"""
    resource_group = db.query(ResourceGroupModel).filter(
        ResourceGroupModel.id == resource_group_id
    ).first()
    
    if not resource_group:
        raise HTTPException(status_code=404, detail="Resource group not found")
    
    return resource_group


@router.post("/", response_model=ResourceGroup)
def create_resource_group(
    resource_group: ResourceGroupCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new resource group"""
    db_resource_group = ResourceGroupModel(**resource_group.model_dump())
    db.add(db_resource_group)
    db.commit()
    db.refresh(db_resource_group)
    return db_resource_group


@router.put("/{resource_group_id}", response_model=ResourceGroup)
def update_resource_group(
    resource_group_id: int,
    resource_group: ResourceGroupCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a resource group"""
    db_resource_group = db.query(ResourceGroupModel).filter(
        ResourceGroupModel.id == resource_group_id
    ).first()
    
    if not db_resource_group:
        raise HTTPException(status_code=404, detail="Resource group not found")
    
    update_data = resource_group.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_resource_group, field, value)
    
    db.commit()
    db.refresh(db_resource_group)
    return db_resource_group


@router.delete("/{resource_group_id}")
def delete_resource_group(
    resource_group_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a resource group"""
    db_resource_group = db.query(ResourceGroupModel).filter(
        ResourceGroupModel.id == resource_group_id
    ).first()
    
    if not db_resource_group:
        raise HTTPException(status_code=404, detail="Resource group not found")
    
    db.delete(db_resource_group)
    db.commit()
    return {"message": "Resource group deleted successfully"}