from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import chat, projects, dashboard, costs, azure, resource_groups

app = FastAPI(
    title="Multi-Cloud Operations Dashboard API",
    description="Backend API for Multi-Cloud Operations Dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(projects.router)
app.include_router(resource_groups.router)
app.include_router(dashboard.router)
app.include_router(costs.router)
app.include_router(azure.router)


@app.get("/")
def root():
    return {"message": "Multi-Cloud Operations Dashboard API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
