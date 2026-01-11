from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from ..core.database import get_db
from ..models.project import Project
from ..models.monthly_cost import MonthlyCost
from ..models.project_cost_summary import ProjectCostSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_projects = db.query(func.count(Project.id)).scalar()
    active_projects = db.query(func.count(Project.id)).filter(Project.is_active == True).scalar()
    
    total_cost = db.query(func.sum(ProjectCostSummary.total_cost_to_date)).scalar() or 0
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_cost": float(total_cost)
    }


@router.get("/cost-trends")
def get_cost_trends(db: Session = Depends(get_db)):
    """Get cost trends by month"""
    trends = db.query(
        MonthlyCost.month,
        func.sum(MonthlyCost.cost).label("total_cost")
    ).group_by(MonthlyCost.month).order_by(MonthlyCost.month).all()
    
    return [
        {
            "month": str(trend.month),
            "cost": float(trend.total_cost or 0)
        }
        for trend in trends
    ]


@router.get("/regional-distribution")
def get_regional_distribution(db: Session = Depends(get_db)):
    """Get cost distribution by region"""
    distribution = db.query(
        Project.deployed_region,
        func.sum(ProjectCostSummary.total_cost_to_date).label("total_cost")
    ).join(
        ProjectCostSummary, Project.id == ProjectCostSummary.project_id
    ).group_by(Project.deployed_region).all()
    
    return [
        {
            "region": dist.deployed_region,
            "cost": float(dist.total_cost or 0)
        }
        for dist in distribution
    ]
