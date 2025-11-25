"""
Projects CRUD API Endpoints

Provides management functionality for project profiles.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict
import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.projects import (
    ProjectProfileInput,
    ProjectProfileUpdate,
    ProjectProfileResponse,
    ProjectListResponse,
    CapitalDeploymentSummary,
    DashboardMetrics,
    DashboardResponse,
    RecentActivity,
)

router = APIRouter()

# In-memory storage (replace with database in production)
projects_storage: Dict[str, Dict] = {}
activity_log: List[Dict] = []


def _log_activity(project_name: str, action: str, activity_type: str):
    """Log a project activity."""
    activity_log.insert(0, {
        "project": project_name,
        "action": action,
        "time": datetime.now().isoformat(),
        "activity_type": activity_type,
    })
    # Keep only last 100 activities
    if len(activity_log) > 100:
        activity_log.pop()


def _project_to_response(project: Dict) -> ProjectProfileResponse:
    """Convert stored project to response schema."""
    deployments = project.get("capital_deployments", [])
    total_funding = sum(d.get("funded_amount", 0) for d in deployments)
    funding_gap = project["project_budget"] - total_funding

    return ProjectProfileResponse(
        project_id=project["project_id"],
        project_name=project["project_name"],
        project_budget=Decimal(str(project["project_budget"])),
        genre=project.get("genre"),
        jurisdiction=project.get("jurisdiction"),
        rating=project.get("rating"),
        is_development=project.get("is_development", False),
        is_first_time_director=project.get("is_first_time_director", False),
        expected_revenue=Decimal(str(project["expected_revenue"])) if project.get("expected_revenue") else None,
        production_start_date=project.get("production_start_date"),
        expected_release_date=project.get("expected_release_date"),
        description=project.get("description"),
        notes=project.get("notes"),
        created_at=project["created_at"],
        updated_at=project["updated_at"],
        capital_deployments=[
            CapitalDeploymentSummary(
                deployment_id=d["deployment_id"],
                program_id=d["program_id"],
                program_name=d.get("program_name", "Unknown Program"),
                allocated_amount=Decimal(str(d.get("allocated_amount", 0))),
                funded_amount=Decimal(str(d.get("funded_amount", 0))),
                recouped_amount=Decimal(str(d.get("recouped_amount", 0))),
                profit_distributed=Decimal(str(d.get("profit_distributed", 0))),
                outstanding_amount=Decimal(str(d.get("outstanding_amount", 0))),
                total_return=Decimal(str(d.get("total_return", 0))),
                multiple=Decimal(str(d["multiple"])) if d.get("multiple") else None,
                currency=d.get("currency", "USD"),
                status=d.get("status", "pending"),
                allocation_date=d.get("allocation_date", ""),
                notes=d.get("notes"),
            )
            for d in deployments
        ],
        total_funding=Decimal(str(total_funding)),
        funding_gap=Decimal(str(funding_gap)),
    )


@router.post(
    "",
    response_model=ProjectProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project",
    description="Create a new project profile",
)
async def create_project(project: ProjectProfileInput) -> ProjectProfileResponse:
    """
    Create a new project profile.

    Args:
        project: Project profile data

    Returns:
        Created project profile with generated ID
    """
    project_id = f"proj_{uuid.uuid4().hex[:12]}"
    now = datetime.now().isoformat()

    stored_project = {
        "project_id": project_id,
        "project_name": project.project_name,
        "project_budget": float(project.project_budget),
        "genre": project.genre,
        "jurisdiction": project.jurisdiction,
        "rating": project.rating,
        "is_development": project.is_development,
        "is_first_time_director": project.is_first_time_director,
        "expected_revenue": float(project.expected_revenue) if project.expected_revenue else None,
        "production_start_date": project.production_start_date,
        "expected_release_date": project.expected_release_date,
        "description": project.description,
        "notes": project.notes,
        "created_at": now,
        "updated_at": now,
        "capital_deployments": [],
    }

    projects_storage[project_id] = stored_project
    _log_activity(project.project_name, "Created project", "project")

    return _project_to_response(stored_project)


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List Projects",
    description="Get list of all projects with optional filtering",
)
async def list_projects(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    is_development: Optional[bool] = Query(None, description="Filter by development stage"),
    min_budget: Optional[float] = Query(None, description="Minimum budget filter"),
    max_budget: Optional[float] = Query(None, description="Maximum budget filter"),
    has_funding_gap: Optional[bool] = Query(None, description="Filter projects with funding gap"),
    limit: int = Query(50, ge=1, le=100, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> ProjectListResponse:
    """
    List all projects with optional filtering.

    Args:
        Various filter parameters

    Returns:
        List of matching projects
    """
    projects = list(projects_storage.values())

    # Apply filters
    if genre:
        projects = [p for p in projects if p.get("genre", "").lower() == genre.lower()]
    if jurisdiction:
        projects = [p for p in projects if p.get("jurisdiction", "").lower() == jurisdiction.lower()]
    if is_development is not None:
        projects = [p for p in projects if p.get("is_development", False) == is_development]
    if min_budget is not None:
        projects = [p for p in projects if p.get("project_budget", 0) >= min_budget]
    if max_budget is not None:
        projects = [p for p in projects if p.get("project_budget", 0) <= max_budget]
    if has_funding_gap is not None:
        projects = [
            p for p in projects
            if (p["project_budget"] - sum(d.get("funded_amount", 0) for d in p.get("capital_deployments", []))) > 0
            == has_funding_gap
        ]

    total_count = len(projects)

    # Apply pagination
    projects = projects[offset:offset + limit]

    return ProjectListResponse(
        projects=[_project_to_response(p) for p in projects],
        total_count=total_count,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectProfileResponse,
    summary="Get Project",
    description="Get a specific project by ID",
)
async def get_project(project_id: str) -> ProjectProfileResponse:
    """
    Get a project by ID.

    Args:
        project_id: The project ID

    Returns:
        The project profile

    Raises:
        HTTPException: If project not found
    """
    if project_id not in projects_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    return _project_to_response(projects_storage[project_id])


@router.patch(
    "/{project_id}",
    response_model=ProjectProfileResponse,
    summary="Update Project",
    description="Partially update a project profile",
)
async def update_project(project_id: str, update: ProjectProfileUpdate) -> ProjectProfileResponse:
    """
    Update a project profile.

    Args:
        project_id: The project ID
        update: Fields to update

    Returns:
        Updated project profile

    Raises:
        HTTPException: If project not found
    """
    if project_id not in projects_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    project = projects_storage[project_id]
    update_data = update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if value is not None:
            if key in ["project_budget", "expected_revenue"] and value is not None:
                project[key] = float(value)
            else:
                project[key] = value

    project["updated_at"] = datetime.now().isoformat()
    _log_activity(project["project_name"], "Updated project", "project")

    return _project_to_response(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Project",
    description="Delete a project profile",
)
async def delete_project(project_id: str):
    """
    Delete a project.

    Args:
        project_id: The project ID

    Raises:
        HTTPException: If project not found
    """
    if project_id not in projects_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    project_name = projects_storage[project_id]["project_name"]
    del projects_storage[project_id]
    _log_activity(project_name, "Deleted project", "project")


@router.post(
    "/{project_id}/deployments",
    response_model=ProjectProfileResponse,
    summary="Add Capital Deployment",
    description="Add a capital deployment record to a project",
)
async def add_deployment(
    project_id: str,
    deployment_id: str,
    program_id: str,
    program_name: str,
    allocated_amount: float,
    funded_amount: float = 0,
    status: str = "pending",
) -> ProjectProfileResponse:
    """
    Add a capital deployment to a project.

    Args:
        project_id: The project ID
        deployment_id: ID of the deployment
        program_id: ID of the capital program
        program_name: Name of the capital program
        allocated_amount: Amount allocated
        funded_amount: Amount funded
        status: Deployment status

    Returns:
        Updated project profile

    Raises:
        HTTPException: If project not found
    """
    if project_id not in projects_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    project = projects_storage[project_id]

    deployment = {
        "deployment_id": deployment_id,
        "program_id": program_id,
        "program_name": program_name,
        "allocated_amount": allocated_amount,
        "funded_amount": funded_amount,
        "recouped_amount": 0,
        "profit_distributed": 0,
        "outstanding_amount": funded_amount,
        "total_return": 0,
        "multiple": None,
        "currency": "USD",
        "status": status,
        "allocation_date": datetime.now().isoformat(),
        "notes": None,
    }

    project["capital_deployments"].append(deployment)
    project["updated_at"] = datetime.now().isoformat()
    _log_activity(project["project_name"], f"Added ${allocated_amount:,.0f} capital allocation", "capital")

    return _project_to_response(project)


@router.get(
    "/dashboard/metrics",
    response_model=DashboardResponse,
    summary="Get Dashboard Metrics",
    description="Get aggregated metrics for the dashboard",
)
async def get_dashboard_metrics() -> DashboardResponse:
    """
    Get aggregated metrics for the dashboard.

    Returns:
        Dashboard metrics and recent activity
    """
    projects = list(projects_storage.values())

    # Calculate metrics
    total_projects = len(projects)
    total_budget = sum(p.get("project_budget", 0) for p in projects)

    # Estimate tax incentives (assume 20% average capture)
    total_tax_incentives = total_budget * 0.20
    average_capture_rate = Decimal("20.0")

    # Count development vs production
    projects_in_development = sum(1 for p in projects if p.get("is_development", False))
    projects_in_production = total_projects - projects_in_development

    # Calculate total deployed capital
    total_funded = sum(
        sum(d.get("funded_amount", 0) for d in p.get("capital_deployments", []))
        for p in projects
    )

    metrics = DashboardMetrics(
        total_projects=total_projects,
        total_budget=Decimal(str(total_budget)),
        total_tax_incentives=Decimal(str(total_tax_incentives)),
        average_capture_rate=average_capture_rate,
        scenarios_generated=total_projects * 4,  # Estimate 4 scenarios per project
        active_capital_programs=3,  # Placeholder - would query from capital_programs
        total_committed_capital=Decimal(str(total_budget * 0.7)),  # Estimate
        total_deployed_capital=Decimal(str(total_funded)),
        projects_in_development=projects_in_development,
        projects_in_production=projects_in_production,
    )

    # Get recent activity (last 10)
    recent = activity_log[:10] if activity_log else [
        {"project": "Sample Project A", "action": "Optimized capital stack", "time": "2 hours ago", "activity_type": "scenario"},
        {"project": "Sample Project B", "action": "Calculated tax incentives", "time": "5 hours ago", "activity_type": "incentive"},
        {"project": "Sample Project C", "action": "Ran waterfall analysis", "time": "1 day ago", "activity_type": "waterfall"},
    ]

    return DashboardResponse(
        metrics=metrics,
        recent_activity=[
            RecentActivity(
                project=a["project"],
                action=a["action"],
                time=a["time"] if "ago" in a["time"] else _format_time_ago(a["time"]),
                activity_type=a["activity_type"],
            )
            for a in recent
        ],
    )


def _format_time_ago(iso_time: str) -> str:
    """Convert ISO timestamp to human-readable 'time ago' format."""
    try:
        timestamp = datetime.fromisoformat(iso_time)
        diff = datetime.now() - timestamp
        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
    except Exception:
        return iso_time
