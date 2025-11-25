"""
Capital Program Manager

Manages capital allocation, constraint validation, and portfolio-level metrics
for animation financing programs.
"""

import logging
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional, Any, Tuple
from datetime import date

from backend.models.capital_program import (
    CapitalProgram,
    CapitalSource,
    CapitalDeployment,
    CapitalProgramConstraints,
    ProgramType,
    ProgramStatus,
    AllocationStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class AllocationRequest:
    """Request to allocate capital from a program to a project"""
    program_id: str
    project_id: str
    project_name: str
    requested_amount: Decimal
    project_budget: Decimal

    # Project characteristics for constraint checking
    jurisdiction: Optional[str] = None
    genre: Optional[str] = None
    rating: Optional[str] = None
    is_development: bool = False
    is_first_time_director: bool = False
    counterparty_name: Optional[str] = None

    # Deployment terms
    equity_percentage: Optional[Decimal] = None
    recoupment_priority: int = 8
    backend_participation_pct: Optional[Decimal] = None

    # Optional: specify source within program
    source_id: Optional[str] = None


@dataclass
class ConstraintViolation:
    """A constraint that would be violated by an allocation"""
    constraint_name: str
    constraint_type: str  # 'hard' or 'soft'
    current_value: str
    limit_value: str
    description: str
    is_blocking: bool  # Hard constraints block allocation


@dataclass
class AllocationResult:
    """Result of an allocation attempt"""
    success: bool
    allocation_id: Optional[str] = None
    deployment: Optional[CapitalDeployment] = None

    # Validation results
    violations: List[ConstraintViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Source selection
    selected_source_id: Optional[str] = None
    source_selection_reason: Optional[str] = None

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "success": self.success,
            "allocation_id": self.allocation_id,
            "deployment": self.deployment.to_dict() if self.deployment else None,
            "violations": [
                {
                    "constraint_name": v.constraint_name,
                    "constraint_type": v.constraint_type,
                    "current_value": v.current_value,
                    "limit_value": v.limit_value,
                    "description": v.description,
                    "is_blocking": v.is_blocking,
                }
                for v in self.violations
            ],
            "warnings": self.warnings,
            "selected_source_id": self.selected_source_id,
            "source_selection_reason": self.source_selection_reason,
            "recommendations": self.recommendations,
        }


@dataclass
class PortfolioMetrics:
    """Portfolio-level performance metrics"""
    # Size metrics
    total_committed: Decimal
    total_deployed: Decimal
    total_available: Decimal
    deployment_rate: Decimal

    # Project metrics
    num_projects: int
    num_active_projects: int
    avg_project_size: Optional[Decimal]

    # Concentration metrics
    largest_project_pct: Decimal
    largest_counterparty_pct: Decimal
    hhi_concentration: Decimal  # Herfindahl-Hirschman Index

    # Performance metrics
    total_recouped: Decimal
    total_profit: Decimal
    portfolio_multiple: Optional[Decimal]
    weighted_irr: Optional[Decimal]

    # Risk metrics
    development_exposure_pct: Decimal
    first_time_director_pct: Decimal

    # Constraint compliance
    hard_constraints_satisfied: bool
    soft_constraints_met: int
    soft_constraints_total: int

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "size_metrics": {
                "total_committed": str(self.total_committed),
                "total_deployed": str(self.total_deployed),
                "total_available": str(self.total_available),
                "deployment_rate": str(self.deployment_rate),
            },
            "project_metrics": {
                "num_projects": self.num_projects,
                "num_active_projects": self.num_active_projects,
                "avg_project_size": str(self.avg_project_size) if self.avg_project_size else None,
            },
            "concentration_metrics": {
                "largest_project_pct": str(self.largest_project_pct),
                "largest_counterparty_pct": str(self.largest_counterparty_pct),
                "hhi_concentration": str(self.hhi_concentration),
            },
            "performance_metrics": {
                "total_recouped": str(self.total_recouped),
                "total_profit": str(self.total_profit),
                "portfolio_multiple": str(self.portfolio_multiple) if self.portfolio_multiple else None,
                "weighted_irr": str(self.weighted_irr) if self.weighted_irr else None,
            },
            "risk_metrics": {
                "development_exposure_pct": str(self.development_exposure_pct),
                "first_time_director_pct": str(self.first_time_director_pct),
            },
            "constraint_compliance": {
                "hard_constraints_satisfied": self.hard_constraints_satisfied,
                "soft_constraints_met": self.soft_constraints_met,
                "soft_constraints_total": self.soft_constraints_total,
            },
        }


class CapitalProgramManager:
    """
    Manages capital programs, allocation decisions, and portfolio metrics.

    Key responsibilities:
    - Validate allocation requests against program constraints
    - Select optimal funding source within programs
    - Track portfolio-level metrics and concentration
    - Generate recommendations for allocation optimization
    """

    def __init__(self):
        """Initialize the manager"""
        # In-memory storage for programs (would be replaced with DB in production)
        self._programs: Dict[str, CapitalProgram] = {}
        logger.info("CapitalProgramManager initialized")

    def register_program(self, program: CapitalProgram) -> None:
        """Register a capital program for management"""
        self._programs[program.program_id] = program
        logger.info(f"Registered program: {program.program_name} ({program.program_id})")

    def get_program(self, program_id: str) -> Optional[CapitalProgram]:
        """Get a registered program by ID"""
        return self._programs.get(program_id)

    def list_programs(self) -> List[CapitalProgram]:
        """List all registered programs"""
        return list(self._programs.values())

    def allocate_capital(
        self,
        request: AllocationRequest,
        dry_run: bool = False
    ) -> AllocationResult:
        """
        Attempt to allocate capital from a program to a project.

        Args:
            request: Allocation request details
            dry_run: If True, validate but don't create deployment

        Returns:
            AllocationResult with success status, deployment, and any violations
        """
        logger.info(
            f"Processing allocation request: {request.requested_amount} from "
            f"{request.program_id} to {request.project_name}"
        )

        # Get program
        program = self._programs.get(request.program_id)
        if not program:
            return AllocationResult(
                success=False,
                violations=[ConstraintViolation(
                    constraint_name="program_exists",
                    constraint_type="hard",
                    current_value="not_found",
                    limit_value="exists",
                    description=f"Program {request.program_id} not found",
                    is_blocking=True,
                )]
            )

        # Validate program status
        if program.status not in {ProgramStatus.ACTIVE, ProgramStatus.PROSPECTIVE}:
            return AllocationResult(
                success=False,
                violations=[ConstraintViolation(
                    constraint_name="program_status",
                    constraint_type="hard",
                    current_value=program.status.value,
                    limit_value="active or prospective",
                    description="Program is not accepting new allocations",
                    is_blocking=True,
                )]
            )

        # Check constraint violations
        violations = self._check_constraints(program, request)
        hard_violations = [v for v in violations if v.is_blocking]

        if hard_violations:
            return AllocationResult(
                success=False,
                violations=violations,
                recommendations=self._generate_recommendations(program, request, violations),
            )

        # Select funding source
        source, source_reason = self._select_source(program, request)
        if not source:
            return AllocationResult(
                success=False,
                violations=[ConstraintViolation(
                    constraint_name="source_availability",
                    constraint_type="hard",
                    current_value="0",
                    limit_value=str(request.requested_amount),
                    description="No source has sufficient available capital",
                    is_blocking=True,
                )]
            )

        # Check if source can fund the request
        if source.available_amount < request.requested_amount:
            return AllocationResult(
                success=False,
                violations=[ConstraintViolation(
                    constraint_name="source_capacity",
                    constraint_type="hard",
                    current_value=str(source.available_amount),
                    limit_value=str(request.requested_amount),
                    description=f"Source {source.source_name} has insufficient capacity",
                    is_blocking=True,
                )]
            )

        # Generate warnings from soft constraint violations
        warnings = [v.description for v in violations if not v.is_blocking]

        if dry_run:
            return AllocationResult(
                success=True,
                violations=violations,
                warnings=warnings,
                selected_source_id=source.source_id,
                source_selection_reason=source_reason,
                recommendations=self._generate_recommendations(program, request, violations),
            )

        # Create deployment
        deployment_id = f"DEP-{uuid.uuid4().hex[:8].upper()}"
        deployment = CapitalDeployment(
            deployment_id=deployment_id,
            program_id=program.program_id,
            source_id=source.source_id,
            project_id=request.project_id,
            project_name=request.project_name,
            allocated_amount=request.requested_amount,
            equity_percentage=request.equity_percentage,
            recoupment_priority=request.recoupment_priority,
            backend_participation_pct=request.backend_participation_pct,
            status=AllocationStatus.APPROVED,
        )

        # Update source drawn amount
        source.drawn_amount += request.requested_amount

        # Add deployment to program
        program.deployments.append(deployment)

        logger.info(
            f"Allocation successful: {deployment_id} - {request.requested_amount} "
            f"from {source.source_name} to {request.project_name}"
        )

        return AllocationResult(
            success=True,
            allocation_id=deployment_id,
            deployment=deployment,
            violations=violations,
            warnings=warnings,
            selected_source_id=source.source_id,
            source_selection_reason=source_reason,
            recommendations=self._generate_recommendations(program, request, violations),
        )

    def _check_constraints(
        self,
        program: CapitalProgram,
        request: AllocationRequest
    ) -> List[ConstraintViolation]:
        """Check all constraints for an allocation request"""
        violations = []
        constraints = program.constraints
        total_committed = program.total_committed

        # === HARD CONSTRAINTS ===

        # Single project concentration
        if total_committed > 0:
            project_pct = (request.requested_amount / total_committed) * Decimal("100")
            if project_pct > constraints.max_single_project_pct:
                violations.append(ConstraintViolation(
                    constraint_name="max_single_project_pct",
                    constraint_type="hard",
                    current_value=f"{project_pct:.1f}%",
                    limit_value=f"{constraints.max_single_project_pct}%",
                    description=f"Allocation would exceed single project limit ({project_pct:.1f}% > {constraints.max_single_project_pct}%)",
                    is_blocking=True,
                ))

        # Project budget constraints
        if constraints.min_project_budget and request.project_budget < constraints.min_project_budget:
            violations.append(ConstraintViolation(
                constraint_name="min_project_budget",
                constraint_type="hard",
                current_value=str(request.project_budget),
                limit_value=str(constraints.min_project_budget),
                description=f"Project budget ${request.project_budget:,.0f} below minimum ${constraints.min_project_budget:,.0f}",
                is_blocking=True,
            ))

        if constraints.max_project_budget and request.project_budget > constraints.max_project_budget:
            violations.append(ConstraintViolation(
                constraint_name="max_project_budget",
                constraint_type="hard",
                current_value=str(request.project_budget),
                limit_value=str(constraints.max_project_budget),
                description=f"Project budget ${request.project_budget:,.0f} exceeds maximum ${constraints.max_project_budget:,.0f}",
                is_blocking=True,
            ))

        # Jurisdiction constraints
        if request.jurisdiction:
            if constraints.prohibited_jurisdictions and request.jurisdiction in constraints.prohibited_jurisdictions:
                violations.append(ConstraintViolation(
                    constraint_name="prohibited_jurisdiction",
                    constraint_type="hard",
                    current_value=request.jurisdiction,
                    limit_value=f"not in {constraints.prohibited_jurisdictions}",
                    description=f"Jurisdiction '{request.jurisdiction}' is prohibited",
                    is_blocking=True,
                ))
            if constraints.required_jurisdictions and request.jurisdiction not in constraints.required_jurisdictions:
                violations.append(ConstraintViolation(
                    constraint_name="required_jurisdiction",
                    constraint_type="hard",
                    current_value=request.jurisdiction,
                    limit_value=f"in {constraints.required_jurisdictions}",
                    description=f"Jurisdiction '{request.jurisdiction}' not in required list",
                    is_blocking=True,
                ))

        # Genre constraints
        if request.genre:
            if constraints.prohibited_genres and request.genre.lower() in [g.lower() for g in constraints.prohibited_genres]:
                violations.append(ConstraintViolation(
                    constraint_name="prohibited_genre",
                    constraint_type="hard",
                    current_value=request.genre,
                    limit_value=f"not in {constraints.prohibited_genres}",
                    description=f"Genre '{request.genre}' is prohibited",
                    is_blocking=True,
                ))
            if constraints.required_genres and request.genre.lower() not in [g.lower() for g in constraints.required_genres]:
                violations.append(ConstraintViolation(
                    constraint_name="required_genre",
                    constraint_type="hard",
                    current_value=request.genre,
                    limit_value=f"in {constraints.required_genres}",
                    description=f"Genre '{request.genre}' not in required list",
                    is_blocking=True,
                ))

        # Rating constraints
        if request.rating and constraints.prohibited_ratings:
            if request.rating.upper() in [r.upper() for r in constraints.prohibited_ratings]:
                violations.append(ConstraintViolation(
                    constraint_name="prohibited_rating",
                    constraint_type="hard",
                    current_value=request.rating,
                    limit_value=f"not in {constraints.prohibited_ratings}",
                    description=f"Rating '{request.rating}' is prohibited",
                    is_blocking=True,
                ))

        # Counterparty concentration
        if request.counterparty_name and total_committed > 0:
            existing_counterparty_exposure = sum(
                d.allocated_amount for d in program.deployments
                if d.project_name and request.counterparty_name.lower() in d.project_name.lower()
            )
            new_exposure = existing_counterparty_exposure + request.requested_amount
            counterparty_pct = (new_exposure / total_committed) * Decimal("100")

            if counterparty_pct > constraints.max_single_counterparty_pct:
                violations.append(ConstraintViolation(
                    constraint_name="max_counterparty_exposure",
                    constraint_type="hard",
                    current_value=f"{counterparty_pct:.1f}%",
                    limit_value=f"{constraints.max_single_counterparty_pct}%",
                    description=f"Counterparty exposure would exceed limit ({counterparty_pct:.1f}%)",
                    is_blocking=True,
                ))

        # === SOFT CONSTRAINTS ===

        # Development exposure
        if request.is_development and total_committed > 0:
            current_dev_exposure = sum(
                d.allocated_amount for d in program.deployments
                # In a real system, we'd track this per-deployment
            )
            new_dev_pct = ((current_dev_exposure + request.requested_amount) / total_committed) * Decimal("100")
            if new_dev_pct > constraints.max_development_pct:
                violations.append(ConstraintViolation(
                    constraint_name="max_development_pct",
                    constraint_type="soft",
                    current_value=f"{new_dev_pct:.1f}%",
                    limit_value=f"{constraints.max_development_pct}%",
                    description=f"Development exposure would exceed target ({new_dev_pct:.1f}%)",
                    is_blocking=False,
                ))

        # First-time director exposure
        if request.is_first_time_director and total_committed > 0:
            current_ftd_exposure = Decimal("0")  # Would track per-deployment
            new_ftd_pct = ((current_ftd_exposure + request.requested_amount) / total_committed) * Decimal("100")
            if new_ftd_pct > constraints.max_first_time_director_pct:
                violations.append(ConstraintViolation(
                    constraint_name="max_first_time_director_pct",
                    constraint_type="soft",
                    current_value=f"{new_ftd_pct:.1f}%",
                    limit_value=f"{constraints.max_first_time_director_pct}%",
                    description=f"First-time director exposure would exceed target ({new_ftd_pct:.1f}%)",
                    is_blocking=False,
                ))

        # Reserve check
        available_after_reserve = program.deployable_capital
        if request.requested_amount > available_after_reserve:
            violations.append(ConstraintViolation(
                constraint_name="reserve_requirement",
                constraint_type="soft",
                current_value=str(available_after_reserve),
                limit_value=str(request.requested_amount),
                description=f"Allocation would dip into reserves (${available_after_reserve:,.0f} available after reserve)",
                is_blocking=False,
            ))

        return violations

    def _select_source(
        self,
        program: CapitalProgram,
        request: AllocationRequest
    ) -> Tuple[Optional[CapitalSource], Optional[str]]:
        """
        Select the best funding source within a program for an allocation.

        Selection criteria:
        1. If source_id specified, use that source
        2. Otherwise, select source with:
           - Sufficient available capital
           - Best match for project characteristics
           - Lowest cost of capital
        """
        # If specific source requested
        if request.source_id:
            for source in program.sources:
                if source.source_id == request.source_id:
                    if source.available_amount >= request.requested_amount:
                        return source, "Specified source has sufficient capacity"
                    else:
                        return None, f"Specified source {request.source_id} has insufficient capacity"
            return None, f"Specified source {request.source_id} not found"

        # Find eligible sources
        eligible_sources = []
        for source in program.sources:
            if source.available_amount < request.requested_amount:
                continue

            # Check source-specific restrictions
            if source.budget_range_min and request.project_budget < source.budget_range_min:
                continue
            if source.budget_range_max and request.project_budget > source.budget_range_max:
                continue

            if request.jurisdiction and source.geographic_restrictions:
                if request.jurisdiction not in source.geographic_restrictions:
                    continue

            if request.genre and source.genre_restrictions:
                if request.genre.lower() not in [g.lower() for g in source.genre_restrictions]:
                    continue

            eligible_sources.append(source)

        if not eligible_sources:
            return None, "No eligible source found"

        # Score sources (lower is better)
        def source_score(s: CapitalSource) -> Decimal:
            score = Decimal("0")
            # Prefer lower cost sources
            if s.interest_rate:
                score += s.interest_rate
            if s.management_fee_pct:
                score += s.management_fee_pct * Decimal("10")
            # Prefer sources with more available capital (for diversification)
            if s.available_amount > 0:
                utilization = s.drawn_amount / s.committed_amount if s.committed_amount > 0 else Decimal("0")
                score += utilization * Decimal("5")
            return score

        # Sort by score and return best
        eligible_sources.sort(key=source_score)
        best_source = eligible_sources[0]

        reason = f"Selected {best_source.source_name}: "
        if best_source.interest_rate:
            reason += f"{best_source.interest_rate}% cost, "
        reason += f"{best_source.utilization_rate:.0f}% utilized"

        return best_source, reason

    def _generate_recommendations(
        self,
        program: CapitalProgram,
        request: AllocationRequest,
        violations: List[ConstraintViolation]
    ) -> List[str]:
        """Generate recommendations based on allocation request and violations"""
        recommendations = []

        # Recommendations based on violations
        for v in violations:
            if v.constraint_name == "max_single_project_pct":
                recommendations.append(
                    f"Consider splitting the allocation across multiple tranches "
                    f"or reducing the amount to stay within {program.constraints.max_single_project_pct}% limit"
                )
            elif v.constraint_name == "source_availability":
                recommendations.append(
                    "Consider adding new capital sources or waiting for existing "
                    "deployments to recoup"
                )
            elif v.constraint_name == "reserve_requirement":
                recommendations.append(
                    f"Current allocation would use reserves. Consider increasing "
                    f"fund commitments or reducing allocation by "
                    f"${request.requested_amount - program.deployable_capital:,.0f}"
                )

        # General recommendations
        if program.deployment_rate > Decimal("80"):
            recommendations.append(
                f"Fund is {program.deployment_rate:.0f}% deployed. "
                "Consider reserving remaining capital for follow-on investments"
            )

        if len(program.deployments) > 0:
            avg_size = program.total_allocated / len(program.deployments)
            if request.requested_amount > avg_size * Decimal("2"):
                recommendations.append(
                    f"This allocation (${request.requested_amount:,.0f}) is significantly larger "
                    f"than average deployment (${avg_size:,.0f}). Ensure this aligns with "
                    "portfolio concentration strategy"
                )

        return recommendations

    def calculate_portfolio_metrics(self, program_id: str) -> Optional[PortfolioMetrics]:
        """
        Calculate comprehensive portfolio metrics for a program.

        Returns:
            PortfolioMetrics with size, concentration, performance, and risk metrics
        """
        program = self._programs.get(program_id)
        if not program:
            return None

        total_committed = program.total_committed
        deployments = program.deployments

        # Calculate concentration metrics
        largest_project_pct = Decimal("0")
        counterparty_exposure: Dict[str, Decimal] = {}

        for d in deployments:
            if total_committed > 0:
                pct = (d.allocated_amount / total_committed) * Decimal("100")
                if pct > largest_project_pct:
                    largest_project_pct = pct

            # Track counterparty (simplified - using project name)
            key = d.project_name.split("-")[0].strip() if d.project_name else "Unknown"
            counterparty_exposure[key] = counterparty_exposure.get(key, Decimal("0")) + d.allocated_amount

        largest_counterparty_pct = Decimal("0")
        if counterparty_exposure and total_committed > 0:
            largest_counterparty_pct = (max(counterparty_exposure.values()) / total_committed) * Decimal("100")

        # Calculate HHI (Herfindahl-Hirschman Index)
        hhi = Decimal("0")
        if deployments and total_committed > 0:
            for d in deployments:
                share = d.allocated_amount / total_committed
                hhi += share * share * Decimal("10000")

        # Calculate performance metrics
        total_allocated = program.total_allocated
        num_projects = len(set(d.project_id for d in deployments))
        active_statuses = {AllocationStatus.APPROVED, AllocationStatus.COMMITTED, AllocationStatus.FUNDED}
        num_active = len([d for d in deployments if d.status in active_statuses])

        avg_project_size = total_allocated / num_projects if num_projects > 0 else None

        total_funded = program.total_funded
        total_recouped = program.total_recouped
        total_profit = program.total_profit
        portfolio_multiple = program.portfolio_multiple

        # Constraint compliance
        hard_satisfied = True
        soft_met = 0
        soft_total = 0

        constraints = program.constraints

        # Check hard constraints
        if largest_project_pct > constraints.max_single_project_pct:
            hard_satisfied = False
        if largest_counterparty_pct > constraints.max_single_counterparty_pct:
            hard_satisfied = False

        # Check soft constraints
        if constraints.target_num_projects:
            soft_total += 1
            if num_projects >= constraints.target_num_projects:
                soft_met += 1

        if constraints.target_multiple and portfolio_multiple:
            soft_total += 1
            if portfolio_multiple >= constraints.target_multiple:
                soft_met += 1

        return PortfolioMetrics(
            total_committed=total_committed,
            total_deployed=total_allocated,
            total_available=program.total_available,
            deployment_rate=program.deployment_rate,
            num_projects=num_projects,
            num_active_projects=num_active,
            avg_project_size=avg_project_size,
            largest_project_pct=largest_project_pct,
            largest_counterparty_pct=largest_counterparty_pct,
            hhi_concentration=hhi,
            total_recouped=total_recouped,
            total_profit=total_profit,
            portfolio_multiple=portfolio_multiple,
            weighted_irr=None,  # Would require more complex calculation
            development_exposure_pct=Decimal("0"),  # Would need per-deployment tracking
            first_time_director_pct=Decimal("0"),  # Would need per-deployment tracking
            hard_constraints_satisfied=hard_satisfied,
            soft_constraints_met=soft_met,
            soft_constraints_total=soft_total,
        )

    def fund_deployment(
        self,
        program_id: str,
        deployment_id: str,
        amount: Optional[Decimal] = None
    ) -> bool:
        """
        Mark a deployment as funded (capital actually transferred).

        Args:
            program_id: Program containing the deployment
            deployment_id: Deployment to fund
            amount: Amount to fund (defaults to full allocated amount)

        Returns:
            True if funding was successful
        """
        program = self._programs.get(program_id)
        if not program:
            return False

        for deployment in program.deployments:
            if deployment.deployment_id == deployment_id:
                fund_amount = amount or deployment.allocated_amount
                deployment.funded_amount = min(
                    deployment.funded_amount + fund_amount,
                    deployment.allocated_amount
                )
                deployment.status = AllocationStatus.FUNDED
                deployment.funding_date = date.today()
                logger.info(f"Funded deployment {deployment_id}: ${fund_amount:,.0f}")
                return True

        return False

    def record_recoupment(
        self,
        program_id: str,
        deployment_id: str,
        recouped_amount: Decimal,
        profit_amount: Decimal = Decimal("0")
    ) -> bool:
        """
        Record recoupment and profit from a project.

        Args:
            program_id: Program containing the deployment
            deployment_id: Deployment receiving funds
            recouped_amount: Principal amount recouped
            profit_amount: Profit amount distributed

        Returns:
            True if recording was successful
        """
        program = self._programs.get(program_id)
        if not program:
            return False

        for deployment in program.deployments:
            if deployment.deployment_id == deployment_id:
                deployment.recouped_amount += recouped_amount
                deployment.profit_distributed += profit_amount

                # Update status if fully recouped
                if deployment.recouped_amount >= deployment.funded_amount:
                    deployment.status = AllocationStatus.RECOUPED

                logger.info(
                    f"Recorded recoupment for {deployment_id}: "
                    f"${recouped_amount:,.0f} principal, ${profit_amount:,.0f} profit"
                )
                return True

        return False

    def get_deployment_summary(self, program_id: str) -> List[Dict[str, Any]]:
        """Get summary of all deployments for a program"""
        program = self._programs.get(program_id)
        if not program:
            return []

        return [d.to_dict() for d in program.deployments]

    def optimize_allocation(
        self,
        program_id: str,
        projects: List[AllocationRequest],
        max_total_allocation: Optional[Decimal] = None
    ) -> List[AllocationResult]:
        """
        Optimize allocation across multiple projects.

        Uses a greedy approach to maximize deployment while respecting constraints.

        Args:
            program_id: Program to allocate from
            projects: List of potential projects
            max_total_allocation: Optional cap on total allocation

        Returns:
            List of AllocationResults for each project
        """
        program = self._programs.get(program_id)
        if not program:
            return []

        results = []
        remaining_capital = max_total_allocation or program.deployable_capital

        # Sort projects by some criteria (could be made configurable)
        # For now, sort by requested amount (smaller first for diversification)
        sorted_projects = sorted(projects, key=lambda p: p.requested_amount)

        for project in sorted_projects:
            if project.requested_amount > remaining_capital:
                # Try partial allocation
                project.requested_amount = remaining_capital

            if project.requested_amount <= 0:
                continue

            result = self.allocate_capital(project, dry_run=False)
            results.append(result)

            if result.success:
                remaining_capital -= project.requested_amount

        return results
