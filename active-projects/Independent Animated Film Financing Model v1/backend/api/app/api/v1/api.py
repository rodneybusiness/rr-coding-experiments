"""
API V1 Router

Combines all endpoint routers for API v1.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    incentives,
    waterfall,
    scenarios,
    deals,
    ownership,
    capital_programs,
    projects,
)

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

api_router.include_router(
    deals.router,
    prefix="/deals",
    tags=["DealBlocks"]
)

api_router.include_router(
    ownership.router,
    prefix="/ownership",
    tags=["Ownership & Control Scoring"]
)

api_router.include_router(
    capital_programs.router,
    prefix="/capital-programs",
    tags=["Engine 5: Capital Programs"]
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"]
)
