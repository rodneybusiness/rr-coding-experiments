"""
Capital Program API Endpoints

CRUD operations and management for Capital Programs.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional
from decimal import Decimal
import uuid

from app.schemas.capital_programs import (
    CapitalSourceInput,
    CapitalProgramConstraintsInput,
    CapitalProgramInput,
    AllocationRequestInput,
    FundingRequest,
    RecoupmentRequest,
    CapitalSourceResponse,
    CapitalDeploymentResponse,
    CapitalProgramMetrics,
    CapitalProgramResponse,
    CapitalProgramListResponse,
    ConstraintViolationResponse,
    AllocationResultResponse,
    PortfolioMetricsResponse,
    ProgramTypesResponse,
    AllocationValidationRequest,
    BatchAllocationRequest,
    BatchAllocationResponse,
)

# Import models and engine (path setup done in api.py)
from models.capital_program import (
    CapitalProgram,
    CapitalSource,
    CapitalDeployment,
    CapitalProgramConstraints,
    ProgramType,
    ProgramStatus,
    AllocationStatus,
)

from engines.capital_programs import (
    AllocationRequest,
    AllocationResult,
    CapitalProgramManager,
)

router = APIRouter()

# Global manager instance
_manager = CapitalProgramManager()


def _source_input_to_model(source_id: str, input: CapitalSourceInput) -> CapitalSource:
    """Convert API input to CapitalSource model"""
    return CapitalSource(
        source_id=source_id,
        source_name=input.source_name,
        source_type=input.source_type,
        committed_amount=input.committed_amount,
        drawn_amount=input.drawn_amount,
        currency=input.currency,
        interest_rate=input.interest_rate,
        management_fee_pct=input.management_fee_pct,
        carry_percentage=input.carry_percentage,
        hurdle_rate=input.hurdle_rate,
        geographic_restrictions=input.geographic_restrictions,
        genre_restrictions=input.genre_restrictions,
        budget_range_min=input.budget_range_min,
        budget_range_max=input.budget_range_max,
        commitment_date=input.commitment_date,
        expiry_date=input.expiry_date,
        notes=input.notes,
    )


def _constraints_input_to_model(
    input: Optional[CapitalProgramConstraintsInput]
) -> CapitalProgramConstraints:
    """Convert API input to CapitalProgramConstraints model"""
    if not input:
        return CapitalProgramConstraints()

    return CapitalProgramConstraints(
        max_single_project_pct=input.max_single_project_pct,
        max_single_counterparty_pct=input.max_single_counterparty_pct,
        min_project_budget=input.min_project_budget,
        max_project_budget=input.max_project_budget,
        required_jurisdictions=input.required_jurisdictions,
        prohibited_jurisdictions=input.prohibited_jurisdictions,
        required_genres=input.required_genres,
        prohibited_genres=input.prohibited_genres,
        prohibited_ratings=input.prohibited_ratings,
        target_num_projects=input.target_num_projects,
        target_avg_budget=input.target_avg_budget,
        target_portfolio_irr=input.target_portfolio_irr,
        target_multiple=input.target_multiple,
        max_development_pct=input.max_development_pct,
        max_first_time_director_pct=input.max_first_time_director_pct,
        target_deployment_years=input.target_deployment_years,
        min_reserve_pct=input.min_reserve_pct,
    )


def _program_input_to_model(program_id: str, input: CapitalProgramInput) -> CapitalProgram:
    """Convert API input to CapitalProgram model"""
    sources = []
    for i, source_input in enumerate(input.sources):
        source_id = f"{program_id}_SRC{i+1:02d}"
        sources.append(_source_input_to_model(source_id, source_input))

    return CapitalProgram(
        program_id=program_id,
        program_name=input.program_name,
        program_type=ProgramType(input.program_type),
        status=ProgramStatus.PROSPECTIVE,
        description=input.description,
        target_size=input.target_size,
        currency=input.currency,
        sources=sources,
        constraints=_constraints_input_to_model(input.constraints),
        manager_name=input.manager_name,
        management_fee_pct=input.management_fee_pct,
        carry_percentage=input.carry_percentage,
        hurdle_rate=input.hurdle_rate,
        vintage_year=input.vintage_year,
        investment_period_years=input.investment_period_years,
        fund_term_years=input.fund_term_years,
        extension_years=input.extension_years,
        formation_date=input.formation_date,
        first_close_date=input.first_close_date,
        final_close_date=input.final_close_date,
        notes=input.notes,
    )


def _source_to_response(source: CapitalSource) -> CapitalSourceResponse:
    """Convert CapitalSource model to API response"""
    return CapitalSourceResponse(
        source_id=source.source_id,
        source_name=source.source_name,
        source_type=source.source_type,
        committed_amount=source.committed_amount,
        drawn_amount=source.drawn_amount,
        available_amount=source.available_amount,
        utilization_rate=source.utilization_rate,
        currency=source.currency,
        interest_rate=source.interest_rate,
        management_fee_pct=source.management_fee_pct,
        carry_percentage=source.carry_percentage,
        hurdle_rate=source.hurdle_rate,
        geographic_restrictions=source.geographic_restrictions,
        genre_restrictions=source.genre_restrictions,
        budget_range_min=source.budget_range_min,
        budget_range_max=source.budget_range_max,
        commitment_date=source.commitment_date,
        expiry_date=source.expiry_date,
        notes=source.notes,
    )


def _deployment_to_response(deployment: CapitalDeployment) -> CapitalDeploymentResponse:
    """Convert CapitalDeployment model to API response"""
    return CapitalDeploymentResponse(
        deployment_id=deployment.deployment_id,
        program_id=deployment.program_id,
        source_id=deployment.source_id,
        project_id=deployment.project_id,
        project_name=deployment.project_name,
        allocated_amount=deployment.allocated_amount,
        funded_amount=deployment.funded_amount,
        recouped_amount=deployment.recouped_amount,
        profit_distributed=deployment.profit_distributed,
        outstanding_amount=deployment.outstanding_amount,
        total_return=deployment.total_return,
        multiple=deployment.multiple,
        currency=deployment.currency,
        status=deployment.status.value,
        equity_percentage=deployment.equity_percentage,
        recoupment_priority=deployment.recoupment_priority,
        backend_participation_pct=deployment.backend_participation_pct,
        allocation_date=deployment.allocation_date,
        funding_date=deployment.funding_date,
        expected_recoupment_date=deployment.expected_recoupment_date,
        notes=deployment.notes,
    )


def _program_to_response(program: CapitalProgram) -> CapitalProgramResponse:
    """Convert CapitalProgram model to API response"""
    return CapitalProgramResponse(
        program_id=program.program_id,
        program_name=program.program_name,
        program_type=program.program_type.value,
        status=program.status.value,
        description=program.description,
        target_size=program.target_size,
        currency=program.currency,
        sources=[_source_to_response(s) for s in program.sources],
        deployments=[_deployment_to_response(d) for d in program.deployments],
        constraints=program.constraints.to_dict(),
        manager_name=program.manager_name,
        management_fee_pct=program.management_fee_pct,
        carry_percentage=program.carry_percentage,
        hurdle_rate=program.hurdle_rate,
        vintage_year=program.vintage_year,
        investment_period_years=program.investment_period_years,
        fund_term_years=program.fund_term_years,
        extension_years=program.extension_years,
        formation_date=program.formation_date,
        first_close_date=program.first_close_date,
        final_close_date=program.final_close_date,
        notes=program.notes,
        metrics=CapitalProgramMetrics(
            total_committed=program.total_committed,
            total_drawn=program.total_drawn,
            total_available=program.total_available,
            total_allocated=program.total_allocated,
            total_funded=program.total_funded,
            total_recouped=program.total_recouped,
            total_profit=program.total_profit,
            commitment_progress=program.commitment_progress,
            deployment_rate=program.deployment_rate,
            num_active_projects=program.num_active_projects,
            portfolio_multiple=program.portfolio_multiple,
            reserve_amount=program.reserve_amount,
            deployable_capital=program.deployable_capital,
        ),
    )


def _allocation_result_to_response(result: AllocationResult) -> AllocationResultResponse:
    """Convert AllocationResult to API response"""
    return AllocationResultResponse(
        success=result.success,
        allocation_id=result.allocation_id,
        deployment=_deployment_to_response(result.deployment) if result.deployment else None,
        violations=[
            ConstraintViolationResponse(
                constraint_name=v.constraint_name,
                constraint_type=v.constraint_type,
                current_value=v.current_value,
                limit_value=v.limit_value,
                description=v.description,
                is_blocking=v.is_blocking,
            )
            for v in result.violations
        ],
        warnings=result.warnings,
        selected_source_id=result.selected_source_id,
        source_selection_reason=result.source_selection_reason,
        recommendations=result.recommendations,
    )


# === PROGRAM ENDPOINTS ===

@router.post(
    "/",
    response_model=CapitalProgramResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Capital Program",
    description="Create a new capital program",
)
async def create_program(request: CapitalProgramInput):
    """Create a new capital program"""
    try:
        program_id = f"PROG-{uuid.uuid4().hex[:8].upper()}"
        program = _program_input_to_model(program_id, request)

        _manager.register_program(program)

        return _program_to_response(program)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create program: {str(e)}",
        )


@router.get(
    "/",
    response_model=CapitalProgramListResponse,
    summary="List Capital Programs",
    description="List all capital programs",
)
async def list_programs(
    program_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """List capital programs with optional filtering"""
    programs = _manager.list_programs()

    # Filter by type
    if program_type:
        programs = [p for p in programs if p.program_type.value == program_type]

    # Filter by status
    if status:
        programs = [p for p in programs if p.status.value == status]

    # Pagination
    total = len(programs)
    programs = programs[offset : offset + limit]

    return CapitalProgramListResponse(
        programs=[_program_to_response(p) for p in programs],
        total_count=total,
    )


@router.get(
    "/types",
    response_model=ProgramTypesResponse,
    summary="List Program Types",
    description="List all available program types",
)
async def list_program_types():
    """Get available program types"""
    types = [
        {"value": t.value, "label": t.value.replace("_", " ").title()}
        for t in ProgramType
    ]
    return ProgramTypesResponse(types=types)


@router.get(
    "/{program_id}",
    response_model=CapitalProgramResponse,
    summary="Get Capital Program",
    description="Get a capital program by ID",
)
async def get_program(program_id: str):
    """Get a capital program by ID"""
    program = _manager.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )

    return _program_to_response(program)


@router.put(
    "/{program_id}/status",
    response_model=CapitalProgramResponse,
    summary="Update Program Status",
    description="Update a program's status",
)
async def update_program_status(program_id: str, new_status: str):
    """Update program status"""
    program = _manager.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )

    try:
        program.status = ProgramStatus(new_status)
        return _program_to_response(program)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}",
        )


# === SOURCE ENDPOINTS ===

@router.post(
    "/{program_id}/sources",
    response_model=CapitalSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Capital Source",
    description="Add a new capital source to a program",
)
async def add_source(program_id: str, source_input: CapitalSourceInput):
    """Add a capital source to a program"""
    program = _manager.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )

    source_id = f"{program_id}_SRC{len(program.sources)+1:02d}"
    source = _source_input_to_model(source_id, source_input)
    program.sources.append(source)

    return _source_to_response(source)


@router.get(
    "/{program_id}/sources",
    response_model=List[CapitalSourceResponse],
    summary="List Capital Sources",
    description="List all sources for a program",
)
async def list_sources(program_id: str):
    """List sources for a program"""
    program = _manager.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )

    return [_source_to_response(s) for s in program.sources]


@router.delete(
    "/{program_id}/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Capital Source",
    description="Remove a capital source from a program",
)
async def remove_source(program_id: str, source_id: str):
    """Remove a capital source from a program"""
    program = _manager.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )

    # Find the source to remove
    source_to_remove = None
    for i, source in enumerate(program.sources):
        if source.source_id == source_id:
            source_to_remove = i
            break

    if source_to_remove is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found in program {program_id}",
        )

    # Check if source has any active deployments (drawn > 0)
    if program.sources[source_to_remove].drawn_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot remove source {source_id} - it has active deployments. "
                   f"Drawn amount: {program.sources[source_to_remove].drawn_amount}",
        )

    # Remove the source
    program.sources.pop(source_to_remove)
    return None


# === ALLOCATION ENDPOINTS ===

@router.post(
    "/{program_id}/allocate",
    response_model=AllocationResultResponse,
    summary="Allocate Capital",
    description="Allocate capital from a program to a project",
)
async def allocate_capital(program_id: str, allocation: AllocationRequestInput):
    """Allocate capital from a program to a project"""
    request = AllocationRequest(
        program_id=program_id,
        project_id=allocation.project_id,
        project_name=allocation.project_name,
        requested_amount=allocation.requested_amount,
        project_budget=allocation.project_budget,
        jurisdiction=allocation.jurisdiction,
        genre=allocation.genre,
        rating=allocation.rating,
        is_development=allocation.is_development,
        is_first_time_director=allocation.is_first_time_director,
        counterparty_name=allocation.counterparty_name,
        equity_percentage=allocation.equity_percentage,
        recoupment_priority=allocation.recoupment_priority,
        backend_participation_pct=allocation.backend_participation_pct,
        source_id=allocation.source_id,
    )

    result = _manager.allocate_capital(request, dry_run=False)
    return _allocation_result_to_response(result)


@router.post(
    "/{program_id}/validate-allocation",
    response_model=AllocationResultResponse,
    summary="Validate Allocation",
    description="Validate an allocation without executing it",
)
async def validate_allocation(program_id: str, allocation: AllocationRequestInput):
    """Validate an allocation without executing"""
    request = AllocationRequest(
        program_id=program_id,
        project_id=allocation.project_id,
        project_name=allocation.project_name,
        requested_amount=allocation.requested_amount,
        project_budget=allocation.project_budget,
        jurisdiction=allocation.jurisdiction,
        genre=allocation.genre,
        rating=allocation.rating,
        is_development=allocation.is_development,
        is_first_time_director=allocation.is_first_time_director,
        counterparty_name=allocation.counterparty_name,
        equity_percentage=allocation.equity_percentage,
        recoupment_priority=allocation.recoupment_priority,
        backend_participation_pct=allocation.backend_participation_pct,
        source_id=allocation.source_id,
    )

    result = _manager.allocate_capital(request, dry_run=True)
    return _allocation_result_to_response(result)


@router.post(
    "/{program_id}/batch-allocate",
    response_model=BatchAllocationResponse,
    summary="Batch Allocate",
    description="Allocate capital to multiple projects optimally",
)
async def batch_allocate(program_id: str, request: BatchAllocationRequest):
    """Allocate capital to multiple projects"""
    allocation_requests = [
        AllocationRequest(
            program_id=program_id,
            project_id=a.project_id,
            project_name=a.project_name,
            requested_amount=a.requested_amount,
            project_budget=a.project_budget,
            jurisdiction=a.jurisdiction,
            genre=a.genre,
            rating=a.rating,
            is_development=a.is_development,
            is_first_time_director=a.is_first_time_director,
            counterparty_name=a.counterparty_name,
            equity_percentage=a.equity_percentage,
            recoupment_priority=a.recoupment_priority,
            backend_participation_pct=a.backend_participation_pct,
            source_id=a.source_id,
        )
        for a in request.allocations
    ]

    results = _manager.optimize_allocation(
        program_id,
        allocation_requests,
        request.max_total_allocation,
    )

    total_allocated = sum(
        r.deployment.allocated_amount for r in results if r.success and r.deployment
    )
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    return BatchAllocationResponse(
        results=[_allocation_result_to_response(r) for r in results],
        total_allocated=total_allocated,
        successful_count=successful,
        failed_count=failed,
    )


# === DEPLOYMENT ENDPOINTS ===

@router.get(
    "/{program_id}/deployments",
    response_model=List[CapitalDeploymentResponse],
    summary="List Deployments",
    description="List all deployments for a program",
)
async def list_deployments(program_id: str):
    """List all deployments for a program"""
    program = _manager.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )

    return [_deployment_to_response(d) for d in program.deployments]


@router.post(
    "/{program_id}/deployments/{deployment_id}/fund",
    response_model=CapitalDeploymentResponse,
    summary="Fund Deployment",
    description="Mark a deployment as funded",
)
async def fund_deployment(
    program_id: str,
    deployment_id: str,
    request: Optional[FundingRequest] = None,
):
    """Fund a deployment"""
    amount = request.amount if request else None

    success = _manager.fund_deployment(program_id, deployment_id, amount)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found in program {program_id}",
        )

    program = _manager.get_program(program_id)
    for d in program.deployments:
        if d.deployment_id == deployment_id:
            return _deployment_to_response(d)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to retrieve funded deployment",
    )


@router.post(
    "/{program_id}/deployments/{deployment_id}/recoup",
    response_model=CapitalDeploymentResponse,
    summary="Record Recoupment",
    description="Record recoupment from a project",
)
async def record_recoupment(
    program_id: str,
    deployment_id: str,
    request: RecoupmentRequest,
):
    """Record recoupment from a project"""
    success = _manager.record_recoupment(
        program_id,
        deployment_id,
        request.recouped_amount,
        request.profit_amount,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found in program {program_id}",
        )

    program = _manager.get_program(program_id)
    for d in program.deployments:
        if d.deployment_id == deployment_id:
            return _deployment_to_response(d)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to retrieve deployment",
    )


# === METRICS ENDPOINTS ===

@router.get(
    "/{program_id}/metrics",
    response_model=PortfolioMetricsResponse,
    summary="Get Portfolio Metrics",
    description="Get detailed portfolio metrics for a program",
)
async def get_portfolio_metrics(program_id: str):
    """Get portfolio metrics for a program"""
    metrics = _manager.calculate_portfolio_metrics(program_id)
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )

    return PortfolioMetricsResponse(**metrics.to_dict())
