"""
Capital Program API Schemas

Pydantic schemas for Capital Program API requests and responses.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field


# === INPUT SCHEMAS ===

class CapitalSourceInput(BaseModel):
    """Input schema for a capital source"""
    source_name: str = Field(..., min_length=1, max_length=200)
    source_type: str = Field(default="general")
    committed_amount: Decimal = Field(..., gt=0)
    drawn_amount: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = Field(default="USD")

    interest_rate: Optional[Decimal] = Field(default=None, ge=0, le=50)
    management_fee_pct: Optional[Decimal] = Field(default=None, ge=0, le=5)
    carry_percentage: Optional[Decimal] = Field(default=None, ge=0, le=50)
    hurdle_rate: Optional[Decimal] = Field(default=None, ge=0, le=30)

    geographic_restrictions: List[str] = Field(default_factory=list)
    genre_restrictions: List[str] = Field(default_factory=list)
    budget_range_min: Optional[Decimal] = Field(default=None, ge=0)
    budget_range_max: Optional[Decimal] = Field(default=None, gt=0)

    commitment_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class CapitalProgramConstraintsInput(BaseModel):
    """Input schema for program constraints"""
    # Hard constraints
    max_single_project_pct: Decimal = Field(default=Decimal("25"), ge=1, le=100)
    max_single_counterparty_pct: Decimal = Field(default=Decimal("40"), ge=1, le=100)
    min_project_budget: Optional[Decimal] = Field(default=None, gt=0)
    max_project_budget: Optional[Decimal] = Field(default=None, gt=0)
    required_jurisdictions: List[str] = Field(default_factory=list)
    prohibited_jurisdictions: List[str] = Field(default_factory=list)
    required_genres: List[str] = Field(default_factory=list)
    prohibited_genres: List[str] = Field(default_factory=list)
    prohibited_ratings: List[str] = Field(default_factory=list)

    # Soft constraints
    target_num_projects: Optional[int] = Field(default=None, ge=1)
    target_avg_budget: Optional[Decimal] = Field(default=None, gt=0)
    target_portfolio_irr: Optional[Decimal] = Field(default=None, ge=0, le=100)
    target_multiple: Optional[Decimal] = Field(default=None, ge=0)
    max_development_pct: Decimal = Field(default=Decimal("30"), ge=0, le=100)
    max_first_time_director_pct: Decimal = Field(default=Decimal("20"), ge=0, le=100)
    target_deployment_years: Optional[int] = Field(default=None, ge=1, le=10)
    min_reserve_pct: Decimal = Field(default=Decimal("10"), ge=0, le=50)


class CapitalProgramInput(BaseModel):
    """Input schema for creating a capital program"""
    program_name: str = Field(..., min_length=1, max_length=200)
    program_type: str = Field(..., description="Type of capital vehicle")
    description: Optional[str] = Field(default=None, max_length=2000)
    target_size: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD")

    sources: List[CapitalSourceInput] = Field(default_factory=list)
    constraints: Optional[CapitalProgramConstraintsInput] = None

    manager_name: Optional[str] = Field(default=None, max_length=200)
    management_fee_pct: Optional[Decimal] = Field(default=None, ge=0, le=5)
    carry_percentage: Optional[Decimal] = Field(default=None, ge=0, le=50)
    hurdle_rate: Optional[Decimal] = Field(default=None, ge=0, le=30)

    vintage_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    investment_period_years: int = Field(default=3, ge=1, le=10)
    fund_term_years: int = Field(default=10, ge=1, le=20)
    extension_years: int = Field(default=2, ge=0, le=5)

    formation_date: Optional[date] = None
    first_close_date: Optional[date] = None
    final_close_date: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=5000)

    class Config:
        json_schema_extra = {
            "example": {
                "program_name": "Animation Fund I",
                "program_type": "external_fund",
                "target_size": "50000000",
                "manager_name": "Film Finance Partners",
                "management_fee_pct": "2.0",
                "carry_percentage": "20.0",
                "hurdle_rate": "8.0",
                "vintage_year": 2024,
            }
        }


class AllocationRequestInput(BaseModel):
    """Input schema for capital allocation request"""
    project_id: str = Field(..., description="Target project ID")
    project_name: str = Field(..., min_length=1, max_length=200)
    requested_amount: Decimal = Field(..., gt=0)
    project_budget: Decimal = Field(..., gt=0)

    jurisdiction: Optional[str] = None
    genre: Optional[str] = None
    rating: Optional[str] = None
    is_development: bool = Field(default=False)
    is_first_time_director: bool = Field(default=False)
    counterparty_name: Optional[str] = None

    equity_percentage: Optional[Decimal] = Field(default=None, ge=0, le=100)
    recoupment_priority: int = Field(default=8, ge=1, le=15)
    backend_participation_pct: Optional[Decimal] = Field(default=None, ge=0, le=100)

    source_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "PROJ-001",
                "project_name": "Sky Warriors",
                "requested_amount": "5000000",
                "project_budget": "30000000",
                "jurisdiction": "Canada",
                "genre": "Animation",
                "equity_percentage": "16.67",
            }
        }


class FundingRequest(BaseModel):
    """Request to fund a deployment"""
    amount: Optional[Decimal] = Field(default=None, gt=0)


class RecoupmentRequest(BaseModel):
    """Request to record recoupment"""
    recouped_amount: Decimal = Field(..., ge=0)
    profit_amount: Decimal = Field(default=Decimal("0"), ge=0)


# === RESPONSE SCHEMAS ===

class CapitalSourceResponse(BaseModel):
    """Response schema for a capital source"""
    source_id: str
    source_name: str
    source_type: str
    committed_amount: Decimal
    drawn_amount: Decimal
    available_amount: Decimal
    utilization_rate: Decimal
    currency: str

    interest_rate: Optional[Decimal]
    management_fee_pct: Optional[Decimal]
    carry_percentage: Optional[Decimal]
    hurdle_rate: Optional[Decimal]

    geographic_restrictions: List[str]
    genre_restrictions: List[str]
    budget_range_min: Optional[Decimal]
    budget_range_max: Optional[Decimal]

    commitment_date: Optional[date]
    expiry_date: Optional[date]
    notes: Optional[str]


class CapitalDeploymentResponse(BaseModel):
    """Response schema for a capital deployment"""
    deployment_id: str
    program_id: str
    source_id: Optional[str]
    project_id: str
    project_name: str

    allocated_amount: Decimal
    funded_amount: Decimal
    recouped_amount: Decimal
    profit_distributed: Decimal
    outstanding_amount: Decimal
    total_return: Decimal
    multiple: Optional[Decimal]
    currency: str

    status: str
    equity_percentage: Optional[Decimal]
    recoupment_priority: int
    backend_participation_pct: Optional[Decimal]

    allocation_date: date
    funding_date: Optional[date]
    expected_recoupment_date: Optional[date]
    notes: Optional[str]


class CapitalProgramMetrics(BaseModel):
    """Portfolio metrics for a program"""
    total_committed: Decimal
    total_drawn: Decimal
    total_available: Decimal
    total_allocated: Decimal
    total_funded: Decimal
    total_recouped: Decimal
    total_profit: Decimal
    commitment_progress: Decimal
    deployment_rate: Decimal
    num_active_projects: int
    portfolio_multiple: Optional[Decimal]
    reserve_amount: Decimal
    deployable_capital: Decimal


class CapitalProgramResponse(BaseModel):
    """Response schema for a capital program"""
    program_id: str
    program_name: str
    program_type: str
    status: str
    description: Optional[str]
    target_size: Decimal
    currency: str

    sources: List[CapitalSourceResponse]
    deployments: List[CapitalDeploymentResponse]
    constraints: Dict[str, Any]

    manager_name: Optional[str]
    management_fee_pct: Optional[Decimal]
    carry_percentage: Optional[Decimal]
    hurdle_rate: Optional[Decimal]

    vintage_year: Optional[int]
    investment_period_years: int
    fund_term_years: int
    extension_years: int

    formation_date: Optional[date]
    first_close_date: Optional[date]
    final_close_date: Optional[date]
    notes: Optional[str]

    metrics: CapitalProgramMetrics


class CapitalProgramListResponse(BaseModel):
    """Response for listing programs"""
    programs: List[CapitalProgramResponse]
    total_count: int


class ConstraintViolationResponse(BaseModel):
    """Response for a constraint violation"""
    constraint_name: str
    constraint_type: str
    current_value: str
    limit_value: str
    description: str
    is_blocking: bool


class AllocationResultResponse(BaseModel):
    """Response for an allocation attempt"""
    success: bool
    allocation_id: Optional[str]
    deployment: Optional[CapitalDeploymentResponse]
    violations: List[ConstraintViolationResponse]
    warnings: List[str]
    selected_source_id: Optional[str]
    source_selection_reason: Optional[str]
    recommendations: List[str]


class PortfolioMetricsResponse(BaseModel):
    """Response for portfolio metrics"""
    size_metrics: Dict[str, Any]
    project_metrics: Dict[str, Any]
    concentration_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    constraint_compliance: Dict[str, Any]


class ProgramTypesResponse(BaseModel):
    """Response listing available program types"""
    types: List[Dict[str, str]]


class AllocationValidationRequest(BaseModel):
    """Request to validate an allocation without executing"""
    allocation: AllocationRequestInput
    dry_run: bool = Field(default=True)


class BatchAllocationRequest(BaseModel):
    """Request to allocate to multiple projects"""
    allocations: List[AllocationRequestInput] = Field(..., min_length=1)
    max_total_allocation: Optional[Decimal] = Field(default=None, gt=0)


class BatchAllocationResponse(BaseModel):
    """Response for batch allocation"""
    results: List[AllocationResultResponse]
    total_allocated: Decimal
    successful_count: int
    failed_count: int
