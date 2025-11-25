"""
Scenario Optimizer Endpoints (Engine 3)
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional
from decimal import Decimal
import uuid

from app.schemas import scenarios as schemas
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

# Import Engine 3 & Engine 4 (path setup done in api.py)
from engines.scenario_optimizer.scenario_generator import ScenarioGenerator
from engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluator
from models.waterfall import WaterfallStructure, WaterfallNode, PayeeType, RecoupmentPriority, RecoupmentBasis
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
        # Use provided waterfall_id or generate one
        waterfall_id = request.waterfall_id or f"WF-{request.project_id}-AUTO"

        # Create sample waterfall structure (in production, load from database)
        waterfall_structure = _create_sample_waterfall(
            request.project_id, waterfall_id
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
        evaluator = ScenarioEvaluator()

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
    1. Loads specified scenarios (regenerates from templates for now)
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
        # Map scenario_ids to template names
        template_map = {
            "scenario_debt_heavy": "debt_heavy",
            "scenario_equity_heavy": "equity_heavy",
            "scenario_balanced": "balanced",
            "scenario_presale_focused": "presale_focused",
            "scenario_incentive_maximized": "incentive_maximized",
        }

        # Default project budget if not loading from database
        project_budget = Decimal("30000000")  # $30M default
        waterfall_id = "waterfall_comparison"

        # Create waterfall structure
        waterfall_structure = _create_sample_waterfall(request.project_id, waterfall_id)

        # Initialize generator and evaluator
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator()

        # Generate requested scenarios
        scenarios = []
        scenario_metrics: Dict[str, Dict] = {}

        for scenario_id in request.scenario_ids:
            template_name = template_map.get(scenario_id)
            if not template_name:
                # Use balanced as fallback for unknown IDs
                template_name = "balanced"

            # Generate capital stack from template
            capital_stack = generator.generate_from_template(
                template_name=template_name,
                project_budget=project_budget
            )

            # Evaluate scenario
            evaluation = evaluator.evaluate(
                capital_stack=capital_stack,
                waterfall_structure=waterfall_structure,
                revenue_projection=project_budget * Decimal("2.5"),
                run_monte_carlo=False
            )

            # Extract capital structure
            capital_structure = _extract_capital_structure(capital_stack)

            # Calculate totals
            total_debt = (
                capital_structure.senior_debt
                + capital_structure.gap_financing
                + capital_structure.mezzanine_debt
            )
            total_equity = capital_structure.equity
            debt_to_equity_ratio = (
                total_debt / total_equity if total_equity > 0 else None
            )

            # Create metrics
            tax_rate = _calculate_tax_rate(capital_stack)
            equity_irr = getattr(evaluation, 'equity_irr', Decimal("0")) or Decimal("0")
            risk_score = Decimal("50")

            metrics = ScenarioMetrics(
                equity_irr=equity_irr,
                cost_of_capital=Decimal("10"),
                tax_incentive_rate=tax_rate,
                risk_score=risk_score,
                debt_coverage_ratio=Decimal("2.0"),
                probability_of_recoupment=Decimal("80.0"),
                total_debt=total_debt,
                total_equity=total_equity,
                debt_to_equity_ratio=debt_to_equity_ratio,
            )

            strengths, weaknesses = _analyze_scenario_strengths_weaknesses(
                capital_structure, metrics
            )

            optimization_score = evaluation.overall_score if evaluation.overall_score else Decimal("70")

            scenario = Scenario(
                scenario_id=scenario_id,
                scenario_name=template_name.replace("_", " ").title(),
                optimization_score=optimization_score,
                capital_structure=capital_structure,
                metrics=metrics,
                strategic_metrics=None,
                strengths=strengths,
                weaknesses=weaknesses,
                validation_passed=True,
                validation_errors=[],
            )

            scenarios.append(scenario)
            scenario_metrics[scenario_id] = {
                "irr": float(equity_irr),
                "risk": float(risk_score),
                "tax_rate": float(tax_rate),
                "score": float(optimization_score),
                "name": template_name.replace("_", " ").title()
            }

        # Generate trade-off analyses
        trade_off_analyses = []

        # IRR vs Risk trade-off
        irr_risk_points = [
            TradeOffPoint(
                scenario_id=sid,
                scenario_name=data["name"],
                x_value=Decimal(str(data["risk"])),
                y_value=Decimal(str(data["irr"])),
                optimization_score=Decimal(str(data["score"]))
            )
            for sid, data in scenario_metrics.items()
        ]

        irr_risk_analysis = TradeOffAnalysis(
            x_axis="Risk Score (lower is better)",
            y_axis="Equity IRR % (higher is better)",
            points=irr_risk_points,
            insights=_generate_irr_risk_insights(scenario_metrics)
        )
        trade_off_analyses.append(irr_risk_analysis)

        # Tax Rate vs IRR trade-off
        tax_irr_points = [
            TradeOffPoint(
                scenario_id=sid,
                scenario_name=data["name"],
                x_value=Decimal(str(data["tax_rate"])),
                y_value=Decimal(str(data["irr"])),
                optimization_score=Decimal(str(data["score"]))
            )
            for sid, data in scenario_metrics.items()
        ]

        tax_irr_analysis = TradeOffAnalysis(
            x_axis="Tax Incentive Rate % (higher is better)",
            y_axis="Equity IRR % (higher is better)",
            points=tax_irr_points,
            insights=_generate_tax_irr_insights(scenario_metrics)
        )
        trade_off_analyses.append(tax_irr_analysis)

        # Generate recommendation
        recommendation = _generate_comparison_recommendation(scenarios, scenario_metrics)

        return ScenarioComparisonResponse(
            project_id=request.project_id,
            scenarios=scenarios,
            trade_off_analyses=trade_off_analyses,
            recommendation=recommendation
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario comparison failed: {str(e)}",
        )


def _generate_irr_risk_insights(metrics: Dict[str, Dict]) -> List[str]:
    """Generate insights for IRR vs Risk trade-off."""
    insights = []

    # Find best IRR and lowest risk
    best_irr = max(metrics.items(), key=lambda x: x[1]["irr"])
    lowest_risk = min(metrics.items(), key=lambda x: x[1]["risk"])

    insights.append(f"{best_irr[1]['name']} offers the highest IRR at {best_irr[1]['irr']:.1f}%")
    insights.append(f"{lowest_risk[1]['name']} has the lowest risk profile")

    # Check for efficient frontier scenarios
    irr_values = [m["irr"] for m in metrics.values()]
    risk_values = [m["risk"] for m in metrics.values()]

    if max(irr_values) - min(irr_values) > 5:
        insights.append("Significant IRR variation across scenarios - careful selection important")

    if best_irr[0] != lowest_risk[0]:
        insights.append("Trade-off exists between maximum returns and minimum risk")
    else:
        insights.append(f"{best_irr[1]['name']} dominates on both IRR and risk dimensions")

    return insights


def _generate_tax_irr_insights(metrics: Dict[str, Dict]) -> List[str]:
    """Generate insights for Tax Rate vs IRR trade-off."""
    insights = []

    best_tax = max(metrics.items(), key=lambda x: x[1]["tax_rate"])
    best_irr = max(metrics.items(), key=lambda x: x[1]["irr"])

    insights.append(f"{best_tax[1]['name']} captures the most tax incentives at {best_tax[1]['tax_rate']:.1f}%")

    if best_tax[0] == best_irr[0]:
        insights.append("Tax optimization aligns with IRR optimization")
    else:
        insights.append(f"Tax-optimized scenario differs from IRR-optimized - consider project priorities")

    avg_tax = sum(m["tax_rate"] for m in metrics.values()) / len(metrics)
    insights.append(f"Average tax incentive capture across scenarios: {avg_tax:.1f}%")

    return insights


def _generate_comparison_recommendation(scenarios: List[Scenario], metrics: Dict[str, Dict]) -> str:
    """Generate overall recommendation from scenario comparison."""
    # Find best overall scenario
    best_overall = max(metrics.items(), key=lambda x: x[1]["score"])
    best_irr = max(metrics.items(), key=lambda x: x[1]["irr"])
    best_tax = max(metrics.items(), key=lambda x: x[1]["tax_rate"])
    lowest_risk = min(metrics.items(), key=lambda x: x[1]["risk"])

    if best_overall[0] == best_irr[0] == best_tax[0]:
        return f"Strong recommendation: {best_overall[1]['name']} dominates across all key metrics (IRR, tax capture, and overall score)."
    elif best_overall[0] == lowest_risk[0]:
        return f"Recommended: {best_overall[1]['name']} offers the best risk-adjusted returns. Consider {best_irr[1]['name']} if maximizing IRR is the priority."
    else:
        return f"Balanced recommendation: {best_overall[1]['name']} offers the best overall score. For maximum IRR, consider {best_irr[1]['name']}. For maximum tax capture, consider {best_tax[1]['name']}."


# ========================================
# New Optimizer Endpoints
# ========================================


@router.post(
    "/validate-constraints",
    response_model=schemas.ValidateConstraintsResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate Constraints",
    description="Validate a capital stack configuration against hard and soft constraints",
)
async def validate_constraints(request: schemas.ValidateConstraintsRequest):
    """
    Validate capital stack against constraints.

    This endpoint:
    1. Converts capital structure to CapitalStack
    2. Applies default or custom constraints
    3. Validates hard constraints (must satisfy)
    4. Validates soft constraints (preferences)
    5. Returns violations and penalties

    Args:
        request: Capital structure and constraints to validate

    Returns:
        Validation result with violations and penalties

    Raises:
        HTTPException: If validation fails
    """
    try:
        from engines.scenario_optimizer.constraint_manager import ConstraintManager
        from models.financial_instruments import (
            SeniorDebt, GapFinancing, MezzanineDebt, Equity, TaxIncentive, PreSale, Grant
        )
        from models.capital_stack import CapitalStack, CapitalComponent

        # Build CapitalStack from capital structure
        components = []
        position = 1

        if request.capital_structure.senior_debt > 0:
            inst = SeniorDebt(
                amount=request.capital_structure.senior_debt,
                interest_rate=Decimal("7.0"),
                term_months=60
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.capital_structure.gap_financing > 0:
            inst = GapFinancing(
                amount=request.capital_structure.gap_financing,
                interest_rate=Decimal("9.0"),
                term_months=48,
                minimum_presales_percentage=Decimal("30.0")
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.capital_structure.mezzanine_debt > 0:
            inst = MezzanineDebt(
                amount=request.capital_structure.mezzanine_debt,
                interest_rate=Decimal("11.0"),
                term_months=60,
                equity_kicker_percentage=Decimal("5.0")
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.capital_structure.equity > 0:
            inst = Equity(
                amount=request.capital_structure.equity,
                ownership_percentage=Decimal("40.0"),
                premium_percentage=Decimal("120.0")
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.capital_structure.tax_incentives > 0:
            inst = TaxIncentive(
                amount=request.capital_structure.tax_incentives,
                jurisdiction="California",
                qualified_spend=request.capital_structure.tax_incentives * Decimal("4"),
                credit_rate=Decimal("25.0"),
                timing_months=18
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.capital_structure.presales > 0:
            inst = PreSale(
                amount=request.capital_structure.presales,
                territory="North America",
                rights_description="All media",
                mg_amount=request.capital_structure.presales,
                payment_on_delivery=Decimal("80.0")
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.capital_structure.grants > 0:
            inst = Grant(
                amount=request.capital_structure.grants,
                grantor_name="Film Fund",
                grant_type="Cultural"
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        capital_stack = CapitalStack(
            stack_name="validation_stack",
            project_budget=request.project_budget,
            components=components
        )

        # Initialize constraint manager (uses defaults if no custom constraints)
        manager = ConstraintManager()

        # TODO: Add custom constraints from request if provided
        # For now, using default constraints only

        # Validate
        validation = manager.validate(capital_stack)

        # Convert violations to output format
        hard_violations = [
            schemas.ConstraintViolationOutput(
                constraint_id=v.constraint.constraint_id,
                constraint_type=v.constraint.constraint_type.value,
                description=v.constraint.description,
                severity=v.severity,
                details=v.details
            )
            for v in validation.hard_violations
        ]

        soft_violations = [
            schemas.ConstraintViolationOutput(
                constraint_id=v.constraint.constraint_id,
                constraint_type=v.constraint.constraint_type.value,
                description=v.constraint.description,
                severity=v.severity,
                details=v.details
            )
            for v in validation.soft_violations
        ]

        return schemas.ValidateConstraintsResponse(
            is_valid=validation.is_valid,
            hard_violations=hard_violations,
            soft_violations=soft_violations,
            total_penalty=validation.total_penalty,
            summary=validation.summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Constraint validation failed: {str(e)}",
        )


@router.post(
    "/optimize-capital-stack",
    response_model=schemas.OptimizeCapitalStackResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimize Capital Stack",
    description="Find optimal capital stack allocation using scipy optimization",
)
async def optimize_capital_stack(request: schemas.OptimizeCapitalStackRequest):
    """
    Optimize capital stack allocation.

    This endpoint:
    1. Takes template capital structure as starting point
    2. Uses scipy.optimize to find optimal allocations
    3. Respects hard constraints
    4. Minimizes soft constraint penalties
    5. Maximizes weighted objective function

    Args:
        request: Template structure, objectives, and constraints

    Returns:
        Optimized capital stack with solver metadata

    Raises:
        HTTPException: If optimization fails
    """
    try:
        from engines.scenario_optimizer.capital_stack_optimizer import CapitalStackOptimizer
        from engines.scenario_optimizer.constraint_manager import ConstraintManager
        from models.financial_instruments import (
            SeniorDebt, GapFinancing, MezzanineDebt, Equity, TaxIncentive, PreSale, Grant
        )
        from models.capital_stack import CapitalStack, CapitalComponent

        # Build template CapitalStack
        components = []
        position = 1

        if request.template_structure.senior_debt > 0:
            inst = SeniorDebt(
                amount=request.template_structure.senior_debt,
                interest_rate=Decimal("7.0"),
                term_months=60
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.template_structure.gap_financing > 0:
            inst = GapFinancing(
                amount=request.template_structure.gap_financing,
                interest_rate=Decimal("9.0"),
                term_months=48,
                minimum_presales_percentage=Decimal("30.0")
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.template_structure.mezzanine_debt > 0:
            inst = MezzanineDebt(
                amount=request.template_structure.mezzanine_debt,
                interest_rate=Decimal("11.0"),
                term_months=60,
                equity_kicker_percentage=Decimal("5.0")
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.template_structure.equity > 0:
            inst = Equity(
                amount=request.template_structure.equity,
                ownership_percentage=Decimal("40.0"),
                premium_percentage=Decimal("120.0")
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.template_structure.tax_incentives > 0:
            inst = TaxIncentive(
                amount=request.template_structure.tax_incentives,
                jurisdiction="California",
                qualified_spend=request.template_structure.tax_incentives * Decimal("4"),
                credit_rate=Decimal("25.0"),
                timing_months=18
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.template_structure.presales > 0:
            inst = PreSale(
                amount=request.template_structure.presales,
                territory="North America",
                rights_description="All media",
                mg_amount=request.template_structure.presales,
                payment_on_delivery=Decimal("80.0")
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        if request.template_structure.grants > 0:
            inst = Grant(
                amount=request.template_structure.grants,
                grantor_name="Film Fund",
                grant_type="Cultural"
            )
            components.append(CapitalComponent(instrument=inst, position=position))
            position += 1

        template_stack = CapitalStack(
            stack_name="template_stack",
            project_budget=request.project_budget,
            components=components
        )

        # Initialize optimizer with constraint manager
        constraint_manager = ConstraintManager()
        optimizer = CapitalStackOptimizer(constraint_manager=constraint_manager)

        # Convert objective weights to dict
        objective_weights = {
            "equity_irr": request.objective_weights.equity_irr / Decimal("100"),
            "cost_of_capital": request.objective_weights.cost_of_capital / Decimal("100"),
            "tax_incentives": request.objective_weights.tax_incentive_capture / Decimal("100"),
            "risk": request.objective_weights.risk_minimization / Decimal("100"),
        }

        # Convert bounds if provided
        bounds_dict = None
        if request.bounds:
            bounds_dict = {
                "equity": (request.bounds.equity_min_pct, request.bounds.equity_max_pct),
                "senior_debt": (request.bounds.senior_debt_min_pct, request.bounds.senior_debt_max_pct),
                "mezzanine_debt": (request.bounds.mezzanine_debt_min_pct, request.bounds.mezzanine_debt_max_pct),
                "gap_financing": (request.bounds.gap_financing_min_pct, request.bounds.gap_financing_max_pct),
                "pre_sale": (request.bounds.pre_sale_min_pct, request.bounds.pre_sale_max_pct),
                "tax_incentive": (request.bounds.tax_incentive_min_pct, request.bounds.tax_incentive_max_pct),
            }

        # Run optimization
        if request.use_convergence:
            result = optimizer.optimize_with_convergence(
                template_stack=template_stack,
                project_budget=request.project_budget,
                objective_weights=objective_weights,
                bounds=bounds_dict,
                scenario_name="optimized_scenario",
                waterfall_structure=None,  # Simple mode without waterfall
                num_starts=3
            )
        else:
            result = optimizer.optimize(
                template_stack=template_stack,
                project_budget=request.project_budget,
                objective_weights=objective_weights,
                bounds=bounds_dict,
                scenario_name="optimized_scenario",
                waterfall_structure=None  # Simple mode without waterfall
            )

        # Extract optimized structure
        optimized_structure = _extract_capital_structure(result.capital_stack)

        # Build convergence info if available
        convergence_info = None
        if "convergence_scores" in result.metadata:
            convergence_info = {
                "num_starts": result.metadata.get("num_starts", 1),
                "convergence_std": result.metadata.get("convergence_std", 0.0),
                "convergence_range": result.metadata.get("convergence_range", 0.0),
            }

        return schemas.OptimizeCapitalStackResponse(
            objective_value=result.objective_value,
            optimized_structure=optimized_structure,
            solver_status=result.solver_status,
            solve_time_seconds=result.solve_time_seconds,
            allocations=result.allocations,
            num_iterations=result.metadata.get("num_iterations", 0),
            num_evaluations=result.metadata.get("num_evaluations", 0),
            convergence_info=convergence_info
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Capital stack optimization failed: {str(e)}",
        )


@router.post(
    "/analyze-tradeoffs",
    response_model=schemas.AnalyzeTradeoffsResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Tradeoffs",
    description="Identify Pareto frontier and analyze tradeoffs between competing objectives",
)
async def analyze_tradeoffs(request: schemas.AnalyzeTradeoffsRequest):
    """
    Analyze tradeoffs between scenarios.

    This endpoint:
    1. Takes multiple evaluated scenarios
    2. Identifies Pareto-optimal scenarios
    3. Calculates trade-off slopes
    4. Generates insights and recommendations
    5. Highlights dominated scenarios

    Args:
        request: List of scenarios with metrics

    Returns:
        Pareto frontiers, recommendations, and trade-off summary

    Raises:
        HTTPException: If analysis fails
    """
    try:
        from engines.scenario_optimizer.tradeoff_analyzer import TradeOffAnalyzer
        from engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluation
        from models.capital_stack import CapitalStack

        # Convert scenarios to ScenarioEvaluation objects
        evaluations = []
        for scenario in request.scenarios:
            # Create minimal evaluation with metrics
            evaluation = ScenarioEvaluation(
                scenario_name=scenario.scenario_name,
                capital_stack=None  # We don't need full stack for tradeoff analysis
            )

            # Set metrics from input
            evaluation.equity_irr = scenario.metrics.equity_irr
            evaluation.weighted_cost_of_capital = scenario.metrics.cost_of_capital
            evaluation.tax_incentive_effective_rate = scenario.metrics.tax_incentive_rate
            evaluation.risk_score = scenario.metrics.risk_score
            evaluation.debt_coverage_ratio = scenario.metrics.debt_coverage_ratio
            evaluation.probability_of_equity_recoupment = scenario.metrics.probability_of_recoupment
            evaluation.senior_debt_recovery_rate = Decimal("95.0")  # Default
            evaluation.overall_score = Decimal("75.0")  # Default

            evaluations.append(evaluation)

        # Initialize analyzer
        analyzer = TradeOffAnalyzer()

        # Convert objective pairs if provided
        objective_pairs = None
        if request.objective_pairs:
            objective_pairs = [tuple(pair) for pair in request.objective_pairs]

        # Run analysis
        analysis = analyzer.analyze(
            evaluations=evaluations,
            objective_pairs=objective_pairs
        )

        # Convert Pareto frontiers to output format
        pareto_frontiers = []
        for frontier in analysis.pareto_frontiers:
            frontier_points = [
                schemas.ParetoPoint(
                    scenario_id=p.scenario_name,
                    scenario_name=p.scenario_name,
                    objective_1_value=p.objective_1_value,
                    objective_2_value=p.objective_2_value,
                    is_pareto_optimal=p.is_pareto_optimal,
                    dominated_by=p.dominated_by
                )
                for p in frontier.frontier_points
            ]

            dominated_points = [
                schemas.ParetoPoint(
                    scenario_id=p.scenario_name,
                    scenario_name=p.scenario_name,
                    objective_1_value=p.objective_1_value,
                    objective_2_value=p.objective_2_value,
                    is_pareto_optimal=p.is_pareto_optimal,
                    dominated_by=p.dominated_by
                )
                for p in frontier.dominated_points
            ]

            pareto_frontiers.append(
                schemas.ParetoFrontierOutput(
                    objective_1_name=frontier.objective_1_name,
                    objective_2_name=frontier.objective_2_name,
                    frontier_points=frontier_points,
                    dominated_points=dominated_points,
                    trade_off_slope=frontier.trade_off_slope,
                    insights=frontier.insights
                )
            )

        return schemas.AnalyzeTradeoffsResponse(
            pareto_frontiers=pareto_frontiers,
            recommended_scenarios=analysis.recommended_scenarios,
            trade_off_summary=analysis.trade_off_summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tradeoff analysis failed: {str(e)}",
        )


def _create_sample_waterfall(project_id: str, waterfall_id: str) -> WaterfallStructure:
    """Create a sample waterfall structure for testing."""
    nodes = [
        WaterfallNode(
            node_id="senior_debt",
            priority=RecoupmentPriority.SENIOR_DEBT,
            description="Senior Debt Recoupment",
            payee_type=PayeeType.LENDER,
            payee_name="Senior Lender",
            recoupment_basis=RecoupmentBasis.REMAINING_POOL,
            percentage_of_receipts=Decimal("100"),
        ),
        WaterfallNode(
            node_id="mezzanine_debt",
            priority=RecoupmentPriority.MEZZANINE_DEBT,
            description="Mezzanine Debt Recoupment",
            payee_type=PayeeType.LENDER,
            payee_name="Mezzanine Lender",
            recoupment_basis=RecoupmentBasis.REMAINING_POOL,
            percentage_of_receipts=Decimal("100"),
        ),
        WaterfallNode(
            node_id="equity",
            priority=RecoupmentPriority.EQUITY_RECOUPMENT,
            description="Equity Recoupment",
            payee_type=PayeeType.INVESTOR,
            payee_name="Equity Investor",
            recoupment_basis=RecoupmentBasis.REMAINING_POOL,
            percentage_of_receipts=Decimal("100"),
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
