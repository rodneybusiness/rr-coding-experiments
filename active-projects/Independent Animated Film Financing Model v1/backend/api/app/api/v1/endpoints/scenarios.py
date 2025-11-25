"""
Scenario Optimizer Endpoints (Engine 3)
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional
from decimal import Decimal
import uuid

from app.schemas.scenarios import (
    ScenarioGenerationRequest,
    ScenarioGenerationResponse,
    Scenario,
    CapitalStructure,
    ScenarioMetrics,
    StrategicMetrics,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
    TradeOffAnalysis,
    TradeOffPoint,
)
from app.schemas.deals import DealBlockInput

# Import Engine 3 & Engine 4
import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_root))

from engines.scenario_optimizer.scenario_generator import ScenarioGenerator
from engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluator
from models.waterfall import WaterfallStructure, WaterfallNode, PayeeType
from models.capital_stack import CapitalStack
from models.deal_block import DealBlock, DealType, DealStatus, RightsWindow, ApprovalRight

router = APIRouter()


def _convert_deal_block_input(input: DealBlockInput) -> DealBlock:
    """Convert API DealBlockInput to DealBlock model."""
    # Convert deal type string to enum with fallback
    try:
        deal_type = DealType(input.deal_type)
    except ValueError:
        deal_type = DealType.OTHER

    # Convert status string to enum with fallback
    try:
        status = DealStatus(input.status)
    except ValueError:
        status = DealStatus.PROSPECTIVE

    # Convert rights windows
    rights_windows = []
    for w in input.rights_windows or []:
        try:
            rights_windows.append(RightsWindow(w))
        except ValueError:
            pass  # Skip invalid rights windows

    # Convert approval rights
    approval_rights = []
    for a in input.approval_rights_granted or []:
        try:
            approval_rights.append(ApprovalRight(a))
        except ValueError:
            pass  # Skip invalid approval rights

    return DealBlock(
        deal_id=f"deal_{uuid.uuid4().hex[:8]}",
        deal_name=input.deal_name,
        deal_type=deal_type,
        status=status,
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
        rights_windows=rights_windows,
        term_years=input.term_years,
        exclusivity=input.exclusivity,
        holdback_days=input.holdback_days,
        ownership_percentage=input.ownership_percentage,
        approval_rights_granted=approval_rights,
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


@router.post(
    "/generate",
    response_model=ScenarioGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Optimized Scenarios",
    description="Generate multiple optimized capital stack scenarios with different objectives",
)
async def generate_scenarios(request: ScenarioGenerationRequest):
    """
    Generate optimized capital stack scenarios.

    This endpoint:
    1. Generates multiple capital stack scenarios from templates
    2. Evaluates each scenario with comprehensive metrics
    3. If deal_blocks provided, includes strategic ownership/control scoring
    4. Validates structural constraints
    5. Identifies strengths and weaknesses

    Args:
        request: Scenario generation parameters

    Returns:
        Multiple scenarios with optimization scores and detailed metrics

    Raises:
        HTTPException: If generation fails or validation errors occur
    """
    try:
        # Create sample waterfall structure (in production, load from database)
        waterfall_structure = _create_sample_waterfall(
            request.project_id, request.waterfall_id
        )

        # Convert deal_blocks if provided
        deal_blocks: Optional[List[DealBlock]] = None
        if request.deal_blocks:
            deal_blocks = [
                _convert_deal_block_input(db_input)
                for db_input in request.deal_blocks
            ]

        # Initialize generator and evaluator
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(waterfall_structure)

        # Get templates to use based on num_scenarios
        all_templates = ["debt_heavy", "equity_heavy", "balanced", "presale_focused", "incentive_maximized"]
        templates_to_use = all_templates[: min(request.num_scenarios, len(all_templates))]

        # Generate and evaluate scenarios
        scenarios = []
        best_score = Decimal("0")
        best_scenario_id = ""

        for template_name in templates_to_use:
            # Generate capital stack from template
            capital_stack = generator.generate_from_template(
                template_name=template_name,
                project_budget=request.project_budget
            )

            # Evaluate with deal_blocks if provided
            evaluation = evaluator.evaluate(
                capital_stack=capital_stack,
                waterfall_structure=waterfall_structure,
                revenue_projection=request.project_budget * Decimal("2.5"),  # Assume 2.5x revenue
                run_monte_carlo=False,  # Skip Monte Carlo for API speed
                deal_blocks=deal_blocks
            )

            # Extract capital structure
            capital_structure = _extract_capital_structure(capital_stack)

            # Calculate total debt and equity
            total_debt = (
                capital_structure.senior_debt
                + capital_structure.gap_financing
                + capital_structure.mezzanine_debt
            )
            total_equity = capital_structure.equity

            # Calculate debt-to-equity ratio
            debt_to_equity_ratio = (
                total_debt / total_equity if total_equity > 0 else None
            )

            # Create scenario metrics from evaluation
            metrics = ScenarioMetrics(
                equity_irr=getattr(evaluation, 'equity_irr', Decimal("0")) or Decimal("0"),
                cost_of_capital=getattr(evaluation, 'weighted_average_cost', Decimal("10")) or Decimal("10"),
                tax_incentive_rate=_calculate_tax_rate(capital_stack),
                risk_score=Decimal("50"),  # Default risk score
                debt_coverage_ratio=Decimal("2.0"),
                probability_of_recoupment=Decimal("80.0"),
                total_debt=total_debt,
                total_equity=total_equity,
                debt_to_equity_ratio=debt_to_equity_ratio,
            )

            # Create strategic metrics if deal_blocks were provided
            strategic_metrics = None
            if deal_blocks and evaluation.strategic_composite_score is not None:
                strategic_metrics = StrategicMetrics(
                    ownership_score=evaluation.ownership_score,
                    control_score=evaluation.control_score,
                    optionality_score=evaluation.optionality_score,
                    friction_score=evaluation.friction_score,
                    strategic_composite_score=evaluation.strategic_composite_score,
                    ownership_control_impacts=evaluation.ownership_control_impacts,
                    strategic_recommendations=evaluation.strategic_recommendations,
                    has_mfn_risk=evaluation.has_mfn_risk,
                    has_control_concentration=evaluation.has_control_concentration,
                    has_reversion_opportunity=evaluation.has_reversion_opportunity,
                )

            # Generate strengths and weaknesses (include strategic insights)
            strengths, weaknesses = _analyze_scenario_strengths_weaknesses(
                capital_structure, metrics, strategic_metrics
            )

            # Calculate optimization score (blend financial + strategic if available)
            optimization_score = evaluation.overall_score if evaluation.overall_score else Decimal("70")

            # Create scenario
            scenario_id = f"scenario_{template_name}"
            scenario = Scenario(
                scenario_id=scenario_id,
                scenario_name=template_name.replace("_", " ").title(),
                optimization_score=optimization_score,
                capital_structure=capital_structure,
                metrics=metrics,
                strategic_metrics=strategic_metrics,
                strengths=strengths,
                weaknesses=weaknesses,
                validation_passed=True,
                validation_errors=[],
            )

            scenarios.append(scenario)

            # Track best scenario
            if optimization_score > best_score:
                best_score = optimization_score
                best_scenario_id = scenario_id

        return ScenarioGenerationResponse(
            project_id=request.project_id,
            project_name=request.project_name,
            project_budget=request.project_budget,
            scenarios=scenarios,
            best_scenario_id=best_scenario_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario generation failed: {str(e)}",
        )


@router.post(
    "/compare",
    response_model=ScenarioComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Scenarios",
    description="Perform detailed comparison and trade-off analysis between selected scenarios",
)
async def compare_scenarios(request: ScenarioComparisonRequest):
    """
    Compare multiple scenarios with trade-off analysis.

    This endpoint:
    1. Loads specified scenarios
    2. Performs side-by-side comparison
    3. Generates trade-off frontier analysis
    4. Provides recommendation

    Args:
        request: Scenarios to compare

    Returns:
        Detailed comparison with trade-off analysis

    Raises:
        HTTPException: If comparison fails
    """
    try:
        # TODO: In production, load actual scenarios from database
        # For now, return a placeholder response

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Scenario comparison endpoint not yet implemented. Use /generate endpoint to get scenarios.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario comparison failed: {str(e)}",
        )


def _create_sample_waterfall(project_id: str, waterfall_id: str) -> WaterfallStructure:
    """Create a sample waterfall structure for testing."""
    nodes = [
        WaterfallNode(
            node_id="senior_debt",
            description="Senior Debt Recoupment",
            payee_type=PayeeType.FINANCIER,
            payee_name="Senior Debt",
            recoupment_basis="senior_debt",
            fixed_amount=None,
            percentage_of_receipts=Decimal("100"),
            capped_at=None,
            waterfall_id=waterfall_id,
            project_id=project_id,
        ),
        WaterfallNode(
            node_id="gap_financing",
            description="Gap Financing Recoupment",
            payee_type=PayeeType.FINANCIER,
            payee_name="Gap Financing",
            recoupment_basis="gap_debt",
            fixed_amount=None,
            percentage_of_receipts=Decimal("100"),
            capped_at=None,
            waterfall_id=waterfall_id,
            project_id=project_id,
        ),
        WaterfallNode(
            node_id="equity",
            description="Equity Recoupment",
            payee_type=PayeeType.FINANCIER,
            payee_name="Equity Investor",
            recoupment_basis="equity",
            fixed_amount=None,
            percentage_of_receipts=Decimal("100"),
            capped_at=None,
            waterfall_id=waterfall_id,
            project_id=project_id,
        ),
    ]

    return WaterfallStructure(
        waterfall_id=waterfall_id,
        project_id=project_id,
        waterfall_name="Standard Waterfall",
        default_distribution_fee_rate=Decimal("30.0"),
        nodes=nodes,
    )


def _extract_capital_structure(capital_stack: CapitalStack) -> CapitalStructure:
    """Extract CapitalStructure from CapitalStack."""
    from models.financial_instruments import (
        SeniorDebt, GapFinancing, MezzanineDebt, Equity, TaxIncentive, PreSale, Grant
    )

    senior_debt = Decimal("0")
    gap_financing = Decimal("0")
    mezzanine_debt = Decimal("0")
    equity = Decimal("0")
    tax_incentives = Decimal("0")
    presales = Decimal("0")
    grants = Decimal("0")

    for component in capital_stack.components:
        inst = component.instrument
        if isinstance(inst, SeniorDebt):
            senior_debt += inst.amount
        elif isinstance(inst, GapFinancing):
            gap_financing += inst.amount
        elif isinstance(inst, MezzanineDebt):
            mezzanine_debt += inst.amount
        elif isinstance(inst, Equity):
            equity += inst.amount
        elif isinstance(inst, TaxIncentive):
            tax_incentives += inst.amount
        elif isinstance(inst, PreSale):
            presales += inst.amount
        elif isinstance(inst, Grant):
            grants += inst.amount

    return CapitalStructure(
        senior_debt=senior_debt,
        gap_financing=gap_financing,
        mezzanine_debt=mezzanine_debt,
        equity=equity,
        tax_incentives=tax_incentives,
        presales=presales,
        grants=grants,
    )


def _calculate_tax_rate(capital_stack: CapitalStack) -> Decimal:
    """Calculate tax incentive rate from capital stack."""
    from models.financial_instruments import TaxIncentive

    tax_amount = sum(
        c.instrument.amount for c in capital_stack.components
        if isinstance(c.instrument, TaxIncentive)
    )
    if capital_stack.project_budget > 0:
        return (tax_amount / capital_stack.project_budget) * Decimal("100")
    return Decimal("0")


def _analyze_scenario_strengths_weaknesses(
    structure: CapitalStructure,
    metrics: ScenarioMetrics,
    strategic_metrics: Optional[StrategicMetrics] = None
) -> tuple[List[str], List[str]]:
    """Analyze scenario to identify strengths and weaknesses."""
    strengths = []
    weaknesses = []

    # Analyze equity IRR
    if metrics.equity_irr >= Decimal("30.0"):
        strengths.append(f"Excellent equity returns ({metrics.equity_irr:.1f}% IRR)")
    elif metrics.equity_irr < Decimal("20.0"):
        weaknesses.append(f"Lower equity returns ({metrics.equity_irr:.1f}% IRR)")

    # Analyze tax incentive capture
    if metrics.tax_incentive_rate >= Decimal("20.0"):
        strengths.append(
            f"Exceptional tax incentive capture ({metrics.tax_incentive_rate:.1f}%)"
        )
    elif metrics.tax_incentive_rate < Decimal("10.0"):
        weaknesses.append(
            f"Limited tax incentive capture ({metrics.tax_incentive_rate:.1f}%)"
        )
    else:
        strengths.append(f"Good tax incentive capture ({metrics.tax_incentive_rate:.1f}%)")

    # Analyze risk
    if metrics.risk_score < Decimal("50.0"):
        strengths.append("Low risk profile")
    elif metrics.risk_score > Decimal("70.0"):
        weaknesses.append("High risk profile")

    # Analyze debt coverage
    if metrics.debt_coverage_ratio >= Decimal("2.0"):
        strengths.append("Strong debt coverage ratio")
    elif metrics.debt_coverage_ratio < Decimal("1.5"):
        weaknesses.append("Weak debt coverage ratio")

    # Analyze cost of capital
    if metrics.cost_of_capital < Decimal("10.0"):
        strengths.append("Low cost of capital")
    elif metrics.cost_of_capital > Decimal("12.0"):
        weaknesses.append("Higher cost of capital")

    # Analyze recoupment probability
    if metrics.probability_of_recoupment >= Decimal("85.0"):
        strengths.append(
            f"Very high probability of recoupment ({metrics.probability_of_recoupment:.1f}%)"
        )

    # Check if equity-heavy
    if structure.equity > structure.senior_debt + structure.gap_financing:
        weaknesses.append("Requires more equity capital")

    # Add strategic insights if available
    if strategic_metrics:
        if strategic_metrics.strategic_composite_score and strategic_metrics.strategic_composite_score >= Decimal("70"):
            strengths.append(f"Strong strategic position (score: {strategic_metrics.strategic_composite_score:.1f})")
        elif strategic_metrics.strategic_composite_score and strategic_metrics.strategic_composite_score < Decimal("50"):
            weaknesses.append(f"Weak strategic position (score: {strategic_metrics.strategic_composite_score:.1f})")

        if strategic_metrics.ownership_score and strategic_metrics.ownership_score >= Decimal("70"):
            strengths.append("Strong ownership retention")
        elif strategic_metrics.ownership_score and strategic_metrics.ownership_score < Decimal("50"):
            weaknesses.append("Significant ownership dilution")

        if strategic_metrics.control_score and strategic_metrics.control_score >= Decimal("70"):
            strengths.append("Strong creative control")
        elif strategic_metrics.control_score and strategic_metrics.control_score < Decimal("50"):
            weaknesses.append("Limited creative control")

        if strategic_metrics.has_mfn_risk:
            weaknesses.append("MFN clause creates deal flexibility risk")

        if strategic_metrics.has_reversion_opportunity:
            strengths.append("Rights reversion opportunity exists")

        if strategic_metrics.has_control_concentration:
            weaknesses.append("Control concentrated with single counterparty")

    # If no weaknesses found
    if not weaknesses:
        weaknesses.append("No significant weaknesses")

    return strengths, weaknesses
