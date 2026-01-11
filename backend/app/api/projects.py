from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectStatusUpdate
from ..models.project import Project as ProjectModel
from ..core.database import get_db
from ..core.auth import get_current_user, require_role

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", 
            response_model=List[Project],
            summary="Get Projects",
            description="Retrieve a list of projects with optional filtering",
            responses={
                200: {
                    "description": "List of projects retrieved successfully",
                    "content": {
                        "application/json": {
                            "example": [
                                {
                                    "id": 1,
                                    "project_name": "Cloud Migration Project",
                                    "project_type": "External",
                                    "member_firm": "Acme Corp",
                                    "deployed_region": "US",
                                    "is_active": True,
                                    "description": "Migrate legacy systems to cloud",
                                    "engagement_manager": "John Doe",
                                    "project_startdate": "2024-01-01",
                                    "project_enddate": "2024-12-31"
                                }
                            ]
                        }
                    }
                },
                400: {"description": "Invalid query parameters"},
                401: {"description": "Authentication required"},
                403: {"description": "Insufficient permissions"}
            })
def get_projects(
    skip: int = 0, 
    limit: int = 100, 
    status: str = None,
    region: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a paginated list of projects with optional filtering.
    
    **Query Parameters:**
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **status**: Filter by project status (planning, active, on-hold, completed, cancelled)
    - **region**: Filter by deployment region (US, EU, APAC)
    
    **Authentication:** Required (any authenticated user)
    
    **Rate Limit:** Included in the 100 requests/minute limit
    """
    # Validate query parameters
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip must be non-negative")
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
    
    query = db.query(ProjectModel)
    
    if status:
        valid_statuses = ["planning", "active", "on-hold", "completed", "cancelled"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        query = query.filter(ProjectModel.status == status)
    
    if region:
        valid_regions = ["US", "EU", "APAC"]
        if region not in valid_regions:
            raise HTTPException(status_code=400, detail=f"Invalid region. Must be one of: {valid_regions}")
        query = query.filter(ProjectModel.deployed_region == region)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific project"""
    if project_id < 1:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", 
             response_model=Project,
             summary="Create Project",
             description="Create a new project",
             responses={
                 201: {
                     "description": "Project created successfully",
                     "content": {
                         "application/json": {
                             "example": {
                                 "id": 1,
                                 "project_name": "New Cloud Project",
                                 "project_type": "External",
                                 "member_firm": "Client Corp",
                                 "deployed_region": "US",
                                 "is_active": True,
                                 "description": "New project description",
                                 "project_startdate": "2024-01-01",
                                 "project_enddate": "2024-12-31"
                             }
                         }
                     }
                 },
                 400: {"description": "Invalid input data"},
                 401: {"description": "Authentication required"},
                 403: {"description": "Insufficient permissions (user role required)"},
                 422: {"description": "Validation error"}
             })
def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("user"))  # Require at least user role
):
    """
    Create a new project in the system.
    
    **Required Fields:**
    - **project_name**: Unique name for the project
    - **project_type**: Type of project (Internal, External, Client Demo)
    - **member_firm**: Associated member firm
    - **deployed_region**: Deployment region (US, EU, APAC)
    - **project_startdate**: Project start date (YYYY-MM-DD)
    - **project_enddate**: Project end date (YYYY-MM-DD)
    
    **Optional Fields:**
    - **description**: Project description
    - **engagement_manager**: Manager assigned to the project
    - **engagement_code**: Internal engagement code
    - **engagement_partner**: Partner information
    - **opportunity_code**: Opportunity tracking code
    
    **Authentication:** Required (user role or higher)
    
    **Validation:**
    - Project name must be unique
    - Start date must be before end date
    - Region must be valid (US, EU, APAC)
    - Project type must be valid
    """
    try:
        project_data = project.model_dump()
        project_data['last_status_update'] = date.today()
        
        db_project = ProjectModel(**project_data)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        db.rollback()
        print(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create project")


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int, 
    project: ProjectUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("user"))  # Require at least user role
):
    """Update a project"""
    if project_id < 1:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    try:
        db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        update_data = project.model_dump(exclude_unset=True)
        
        # Update last_status_update if status-related fields are being updated
        if any(field in update_data for field in ['status', 'progress_percentage', 'health_status']):
            update_data['last_status_update'] = date.today()
        
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update project")


@router.patch("/{project_id}/status", response_model=Project)
def update_project_status(
    project_id: int,
    status_update: ProjectStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("user"))  # Require at least user role
):
    """Update project status and related fields"""
    if project_id < 1:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    try:
        db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update status fields
        db_project.status = status_update.status
        db_project.last_status_update = date.today()
        
        if status_update.progress_percentage is not None:
            if not 0 <= status_update.progress_percentage <= 100:
                raise HTTPException(status_code=400, detail="Progress percentage must be between 0 and 100")
            db_project.progress_percentage = status_update.progress_percentage
        
        if status_update.health_status is not None:
            db_project.health_status = status_update.health_status
        
        if status_update.status_notes is not None:
            db_project.status_notes = status_update.status_notes
        
        # Auto-update is_active based on status
        if status_update.status in ["completed", "cancelled"]:
            db_project.is_active = False
        elif status_update.status in ["active", "planning"]:
            db_project.is_active = True
        
        db.commit()
        db.refresh(db_project)
        return db_project
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating project status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update project status")


@router.get("/{project_id}/status-history")
def get_project_status_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get project status history (placeholder for future implementation)"""
    if project_id < 1:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # For now, return current status info
    # In a full implementation, you'd have a separate status_history table
    return {
        "project_id": project_id,
        "current_status": project.status,
        "last_update": project.last_status_update,
        "progress": project.progress_percentage,
        "health": project.health_status,
        "notes": project.status_notes
    }


@router.delete("/{project_id}")
def delete_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))  # Require admin role for deletion
):
    """Delete a project"""
    if project_id < 1:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    try:
        db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        db.delete(db_project)
        db.commit()
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete project")
