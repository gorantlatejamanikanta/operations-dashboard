from pydantic import BaseModel, ConfigDict, Field, validator
from datetime import date
from typing import Optional
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, Enum):
    """Project priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectHealthStatus(str, Enum):
    """Project health status indicators"""
    GREEN = "green"    # On track
    YELLOW = "yellow"  # At risk
    RED = "red"        # Critical issues


class ProjectBase(BaseModel):
    """Base project model with core fields and validation"""
    
    project_name: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Unique name for the project",
        example="Cloud Migration Project"
    )
    project_type: str = Field(
        ..., 
        description="Type of project",
        example="External"
    )
    member_firm: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Associated member firm or client",
        example="Acme Corporation"
    )
    deployed_region: str = Field(
        ..., 
        description="Primary deployment region",
        example="US"
    )
    is_active: Optional[bool] = Field(
        True, 
        description="Whether the project is currently active"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Detailed project description",
        example="Migration of legacy systems to cloud infrastructure"
    )
    engagement_code: Optional[str] = Field(
        None, 
        max_length=50,
        description="Internal engagement tracking code",
        example="ENG-2024-001"
    )
    engagement_partner: Optional[str] = Field(
        None, 
        max_length=200,
        description="Partner responsible for the engagement",
        example="Jane Smith"
    )
    opportunity_code: Optional[str] = Field(
        None, 
        max_length=50,
        description="Sales opportunity tracking code",
        example="OPP-2024-001"
    )
    engagement_manager: Optional[str] = Field(
        None, 
        max_length=200,
        description="Manager assigned to this engagement",
        example="John Doe"
    )
    project_startdate: date = Field(
        ..., 
        description="Project start date",
        example="2024-01-01"
    )
    project_enddate: date = Field(
        ..., 
        description="Project end date",
        example="2024-12-31"
    )
    
    # Status management fields
    status: Optional[ProjectStatus] = Field(
        ProjectStatus.PLANNING, 
        description="Current project status"
    )
    progress_percentage: Optional[int] = Field(
        0, 
        ge=0, 
        le=100,
        description="Project completion percentage (0-100)",
        example=45
    )
    budget_allocated: Optional[int] = Field(
        None, 
        ge=0,
        description="Total budget allocated in USD",
        example=100000
    )
    budget_spent: Optional[int] = Field(
        0, 
        ge=0,
        description="Amount spent so far in USD",
        example=45000
    )
    priority: Optional[ProjectPriority] = Field(
        ProjectPriority.MEDIUM, 
        description="Project priority level"
    )
    health_status: Optional[ProjectHealthStatus] = Field(
        ProjectHealthStatus.GREEN, 
        description="Project health indicator"
    )
    last_status_update: Optional[date] = Field(
        None, 
        description="Date of last status update"
    )
    status_notes: Optional[str] = Field(
        None, 
        max_length=500,
        description="Notes about current status",
        example="Project is on track, no major issues"
    )
    
    # Project Intake Form fields
    business_justification: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Business justification for the project"
    )
    business_unit: Optional[str] = Field(
        None, 
        max_length=100,
        description="Business unit sponsoring the project"
    )
    department: Optional[str] = Field(
        None, 
        max_length=100,
        description="Department responsible for the project"
    )
    cost_center: Optional[str] = Field(
        None, 
        max_length=50,
        description="Cost center for billing"
    )
    project_sponsor: Optional[str] = Field(
        None, 
        max_length=200,
        description="Executive sponsor of the project"
    )
    project_manager: Optional[str] = Field(
        None, 
        max_length=200,
        description="Project manager assigned"
    )
    technical_lead: Optional[str] = Field(
        None, 
        max_length=200,
        description="Technical lead for the project"
    )
    budget_source: Optional[str] = Field(
        None, 
        max_length=100,
        description="Source of project funding"
    )
    cloud_providers: Optional[str] = Field(
        None, 
        max_length=200,
        description="Cloud providers to be used (comma-separated)",
        example="AWS, Azure"
    )
    compliance_requirements: Optional[str] = Field(
        None, 
        max_length=500,
        description="Compliance requirements (comma-separated)",
        example="SOC2, GDPR, HIPAA"
    )
    security_classification: Optional[str] = Field(
        "Internal", 
        max_length=50,
        description="Security classification level",
        example="Internal"
    )
    client_name: Optional[str] = Field(
        None, 
        max_length=200,
        description="Client name for external projects"
    )
    contract_type: Optional[str] = Field(
        None, 
        max_length=100,
        description="Type of contract",
        example="Fixed Price"
    )
    risk_assessment: Optional[str] = Field(
        "Low", 
        max_length=50,
        description="Overall risk assessment",
        example="Medium"
    )
    data_classification: Optional[str] = Field(
        "Internal", 
        max_length=50,
        description="Data classification level"
    )
    regulatory_requirements: Optional[str] = Field(
        None, 
        max_length=500,
        description="Regulatory requirements"
    )
    success_criteria: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Success criteria and KPIs"
    )
    assumptions: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Project assumptions"
    )
    dependencies: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Project dependencies"
    )
    constraints: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Project constraints"
    )
    
    @validator('project_enddate')
    def validate_end_date(cls, v, values):
        """Ensure end date is after start date"""
        if 'project_startdate' in values and v <= values['project_startdate']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('project_type')
    def validate_project_type(cls, v):
        """Validate project type"""
        valid_types = ['Internal', 'External', 'Client Demo']
        if v not in valid_types:
            raise ValueError(f'Project type must be one of: {valid_types}')
        return v
    
    @validator('deployed_region')
    def validate_region(cls, v):
        """Validate deployment region"""
        valid_regions = ['US', 'EU', 'APAC']
        if v not in valid_regions:
            raise ValueError(f'Region must be one of: {valid_regions}')
        return v


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    
    class Config:
        schema_extra = {
            "example": {
                "project_name": "Cloud Migration Project",
                "project_type": "External",
                "member_firm": "Acme Corporation",
                "deployed_region": "US",
                "description": "Migration of legacy systems to cloud infrastructure",
                "engagement_manager": "John Doe",
                "project_startdate": "2024-01-01",
                "project_enddate": "2024-12-31",
                "budget_allocated": 100000,
                "priority": "high",
                "business_justification": "Reduce operational costs and improve scalability"
            }
        }


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project"""
    
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    project_type: Optional[str] = None
    member_firm: Optional[str] = Field(None, min_length=1, max_length=200)
    deployed_region: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=1000)
    engagement_code: Optional[str] = Field(None, max_length=50)
    engagement_partner: Optional[str] = Field(None, max_length=200)
    opportunity_code: Optional[str] = Field(None, max_length=50)
    engagement_manager: Optional[str] = Field(None, max_length=200)
    project_startdate: Optional[date] = None
    project_enddate: Optional[date] = None
    
    # Status management updates
    status: Optional[ProjectStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    budget_allocated: Optional[int] = Field(None, ge=0)
    budget_spent: Optional[int] = Field(None, ge=0)
    priority: Optional[ProjectPriority] = None
    health_status: Optional[ProjectHealthStatus] = None
    last_status_update: Optional[date] = None
    status_notes: Optional[str] = Field(None, max_length=500)
    
    # Intake form updates
    business_justification: Optional[str] = Field(None, max_length=1000)
    business_unit: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    cost_center: Optional[str] = Field(None, max_length=50)
    project_sponsor: Optional[str] = Field(None, max_length=200)
    project_manager: Optional[str] = Field(None, max_length=200)
    technical_lead: Optional[str] = Field(None, max_length=200)
    budget_source: Optional[str] = Field(None, max_length=100)
    cloud_providers: Optional[str] = Field(None, max_length=200)
    compliance_requirements: Optional[str] = Field(None, max_length=500)
    security_classification: Optional[str] = Field(None, max_length=50)
    client_name: Optional[str] = Field(None, max_length=200)
    contract_type: Optional[str] = Field(None, max_length=100)
    risk_assessment: Optional[str] = Field(None, max_length=50)
    data_classification: Optional[str] = Field(None, max_length=50)
    regulatory_requirements: Optional[str] = Field(None, max_length=500)
    success_criteria: Optional[str] = Field(None, max_length=1000)
    assumptions: Optional[str] = Field(None, max_length=1000)
    dependencies: Optional[str] = Field(None, max_length=1000)
    constraints: Optional[str] = Field(None, max_length=1000)


class ProjectStatusUpdate(BaseModel):
    """Schema for updating project status"""
    
    status: ProjectStatus = Field(..., description="New project status")
    progress_percentage: Optional[int] = Field(
        None, 
        ge=0, 
        le=100,
        description="Updated progress percentage"
    )
    health_status: Optional[ProjectHealthStatus] = Field(
        None, 
        description="Updated health status"
    )
    status_notes: Optional[str] = Field(
        None, 
        max_length=500,
        description="Notes about the status update"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "active",
                "progress_percentage": 75,
                "health_status": "green",
                "status_notes": "Project is progressing well, on schedule"
            }
        }


class Project(ProjectBase):
    """Complete project model with ID"""
    
    id: int = Field(..., description="Unique project identifier", example=1)
    
    model_config = ConfigDict(from_attributes=True)
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "project_name": "Cloud Migration Project",
                "project_type": "External",
                "member_firm": "Acme Corporation",
                "deployed_region": "US",
                "is_active": True,
                "description": "Migration of legacy systems to cloud infrastructure",
                "engagement_manager": "John Doe",
                "project_startdate": "2024-01-01",
                "project_enddate": "2024-12-31",
                "status": "active",
                "progress_percentage": 45,
                "budget_allocated": 100000,
                "budget_spent": 45000,
                "priority": "high",
                "health_status": "green"
            }
        }
