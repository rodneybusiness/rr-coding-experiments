"""
Capital Program Model

Company-level capital vehicle management for animation financing.
Enables tracking capital sources, deployment to projects, and portfolio-level constraints.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field, field_validator, model_validator


class ProgramType(str, Enum):
    """Types of capital programs/vehicles"""
    # Internal company funds
    INTERNAL_POOL = "internal_pool"

    # External investor capital
    EXTERNAL_FUND = "external_fund"
    PRIVATE_EQUITY = "private_equity"
    FAMILY_OFFICE = "family_office"

    # Studio/Streamer arrangements
    OUTPUT_DEAL = "output_deal"
    FIRST_LOOK = "first_look"
    OVERHEAD_DEAL = "overhead_deal"

    # Special structures
    SPV = "spv"  # Special Purpose Vehicle per project
    TAX_CREDIT_FUND = "tax_credit_fund"
    INTERNATIONAL_COPRO = "international_copro"
    GOVERNMENT_FUND = "government_fund"


class ProgramStatus(str, Enum):
    """Status of the capital program"""
    PROSPECTIVE = "prospective"
    IN_NEGOTIATION = "in_negotiation"
    ACTIVE = "active"
    FULLY_DEPLOYED = "fully_deployed"
    WINDING_DOWN = "winding_down"
    CLOSED = "closed"


class AllocationStatus(str, Enum):
    """Status of a capital deployment/allocation"""
    PENDING = "pending"
    APPROVED = "approved"
    COMMITTED = "committed"
    FUNDED = "funded"
    RECOUPED = "recouped"
    WRITTEN_OFF = "written_off"


class CapitalSource(BaseModel):
    """
    A source of capital within a program.
    Programs can have multiple sources (e.g., fund with LP commitments).
    """
    source_id: str = Field(..., description="Unique identifier for this source")
    source_name: str = Field(..., min_length=1, max_length=200)
    source_type: str = Field(
        default="general",
        description="Type: general, lp_commitment, credit_facility, grant, etc."
    )

    committed_amount: Decimal = Field(..., gt=0, description="Total committed capital")
    drawn_amount: Decimal = Field(default=Decimal("0"), ge=0, description="Amount already drawn")
    currency: str = Field(default="USD")

    # Terms
    interest_rate: Optional[Decimal] = Field(
        default=None, ge=0, le=50,
        description="Annual interest/preferred return rate %"
    )
    management_fee_pct: Optional[Decimal] = Field(
        default=None, ge=0, le=5,
        description="Annual management fee %"
    )
    carry_percentage: Optional[Decimal] = Field(
        default=None, ge=0, le=50,
        description="Carried interest/profit share %"
    )
    hurdle_rate: Optional[Decimal] = Field(
        default=None, ge=0, le=30,
        description="Preferred return hurdle rate %"
    )

    # Restrictions
    geographic_restrictions: List[str] = Field(
        default_factory=list,
        description="Required/permitted geographies for deployment"
    )
    genre_restrictions: List[str] = Field(
        default_factory=list,
        description="Required/permitted content genres"
    )
    budget_range_min: Optional[Decimal] = Field(default=None, ge=0)
    budget_range_max: Optional[Decimal] = Field(default=None, gt=0)

    # Dates
    commitment_date: Optional[date] = Field(default=None)
    expiry_date: Optional[date] = Field(default=None)

    notes: Optional[str] = Field(default=None, max_length=2000)

    @property
    def available_amount(self) -> Decimal:
        """Capital available for deployment"""
        return self.committed_amount - self.drawn_amount

    @property
    def utilization_rate(self) -> Decimal:
        """Percentage of committed capital deployed"""
        if self.committed_amount == 0:
            return Decimal("0")
        return (self.drawn_amount / self.committed_amount) * Decimal("100")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "committed_amount": str(self.committed_amount),
            "drawn_amount": str(self.drawn_amount),
            "available_amount": str(self.available_amount),
            "utilization_rate": str(self.utilization_rate),
            "currency": self.currency,
            "interest_rate": str(self.interest_rate) if self.interest_rate else None,
            "management_fee_pct": str(self.management_fee_pct) if self.management_fee_pct else None,
            "carry_percentage": str(self.carry_percentage) if self.carry_percentage else None,
            "hurdle_rate": str(self.hurdle_rate) if self.hurdle_rate else None,
            "geographic_restrictions": self.geographic_restrictions,
            "genre_restrictions": self.genre_restrictions,
            "budget_range_min": str(self.budget_range_min) if self.budget_range_min else None,
            "budget_range_max": str(self.budget_range_max) if self.budget_range_max else None,
            "commitment_date": self.commitment_date.isoformat() if self.commitment_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "notes": self.notes,
        }


class CapitalDeployment(BaseModel):
    """
    A deployment of capital from a program to a specific project.
    Tracks the full lifecycle from allocation through recoupment.
    """
    deployment_id: str = Field(..., description="Unique identifier")
    program_id: str = Field(..., description="Parent program")
    source_id: Optional[str] = Field(default=None, description="Specific source within program")
    project_id: str = Field(..., description="Target project")
    project_name: str = Field(..., min_length=1, max_length=200)

    # Financial
    allocated_amount: Decimal = Field(..., gt=0, description="Amount allocated to project")
    funded_amount: Decimal = Field(default=Decimal("0"), ge=0, description="Amount actually funded")
    recouped_amount: Decimal = Field(default=Decimal("0"), ge=0, description="Amount recouped")
    profit_distributed: Decimal = Field(default=Decimal("0"), ge=0, description="Profit distributed")
    currency: str = Field(default="USD")

    status: AllocationStatus = Field(default=AllocationStatus.PENDING)

    # Terms specific to this deployment
    equity_percentage: Optional[Decimal] = Field(
        default=None, ge=0, le=100,
        description="Equity ownership % in the project"
    )
    recoupment_priority: int = Field(
        default=8, ge=1, le=15,
        description="Priority in waterfall (1=first)"
    )
    backend_participation_pct: Optional[Decimal] = Field(
        default=None, ge=0, le=100,
        description="Backend profit participation %"
    )

    # Dates
    allocation_date: date = Field(default_factory=date.today)
    funding_date: Optional[date] = Field(default=None)
    expected_recoupment_date: Optional[date] = Field(default=None)

    notes: Optional[str] = Field(default=None, max_length=2000)

    @property
    def outstanding_amount(self) -> Decimal:
        """Amount still outstanding (funded - recouped)"""
        return max(Decimal("0"), self.funded_amount - self.recouped_amount)

    @property
    def total_return(self) -> Decimal:
        """Total returned (recouped + profit)"""
        return self.recouped_amount + self.profit_distributed

    @property
    def multiple(self) -> Optional[Decimal]:
        """Return multiple on funded amount"""
        if self.funded_amount == 0:
            return None
        return self.total_return / self.funded_amount

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "deployment_id": self.deployment_id,
            "program_id": self.program_id,
            "source_id": self.source_id,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "allocated_amount": str(self.allocated_amount),
            "funded_amount": str(self.funded_amount),
            "recouped_amount": str(self.recouped_amount),
            "profit_distributed": str(self.profit_distributed),
            "outstanding_amount": str(self.outstanding_amount),
            "total_return": str(self.total_return),
            "multiple": str(self.multiple) if self.multiple else None,
            "currency": self.currency,
            "status": self.status.value,
            "equity_percentage": str(self.equity_percentage) if self.equity_percentage else None,
            "recoupment_priority": self.recoupment_priority,
            "backend_participation_pct": str(self.backend_participation_pct) if self.backend_participation_pct else None,
            "allocation_date": self.allocation_date.isoformat(),
            "funding_date": self.funding_date.isoformat() if self.funding_date else None,
            "expected_recoupment_date": self.expected_recoupment_date.isoformat() if self.expected_recoupment_date else None,
            "notes": self.notes,
        }


class CapitalProgramConstraints(BaseModel):
    """
    Portfolio-level constraints for a capital program.
    Defines both hard limits (must not exceed) and soft limits (targets).
    """
    # === HARD CONSTRAINTS (must be satisfied) ===

    # Concentration limits
    max_single_project_pct: Decimal = Field(
        default=Decimal("25"),
        ge=1, le=100,
        description="Max % of fund in single project"
    )
    max_single_counterparty_pct: Decimal = Field(
        default=Decimal("40"),
        ge=1, le=100,
        description="Max % exposure to single counterparty"
    )

    # Project requirements
    min_project_budget: Optional[Decimal] = Field(
        default=None, gt=0,
        description="Minimum project budget for deployment"
    )
    max_project_budget: Optional[Decimal] = Field(
        default=None, gt=0,
        description="Maximum project budget for deployment"
    )

    # Geographic requirements
    required_jurisdictions: List[str] = Field(
        default_factory=list,
        description="Must deploy in these jurisdictions"
    )
    prohibited_jurisdictions: List[str] = Field(
        default_factory=list,
        description="Cannot deploy in these jurisdictions"
    )

    # Content requirements
    required_genres: List[str] = Field(
        default_factory=list,
        description="Must be these genres"
    )
    prohibited_genres: List[str] = Field(
        default_factory=list,
        description="Cannot be these genres"
    )

    # Rating requirements
    prohibited_ratings: List[str] = Field(
        default_factory=list,
        description="Cannot fund projects with these ratings (e.g., ['R', 'NC-17'])"
    )

    # === SOFT CONSTRAINTS (targets, not enforced) ===

    # Portfolio diversification targets
    target_num_projects: Optional[int] = Field(
        default=None, ge=1,
        description="Target number of projects in portfolio"
    )
    target_avg_budget: Optional[Decimal] = Field(
        default=None, gt=0,
        description="Target average project budget"
    )

    # Return targets
    target_portfolio_irr: Optional[Decimal] = Field(
        default=None, ge=0, le=100,
        description="Target portfolio IRR %"
    )
    target_multiple: Optional[Decimal] = Field(
        default=None, ge=0,
        description="Target portfolio return multiple"
    )

    # Risk targets
    max_development_pct: Decimal = Field(
        default=Decimal("30"),
        ge=0, le=100,
        description="Max % of fund in development-stage projects"
    )
    max_first_time_director_pct: Decimal = Field(
        default=Decimal("20"),
        ge=0, le=100,
        description="Max % of fund with first-time directors"
    )

    # Deployment pacing
    target_deployment_years: Optional[int] = Field(
        default=None, ge=1, le=10,
        description="Target years to deploy capital"
    )
    min_reserve_pct: Decimal = Field(
        default=Decimal("10"),
        ge=0, le=50,
        description="Min % to reserve for follow-ons and overages"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "hard_constraints": {
                "max_single_project_pct": str(self.max_single_project_pct),
                "max_single_counterparty_pct": str(self.max_single_counterparty_pct),
                "min_project_budget": str(self.min_project_budget) if self.min_project_budget else None,
                "max_project_budget": str(self.max_project_budget) if self.max_project_budget else None,
                "required_jurisdictions": self.required_jurisdictions,
                "prohibited_jurisdictions": self.prohibited_jurisdictions,
                "required_genres": self.required_genres,
                "prohibited_genres": self.prohibited_genres,
                "prohibited_ratings": self.prohibited_ratings,
            },
            "soft_constraints": {
                "target_num_projects": self.target_num_projects,
                "target_avg_budget": str(self.target_avg_budget) if self.target_avg_budget else None,
                "target_portfolio_irr": str(self.target_portfolio_irr) if self.target_portfolio_irr else None,
                "target_multiple": str(self.target_multiple) if self.target_multiple else None,
                "max_development_pct": str(self.max_development_pct),
                "max_first_time_director_pct": str(self.max_first_time_director_pct),
                "target_deployment_years": self.target_deployment_years,
                "min_reserve_pct": str(self.min_reserve_pct),
            }
        }


class CapitalProgram(BaseModel):
    """
    A capital program/vehicle for financing animation projects.

    Represents company-level capital management including:
    - Multiple capital sources (LPs, credit facilities, etc.)
    - Deployments to individual projects
    - Portfolio-level constraints and targets
    - Performance tracking and reporting
    """
    program_id: str = Field(..., description="Unique identifier")
    program_name: str = Field(..., min_length=1, max_length=200)
    program_type: ProgramType = Field(..., description="Type of capital vehicle")
    status: ProgramStatus = Field(default=ProgramStatus.PROSPECTIVE)

    # Description
    description: Optional[str] = Field(default=None, max_length=2000)

    # Total capacity
    target_size: Decimal = Field(..., gt=0, description="Target fund size")
    currency: str = Field(default="USD")

    # Components
    sources: List[CapitalSource] = Field(
        default_factory=list,
        description="Capital sources within this program"
    )
    deployments: List[CapitalDeployment] = Field(
        default_factory=list,
        description="Deployments to projects"
    )
    constraints: CapitalProgramConstraints = Field(
        default_factory=CapitalProgramConstraints,
        description="Portfolio constraints"
    )

    # Management
    manager_name: Optional[str] = Field(default=None, max_length=200)
    management_fee_pct: Optional[Decimal] = Field(
        default=None, ge=0, le=5,
        description="Annual management fee %"
    )
    carry_percentage: Optional[Decimal] = Field(
        default=None, ge=0, le=50,
        description="Carried interest %"
    )
    hurdle_rate: Optional[Decimal] = Field(
        default=None, ge=0, le=30,
        description="Preferred return hurdle %"
    )

    # Term
    vintage_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    investment_period_years: int = Field(default=3, ge=1, le=10)
    fund_term_years: int = Field(default=10, ge=1, le=20)
    extension_years: int = Field(default=2, ge=0, le=5)

    # Dates
    formation_date: Optional[date] = Field(default=None)
    first_close_date: Optional[date] = Field(default=None)
    final_close_date: Optional[date] = Field(default=None)

    notes: Optional[str] = Field(default=None, max_length=5000)

    # === COMPUTED PROPERTIES ===

    @property
    def total_committed(self) -> Decimal:
        """Total capital committed from all sources"""
        return sum(s.committed_amount for s in self.sources)

    @property
    def total_drawn(self) -> Decimal:
        """Total capital drawn from sources"""
        return sum(s.drawn_amount for s in self.sources)

    @property
    def total_available(self) -> Decimal:
        """Total capital available for deployment"""
        return sum(s.available_amount for s in self.sources)

    @property
    def total_allocated(self) -> Decimal:
        """Total allocated to projects"""
        return sum(d.allocated_amount for d in self.deployments)

    @property
    def total_funded(self) -> Decimal:
        """Total actually funded to projects"""
        return sum(d.funded_amount for d in self.deployments)

    @property
    def total_recouped(self) -> Decimal:
        """Total recouped from projects"""
        return sum(d.recouped_amount for d in self.deployments)

    @property
    def total_profit(self) -> Decimal:
        """Total profit distributed from projects"""
        return sum(d.profit_distributed for d in self.deployments)

    @property
    def commitment_progress(self) -> Decimal:
        """Progress toward target size"""
        if self.target_size == 0:
            return Decimal("0")
        return (self.total_committed / self.target_size) * Decimal("100")

    @property
    def deployment_rate(self) -> Decimal:
        """Percentage of committed capital deployed"""
        if self.total_committed == 0:
            return Decimal("0")
        return (self.total_allocated / self.total_committed) * Decimal("100")

    @property
    def num_active_projects(self) -> int:
        """Number of projects with active deployments"""
        active_statuses = {AllocationStatus.APPROVED, AllocationStatus.COMMITTED, AllocationStatus.FUNDED}
        return len([d for d in self.deployments if d.status in active_statuses])

    @property
    def portfolio_multiple(self) -> Optional[Decimal]:
        """Current portfolio return multiple"""
        if self.total_funded == 0:
            return None
        total_return = self.total_recouped + self.total_profit
        return total_return / self.total_funded

    @property
    def reserve_amount(self) -> Decimal:
        """Amount reserved per constraints"""
        return self.total_committed * self.constraints.min_reserve_pct / Decimal("100")

    @property
    def deployable_capital(self) -> Decimal:
        """Capital available for new deployments (after reserves)"""
        return max(Decimal("0"), self.total_available - self.reserve_amount)

    # === VALIDATION ===

    @model_validator(mode="after")
    def validate_program(self) -> "CapitalProgram":
        """Validate program consistency"""
        # Ensure drawn doesn't exceed committed
        if self.total_drawn > self.total_committed:
            raise ValueError("Total drawn cannot exceed total committed")

        # Ensure funded doesn't exceed allocated
        if self.total_funded > self.total_allocated:
            raise ValueError("Total funded cannot exceed total allocated")

        # Validate fund term
        if self.investment_period_years > self.fund_term_years:
            raise ValueError("Investment period cannot exceed fund term")

        return self

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "program_id": self.program_id,
            "program_name": self.program_name,
            "program_type": self.program_type.value,
            "status": self.status.value,
            "description": self.description,
            "target_size": str(self.target_size),
            "currency": self.currency,
            "sources": [s.to_dict() for s in self.sources],
            "deployments": [d.to_dict() for d in self.deployments],
            "constraints": self.constraints.to_dict(),
            "manager_name": self.manager_name,
            "management_fee_pct": str(self.management_fee_pct) if self.management_fee_pct else None,
            "carry_percentage": str(self.carry_percentage) if self.carry_percentage else None,
            "hurdle_rate": str(self.hurdle_rate) if self.hurdle_rate else None,
            "vintage_year": self.vintage_year,
            "investment_period_years": self.investment_period_years,
            "fund_term_years": self.fund_term_years,
            "extension_years": self.extension_years,
            "formation_date": self.formation_date.isoformat() if self.formation_date else None,
            "first_close_date": self.first_close_date.isoformat() if self.first_close_date else None,
            "final_close_date": self.final_close_date.isoformat() if self.final_close_date else None,
            "notes": self.notes,
            # Computed metrics
            "metrics": {
                "total_committed": str(self.total_committed),
                "total_drawn": str(self.total_drawn),
                "total_available": str(self.total_available),
                "total_allocated": str(self.total_allocated),
                "total_funded": str(self.total_funded),
                "total_recouped": str(self.total_recouped),
                "total_profit": str(self.total_profit),
                "commitment_progress": str(self.commitment_progress),
                "deployment_rate": str(self.deployment_rate),
                "num_active_projects": self.num_active_projects,
                "portfolio_multiple": str(self.portfolio_multiple) if self.portfolio_multiple else None,
                "reserve_amount": str(self.reserve_amount),
                "deployable_capital": str(self.deployable_capital),
            }
        }

    class Config:
        json_schema_extra = {
            "example": {
                "program_id": "PROG-001",
                "program_name": "Animation Fund I",
                "program_type": "external_fund",
                "status": "active",
                "target_size": "50000000",
                "currency": "USD",
                "manager_name": "Film Finance Partners",
                "management_fee_pct": "2.0",
                "carry_percentage": "20.0",
                "hurdle_rate": "8.0",
                "vintage_year": 2024,
                "investment_period_years": 3,
                "fund_term_years": 10,
            }
        }


# === FACTORY FUNCTIONS ===

def create_internal_pool(
    program_id: str,
    program_name: str,
    target_size: Decimal,
    committed_amount: Decimal,
) -> CapitalProgram:
    """Create an internal capital pool (company funds)"""
    source = CapitalSource(
        source_id=f"{program_id}_internal",
        source_name="Internal Capital",
        source_type="general",
        committed_amount=committed_amount,
    )
    return CapitalProgram(
        program_id=program_id,
        program_name=program_name,
        program_type=ProgramType.INTERNAL_POOL,
        status=ProgramStatus.ACTIVE,
        target_size=target_size,
        sources=[source],
    )


def create_external_fund(
    program_id: str,
    program_name: str,
    target_size: Decimal,
    manager_name: str,
    management_fee_pct: Decimal = Decimal("2.0"),
    carry_percentage: Decimal = Decimal("20.0"),
    hurdle_rate: Decimal = Decimal("8.0"),
    vintage_year: Optional[int] = None,
) -> CapitalProgram:
    """Create an external fund structure"""
    from datetime import date as dt
    vintage = vintage_year or dt.today().year

    return CapitalProgram(
        program_id=program_id,
        program_name=program_name,
        program_type=ProgramType.EXTERNAL_FUND,
        status=ProgramStatus.PROSPECTIVE,
        target_size=target_size,
        manager_name=manager_name,
        management_fee_pct=management_fee_pct,
        carry_percentage=carry_percentage,
        hurdle_rate=hurdle_rate,
        vintage_year=vintage,
        investment_period_years=3,
        fund_term_years=10,
        extension_years=2,
    )


def create_output_deal(
    program_id: str,
    program_name: str,
    studio_name: str,
    commitment: Decimal,
    num_pictures: int,
    term_years: int = 5,
) -> CapitalProgram:
    """Create a studio output deal"""
    source = CapitalSource(
        source_id=f"{program_id}_studio",
        source_name=f"{studio_name} Commitment",
        source_type="studio_commitment",
        committed_amount=commitment,
    )
    constraints = CapitalProgramConstraints(
        target_num_projects=num_pictures,
    )
    return CapitalProgram(
        program_id=program_id,
        program_name=program_name,
        program_type=ProgramType.OUTPUT_DEAL,
        status=ProgramStatus.ACTIVE,
        description=f"Output deal with {studio_name} for {num_pictures} pictures",
        target_size=commitment,
        sources=[source],
        constraints=constraints,
        fund_term_years=term_years,
        investment_period_years=term_years,
    )


def create_spv(
    program_id: str,
    project_name: str,
    project_budget: Decimal,
) -> CapitalProgram:
    """Create a Special Purpose Vehicle for a single project"""
    return CapitalProgram(
        program_id=program_id,
        program_name=f"SPV - {project_name}",
        program_type=ProgramType.SPV,
        status=ProgramStatus.PROSPECTIVE,
        description=f"Single-purpose vehicle for {project_name}",
        target_size=project_budget,
        constraints=CapitalProgramConstraints(
            max_single_project_pct=Decimal("100"),  # SPV funds only one project
            target_num_projects=1,
        ),
        investment_period_years=2,
        fund_term_years=7,
    )
