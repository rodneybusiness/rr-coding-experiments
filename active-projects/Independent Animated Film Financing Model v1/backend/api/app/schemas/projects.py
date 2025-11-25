"""
Project Profile Schemas

Pydantic schemas for project management API endpoints.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectProfileInput(BaseModel):
    """Input schema for creating/updating a project."""

    project_name: str = Field(..., description="Name of the project")
    project_budget: Decimal = Field(..., gt=0, description="Total project budget")
    genre: Optional[str] = Field(None, description="Project genre (e.g., Animation, Drama)")
    jurisdiction: Optional[str] = Field(None, description="Primary jurisdiction for production")
    rating: Optional[str] = Field(None, description="Target rating (e.g., G, PG, PG-13, R)")
    is_development: bool = Field(False, description="Whether project is in development stage")
    is_first_time_director: bool = Field(False, description="Whether director is first-time")
    expected_revenue: Optional[Decimal] = Field(None, ge=0, description="Expected total revenue")
    production_start_date: Optional[str] = Field(None, description="Production start date (YYYY-MM-DD)")
    expected_release_date: Optional[str] = Field(None, description="Expected release date (YYYY-MM-DD)")
    description: Optional[str] = Field(None, description="Project description")
    notes: Optional[str] = Field(None, description="Additional notes")


class ProjectProfileUpdate(BaseModel):
    """Input schema for partial project updates."""

    project_name: Optional[str] = None
    project_budget: Optional[Decimal] = Field(None, gt=0)
    genre: Optional[str] = None
    jurisdiction: Optional[str] = None
    rating: Optional[str] = None
    is_development: Optional[bool] = None
    is_first_time_director: Optional[bool] = None
    expected_revenue: Optional[Decimal] = Field(None, ge=0)
    production_start_date: Optional[str] = None
    expected_release_date: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class CapitalDeploymentSummary(BaseModel):
    """Summary of a capital deployment for a project."""

    deployment_id: str
    program_id: str
    program_name: str
    allocated_amount: Decimal
    funded_amount: Decimal
    recouped_amount: Decimal
    profit_distributed: Decimal
    outstanding_amount: Decimal
    total_return: Decimal
    multiple: Optional[Decimal] = None
    currency: str = "USD"
    status: str
    allocation_date: str
    notes: Optional[str] = None


class ProjectProfileResponse(BaseModel):
    """Response schema for a project profile."""

    project_id: str
    project_name: str
    project_budget: Decimal
    genre: Optional[str] = None
    jurisdiction: Optional[str] = None
    rating: Optional[str] = None
    is_development: bool = False
    is_first_time_director: bool = False
    expected_revenue: Optional[Decimal] = None
    production_start_date: Optional[str] = None
    expected_release_date: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str
    capital_deployments: List[CapitalDeploymentSummary] = []
    total_funding: Decimal = Decimal("0")
    funding_gap: Decimal


class ProjectListResponse(BaseModel):
    """Response schema for listing projects."""

    projects: List[ProjectProfileResponse]
    total_count: int


class DashboardMetrics(BaseModel):
    """Aggregated metrics for the dashboard."""

    total_projects: int
    total_budget: Decimal
    total_tax_incentives: Decimal
    average_capture_rate: Decimal
    scenarios_generated: int
    active_capital_programs: int
    total_committed_capital: Decimal
    total_deployed_capital: Decimal
    projects_in_development: int
    projects_in_production: int


class RecentActivity(BaseModel):
    """A recent activity entry."""

    project: str
    action: str
    time: str
    activity_type: str  # 'scenario', 'incentive', 'waterfall', 'deal', 'capital'


class DashboardResponse(BaseModel):
    """Response schema for the dashboard endpoint."""

    metrics: DashboardMetrics
    recent_activity: List[RecentActivity]
