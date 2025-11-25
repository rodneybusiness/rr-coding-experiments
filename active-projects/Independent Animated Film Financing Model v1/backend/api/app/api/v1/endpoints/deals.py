"""
DealBlock API Endpoints

CRUD operations and analysis for DealBlocks.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict
from decimal import Decimal
import uuid

from app.schemas.deals import (
    DealBlockInput,
    DealBlockResponse,
    DealBlockListResponse,
    DealBlockCreateRequest,
    DealBlockAnalysisRequest,
    DealBlockAnalysisResponse,
    DealTemplateResponse,
    DealTemplatesListResponse,
)

# Import models (path setup done in api.py)
from models.deal_block import (
    DealBlock,
    DealType,
    DealStatus,
    ApprovalRight,
    RightsWindow,
    create_equity_investment_template,
    create_presale_template,
    create_streamer_license_template,
    create_streamer_original_template,
    create_gap_financing_template,
)

router = APIRouter()

# In-memory storage (replace with database in production)
_deal_storage: Dict[str, DealBlock] = {}


def _input_to_deal_block(deal_id: str, input: DealBlockInput) -> DealBlock:
    """Convert API input to DealBlock model"""
    return DealBlock(
        deal_id=deal_id,
        deal_name=input.deal_name,
        deal_type=DealType(input.deal_type),
        status=DealStatus(input.status),
        counterparty_name=input.counterparty_name,
        counterparty_type=input.counterparty_type,
        amount=input.amount,
        currency=input.currency,
        payment_schedule=input.payment_schedule or {},
        recoupment_priority=input.recoupment_priority,
        is_recoupable=input.is_recoupable,
        interest_rate=input.interest_rate,
        premium_percentage=input.premium_percentage,
        backend_participation_pct=input.backend_participation_pct,
        origination_fee_pct=input.origination_fee_pct,
        distribution_fee_pct=input.distribution_fee_pct,
        sales_commission_pct=input.sales_commission_pct,
        territories=input.territories,
        is_worldwide=input.is_worldwide,
        rights_windows=[RightsWindow(w) for w in input.rights_windows] if input.rights_windows else [],
        term_years=input.term_years,
        exclusivity=input.exclusivity,
        holdback_days=input.holdback_days,
        ownership_percentage=input.ownership_percentage,
        approval_rights_granted=[ApprovalRight(a) for a in input.approval_rights_granted] if input.approval_rights_granted else [],
        has_board_seat=input.has_board_seat,
        has_veto_rights=input.has_veto_rights,
        veto_scope=input.veto_scope,
        ip_ownership=input.ip_ownership,
        mfn_clause=input.mfn_clause,
        mfn_scope=input.mfn_scope,
        reversion_trigger_years=input.reversion_trigger_years,
        reversion_trigger_condition=input.reversion_trigger_condition,
        sequel_rights_holder=input.sequel_rights_holder,
        sequel_participation_pct=input.sequel_participation_pct,
        cross_collateralized=input.cross_collateralized,
        cross_collateral_scope=input.cross_collateral_scope,
        probability_of_closing=input.probability_of_closing,
        complexity_score=input.complexity_score,
        expected_close_date=input.expected_close_date,
        notes=input.notes,
    )


def _deal_block_to_response(deal: DealBlock) -> DealBlockResponse:
    """Convert DealBlock model to API response"""
    return DealBlockResponse(
        deal_id=deal.deal_id,
        deal_name=deal.deal_name,
        deal_type=deal.deal_type.value,
        status=deal.status.value,
        counterparty_name=deal.counterparty_name,
        counterparty_type=deal.counterparty_type,
        amount=deal.amount,
        currency=deal.currency,
        payment_schedule=deal.payment_schedule,
        recoupment_priority=deal.recoupment_priority,
        is_recoupable=deal.is_recoupable,
        interest_rate=deal.interest_rate,
        premium_percentage=deal.premium_percentage,
        backend_participation_pct=deal.backend_participation_pct,
        origination_fee_pct=deal.origination_fee_pct,
        distribution_fee_pct=deal.distribution_fee_pct,
        sales_commission_pct=deal.sales_commission_pct,
        territories=deal.territories,
        is_worldwide=deal.is_worldwide,
        rights_windows=[w.value for w in deal.rights_windows],
        term_years=deal.term_years,
        exclusivity=deal.exclusivity,
        holdback_days=deal.holdback_days,
        ownership_percentage=deal.ownership_percentage,
        approval_rights_granted=[a.value for a in deal.approval_rights_granted],
        has_board_seat=deal.has_board_seat,
        has_veto_rights=deal.has_veto_rights,
        veto_scope=deal.veto_scope,
        ip_ownership=deal.ip_ownership,
        mfn_clause=deal.mfn_clause,
        mfn_scope=deal.mfn_scope,
        reversion_trigger_years=deal.reversion_trigger_years,
        reversion_trigger_condition=deal.reversion_trigger_condition,
        sequel_rights_holder=deal.sequel_rights_holder,
        sequel_participation_pct=deal.sequel_participation_pct,
        cross_collateralized=deal.cross_collateralized,
        cross_collateral_scope=deal.cross_collateral_scope,
        probability_of_closing=deal.probability_of_closing,
        complexity_score=deal.complexity_score,
        created_date=deal.created_date,
        expected_close_date=deal.expected_close_date,
        notes=deal.notes,
        # Computed
        net_amount=deal.net_amount_after_fees(),
        expected_value=deal.expected_value(),
        control_impact_score=deal.control_impact_score(),
        ownership_impact_score=deal.ownership_impact_score(),
        optionality_score=deal.optionality_score(),
    )


@router.post(
    "/",
    response_model=DealBlockResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create DealBlock",
    description="Create a new DealBlock for a project",
)
async def create_deal(request: DealBlockCreateRequest):
    """
    Create a new DealBlock.

    Returns the created DealBlock with computed scores.
    """
    try:
        deal_id = f"DEAL-{uuid.uuid4().hex[:8].upper()}"
        deal = _input_to_deal_block(deal_id, request.deal)

        # Store in memory
        _deal_storage[deal_id] = deal

        return _deal_block_to_response(deal)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deal: {str(e)}",
        )


@router.get(
    "/{deal_id}",
    response_model=DealBlockResponse,
    summary="Get DealBlock",
    description="Retrieve a DealBlock by ID",
)
async def get_deal(deal_id: str):
    """Get a DealBlock by ID"""
    if deal_id not in _deal_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_id} not found",
        )

    return _deal_block_to_response(_deal_storage[deal_id])


@router.put(
    "/{deal_id}",
    response_model=DealBlockResponse,
    summary="Update DealBlock",
    description="Update an existing DealBlock",
)
async def update_deal(deal_id: str, input: DealBlockInput):
    """Update an existing DealBlock"""
    if deal_id not in _deal_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_id} not found",
        )

    try:
        deal = _input_to_deal_block(deal_id, input)
        _deal_storage[deal_id] = deal
        return _deal_block_to_response(deal)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{deal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete DealBlock",
    description="Delete a DealBlock by ID",
)
async def delete_deal(deal_id: str):
    """Delete a DealBlock"""
    if deal_id not in _deal_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_id} not found",
        )

    del _deal_storage[deal_id]


@router.get(
    "/",
    response_model=DealBlockListResponse,
    summary="List DealBlocks",
    description="List all DealBlocks with optional filtering",
)
async def list_deals(
    deal_type: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
):
    """List DealBlocks with optional filtering"""
    deals = list(_deal_storage.values())

    # Filter by type
    if deal_type:
        deals = [d for d in deals if d.deal_type.value == deal_type]

    # Filter by status
    if status:
        deals = [d for d in deals if d.status.value == status]

    # Pagination
    total = len(deals)
    deals = deals[offset : offset + limit]

    return DealBlockListResponse(
        deals=[_deal_block_to_response(d) for d in deals],
        total_count=total,
    )


@router.post(
    "/analyze",
    response_model=DealBlockAnalysisResponse,
    summary="Analyze DealBlocks",
    description="Analyze a set of DealBlocks for aggregate metrics and risks",
)
async def analyze_deals(request: DealBlockAnalysisRequest):
    """
    Analyze a set of DealBlocks.

    Returns aggregate metrics, risk flags, and individual summaries.
    """
    try:
        # Convert inputs to DealBlocks
        deals = []
        for i, input in enumerate(request.deal_blocks):
            deal_id = f"TEMP-{i:03d}"
            deal = _input_to_deal_block(deal_id, input)
            deals.append(deal)

        # Calculate aggregates
        total_value = sum(d.amount for d in deals)
        total_expected = sum(d.expected_value() for d in deals)

        control_impacts = [d.control_impact_score() for d in deals]
        ownership_impacts = [d.ownership_impact_score() for d in deals]
        optionality_scores = [d.optionality_score() for d in deals]

        avg_control = Decimal(str(sum(control_impacts) / len(control_impacts)))
        avg_ownership = Decimal(str(sum(ownership_impacts) / len(ownership_impacts)))
        avg_optionality = Decimal(str(sum(optionality_scores) / len(optionality_scores)))
        total_complexity = sum(d.complexity_score for d in deals)

        # Risk flags
        has_mfn = any(d.mfn_clause for d in deals)
        has_worldwide = any(d.is_worldwide for d in deals)
        has_ip_transfer = any(d.ip_ownership == "counterparty" for d in deals)

        # Breakdown by type
        deals_by_type: Dict[str, int] = {}
        value_by_type: Dict[str, Decimal] = {}
        for d in deals:
            dtype = d.deal_type.value
            deals_by_type[dtype] = deals_by_type.get(dtype, 0) + 1
            value_by_type[dtype] = value_by_type.get(dtype, Decimal("0")) + d.amount

        # Individual summaries
        summaries = [
            {
                "deal_name": d.deal_name,
                "deal_type": d.deal_type.value,
                "amount": str(d.amount),
                "expected_value": str(d.expected_value()),
                "control_impact": d.control_impact_score(),
                "ownership_impact": d.ownership_impact_score(),
                "optionality": d.optionality_score(),
                "key_risks": _identify_risks(d),
            }
            for d in deals
        ]

        return DealBlockAnalysisResponse(
            project_id=request.project_id,
            total_deal_value=total_value,
            total_expected_value=total_expected,
            deal_count=len(deals),
            average_control_impact=avg_control,
            average_ownership_impact=avg_ownership,
            average_optionality=avg_optionality,
            total_complexity=total_complexity,
            has_mfn_deals=has_mfn,
            has_worldwide_rights_deals=has_worldwide,
            has_ip_transfer_deals=has_ip_transfer,
            deals_by_type=deals_by_type,
            value_by_type=value_by_type,
            deal_summaries=summaries,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.get(
    "/templates",
    response_model=DealTemplatesListResponse,
    summary="Get Deal Templates",
    description="Get available DealBlock templates",
)
async def get_templates():
    """Get available DealBlock templates"""
    templates = [
        DealTemplateResponse(
            template_name="Equity Investment",
            deal_type="equity_investment",
            description="Standard equity investment with ownership, premium, and potential board seat",
            default_values={
                "ownership_percentage": "25",
                "premium_percentage": "20",
                "has_board_seat": True,
                "recoupment_priority": 8,
            },
        ),
        DealTemplateResponse(
            template_name="Pre-Sale / MG",
            deal_type="presale_mg",
            description="Territory pre-sale with minimum guarantee and overage participation",
            default_values={
                "sales_commission_pct": "15",
                "backend_participation_pct": "50",
                "term_years": 15,
                "recoupment_priority": 6,
            },
        ),
        DealTemplateResponse(
            template_name="Streamer License",
            deal_type="streamer_license",
            description="SVOD license deal with fixed fee and limited rights",
            default_values={
                "term_years": 7,
                "holdback_days": 120,
                "is_recoupable": False,
                "recoupment_priority": 1,
            },
        ),
        DealTemplateResponse(
            template_name="Streamer Original",
            deal_type="streamer_original",
            description="Cost-plus buyout with full creative control to platform",
            default_values={
                "premium_percentage": "15",
                "is_worldwide": True,
                "term_years": 25,
                "ip_ownership": "counterparty",
                "sequel_rights_holder": "counterparty",
            },
        ),
        DealTemplateResponse(
            template_name="Gap Financing",
            deal_type="gap_financing",
            description="Gap loan against unsold territory value",
            default_values={
                "interest_rate": "12",
                "origination_fee_pct": "3",
                "recoupment_priority": 5,
            },
        ),
        DealTemplateResponse(
            template_name="Theatrical Distribution",
            deal_type="theatrical_distribution",
            description="Theatrical distribution deal with P&A commitment",
            default_values={
                "distribution_fee_pct": "30",
                "term_years": 15,
                "recoupment_priority": 1,
            },
        ),
    ]

    return DealTemplatesListResponse(templates=templates)


def _identify_risks(deal: DealBlock) -> List[str]:
    """Identify key risks for a deal"""
    risks = []

    if deal.mfn_clause:
        risks.append("MFN clause limits future deal flexibility")

    if deal.ip_ownership == "counterparty":
        risks.append("IP ownership transferred to counterparty")

    if deal.is_worldwide and deal.term_years and deal.term_years > 15:
        risks.append("Long-term worldwide rights encumbrance")

    if deal.sequel_rights_holder and deal.sequel_rights_holder != "producer":
        risks.append("Sequel rights not retained")

    if deal.cross_collateralized:
        risks.append("Cross-collateralization risk")

    if ApprovalRight.FINAL_CUT in deal.approval_rights_granted:
        risks.append("Final cut approval ceded")

    if deal.has_veto_rights:
        risks.append("Counterparty has veto rights")

    if not risks:
        risks.append("No significant risks identified")

    return risks
