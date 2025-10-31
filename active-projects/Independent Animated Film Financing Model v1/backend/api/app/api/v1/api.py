"""
API V1 Router

Combines all endpoint routers for API v1.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import incentives, waterfall, scenarios

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    incentives.router,
    prefix="/incentives",
    tags=["Engine 1: Tax Incentives"]
)

api_router.include_router(
    waterfall.router,
    prefix="/waterfall",
    tags=["Engine 2: Waterfall"]
)

api_router.include_router(
    scenarios.router,
    prefix="/scenarios",
    tags=["Engine 3: Scenarios"]
)
