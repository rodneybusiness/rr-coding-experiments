"""
Ownership & Control Scorer API Endpoints

Provides scoring functionality for deal blocks based on ownership,
control, optionality, and execution friction dimensions.
"""

from decimal import Decimal
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException

from app.schemas.ownership import (
    OwnershipScoreRequest,
    OwnershipScoreResponse,
    ScoreDealBlockInput,
    ScoreWeights,
    ControlImpactResponse,
    ScoringFlagsResponse,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
)

# Import models and engine (path setup done in api.py)
from models.deal_block import (
    DealBlock,
    DealType,
    ApprovalRight,
    RightsWindow,
)

from engines.scenario_optimizer.ownership_control_scorer import (
    OwnershipControlScorer,
    OwnershipControlResult,
)

router = APIRouter()


def _convert_input_to_deal_block(input_deal: ScoreDealBlockInput) -> DealBlock:
    """Convert API input schema to DealBlock model"""
    # Convert deal type string to enum
    try:
        deal_type = DealType(input_deal.deal_type)
    except ValueError:
        deal_type = DealType.OTHER

    # Convert approval rights strings to enums
    approval_rights = []
    for ar in input_deal.approval_rights_granted:
        try:
            approval_rights.append(ApprovalRight(ar))
        except ValueError:
            pass  # Skip invalid approval rights

    # Convert rights windows strings to enums
    rights_windows = []
    for rw in input_deal.rights_windows:
        try:
            rights_windows.append(RightsWindow(rw))
        except ValueError:
            pass  # Skip invalid rights windows

    return DealBlock(
        deal_id=input_deal.deal_id,
        deal_name=input_deal.deal_name,
        deal_type=deal_type,
        counterparty_name=input_deal.counterparty_name,
        amount=input_deal.amount,
        territories=input_deal.territories,
        is_worldwide=input_deal.is_worldwide,
        rights_windows=rights_windows,
        term_years=input_deal.term_years,
        exclusivity=input_deal.exclusivity,
        holdback_days=input_deal.holdback_days,
        ownership_percentage=input_deal.ownership_percentage,
        approval_rights_granted=approval_rights,
        has_board_seat=input_deal.has_board_seat,
        has_veto_rights=input_deal.has_veto_rights,
        veto_scope=input_deal.veto_scope,
        ip_ownership=input_deal.ip_ownership,
        mfn_clause=input_deal.mfn_clause,
        mfn_scope=input_deal.mfn_scope,
        reversion_trigger_years=input_deal.reversion_trigger_years,
        sequel_rights_holder=input_deal.sequel_rights_holder,
        cross_collateralized=input_deal.cross_collateralized,
        cross_collateral_scope=input_deal.cross_collateral_scope,
        complexity_score=input_deal.complexity_score,
    )


def _result_to_response(result: OwnershipControlResult) -> OwnershipScoreResponse:
    """Convert scorer result to API response"""
    return OwnershipScoreResponse(
        ownership_score=result.ownership_score,
        control_score=result.control_score,
        optionality_score=result.optionality_score,
        friction_score=result.friction_score,
        composite_score=result.composite_score,
        impacts=[
            ControlImpactResponse(
                source=i.source,
                dimension=i.dimension,
                impact=i.impact,
                explanation=i.explanation
            )
            for i in result.impacts
        ],
        deal_impacts=result.deal_impacts,
        recommendations=result.recommendations,
        flags=ScoringFlagsResponse(
            has_mfn_risk=result.has_mfn_risk,
            has_control_concentration=result.has_control_concentration,
            has_reversion_opportunity=result.has_reversion_opportunity
        )
    )


@router.post("/score", response_model=OwnershipScoreResponse)
async def score_deals(request: OwnershipScoreRequest) -> OwnershipScoreResponse:
    """
    Score a set of deal blocks on ownership, control, optionality, and friction.

    Returns dimension scores (0-100), a weighted composite score,
    detailed impact explanations, and actionable recommendations.
    """
    try:
        # Convert weights if provided
        weights = None
        if request.weights:
            weights = {
                "ownership": request.weights.ownership,
                "control": request.weights.control,
                "optionality": request.weights.optionality,
                "friction": request.weights.friction,
            }

        # Initialize scorer
        scorer = OwnershipControlScorer(weights=weights)

        # Convert input deals to DealBlock models
        deal_blocks = [
            _convert_input_to_deal_block(d)
            for d in request.deal_blocks
        ]

        # Score the scenario
        result = scorer.score_scenario(deal_blocks)

        return _result_to_response(result)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/compare", response_model=ScenarioComparisonResponse)
async def compare_scenarios(request: ScenarioComparisonRequest) -> ScenarioComparisonResponse:
    """
    Compare multiple scenarios and identify which is best on each dimension.

    Useful for side-by-side comparison of different deal structures.
    """
    try:
        # Convert weights if provided
        weights = None
        if request.weights:
            weights = {
                "ownership": request.weights.ownership,
                "control": request.weights.control,
                "optionality": request.weights.optionality,
                "friction": request.weights.friction,
            }

        # Initialize scorer
        scorer = OwnershipControlScorer(weights=weights)

        # Convert and score each scenario
        results: Dict[str, OwnershipScoreResponse] = {}
        raw_results: Dict[str, OwnershipControlResult] = {}

        for scenario_name, deal_inputs in request.scenarios.items():
            deal_blocks = [_convert_input_to_deal_block(d) for d in deal_inputs]
            result = scorer.score_scenario(deal_blocks)
            results[scenario_name] = _result_to_response(result)
            raw_results[scenario_name] = result

        # Find best scenarios for each dimension
        best_composite = max(raw_results.keys(), key=lambda k: raw_results[k].composite_score)
        best_ownership = max(raw_results.keys(), key=lambda k: raw_results[k].ownership_score)
        best_control = max(raw_results.keys(), key=lambda k: raw_results[k].control_score)
        best_optionality = max(raw_results.keys(), key=lambda k: raw_results[k].optionality_score)
        lowest_friction = min(raw_results.keys(), key=lambda k: raw_results[k].friction_score)

        return ScenarioComparisonResponse(
            results=results,
            best_composite=best_composite,
            best_ownership=best_ownership,
            best_control=best_control,
            best_optionality=best_optionality,
            lowest_friction=lowest_friction
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/weights")
async def get_default_weights() -> Dict[str, Any]:
    """
    Get the default scoring weights.

    Returns the default weight configuration that will be used
    if no custom weights are provided.
    """
    return {
        "ownership": 0.35,
        "control": 0.30,
        "optionality": 0.20,
        "friction": 0.15,
        "note": "Weights should sum to 1.0. Friction is inverted (lower is better)."
    }


@router.get("/dimensions")
async def get_dimension_info() -> Dict[str, Dict]:
    """
    Get information about each scoring dimension.

    Useful for UI tooltips and documentation.
    """
    return {
        "ownership": {
            "name": "Ownership Score",
            "description": "How much IP and revenue rights does producer retain?",
            "scale": "0-100 (higher is better)",
            "factors": [
                "IP ownership (producer/shared/counterparty)",
                "Territory coverage (worldwide vs regional)",
                "Rights windows granted",
                "License term length",
                "Equity percentage ceded"
            ],
            "interpretation": {
                "90-100": "Full ownership, minimal encumbrances",
                "70-89": "Strong ownership with some licenses",
                "50-69": "Shared ownership or significant licenses",
                "30-49": "Minority position or major rights sold",
                "0-29": "Work-for-hire or full buyout"
            }
        },
        "control": {
            "name": "Control Score",
            "description": "How much creative and business control is retained?",
            "scale": "0-100 (higher is better)",
            "factors": [
                "Approval rights granted (final cut, script, cast, etc.)",
                "Board seats granted",
                "Veto rights granted",
                "IP ownership implications"
            ],
            "interpretation": {
                "90-100": "Full creative control, no approvals needed",
                "70-89": "Minor approval requirements",
                "50-69": "Shared control, some creative approvals",
                "30-49": "Significant control ceded, veto rights granted",
                "0-29": "Minimal control, counterparty has final cut"
            }
        },
        "optionality": {
            "name": "Optionality Score",
            "description": "How much future flexibility is preserved?",
            "scale": "0-100 (higher is better)",
            "factors": [
                "Sequel/derivative rights holder",
                "MFN (Most Favored Nations) clauses",
                "Reversion trigger terms",
                "Cross-collateralization",
                "Holdback periods"
            ],
            "interpretation": {
                "90-100": "All sequel rights, no MFN, clean reversions",
                "70-89": "Most options preserved, minor constraints",
                "50-69": "Some sequel rights encumbered, MFN present",
                "30-49": "Significant future constraints",
                "0-29": "Franchise locked up, no optionality"
            }
        },
        "friction": {
            "name": "Friction Score",
            "description": "How complex and risky is execution?",
            "scale": "0-100 (lower is better)",
            "factors": [
                "Deal complexity score",
                "Number of approval rights",
                "Board/veto coordination",
                "MFN compliance monitoring",
                "Cross-collateral accounting"
            ],
            "interpretation": {
                "0-20": "Simple deal, minimal approvals",
                "21-40": "Standard complexity",
                "41-60": "Multiple parties, some approvals",
                "61-80": "Complex structure, many stakeholders",
                "81-100": "Very complex, high execution risk"
            }
        }
    }
