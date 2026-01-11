from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class ProjectResourceGroup(Base):
    __tablename__ = "project_resource_group"

    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    resource_group_id = Column(Integer, ForeignKey("resource_group.id"), primary_key=True)
