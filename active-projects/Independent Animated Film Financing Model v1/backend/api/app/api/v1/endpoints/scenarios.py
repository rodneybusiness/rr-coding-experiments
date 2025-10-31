"""
Scenario Optimizer Endpoints (Engine 3)
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict
from decimal import Decimal

from app.schemas.scenarios import (
    ScenarioGenerationRequest,
    ScenarioGenerationResponse,
    Scenario,
    CapitalStructure,
    ScenarioMetrics,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
    TradeOffAnalysis,
    TradeOffPoint,
)

# Import Engine 3
import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_root))

from engines.scenario_optimizer.scenario_generator import ScenarioGenerator
from engines.scenario_optimizer.constraint_manager import ConstraintManager
from engines.scenario_optimizer.capital_stack_optimizer import CapitalStackOptimizer
from engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluator
from engines.scenario_optimizer.scenario_comparator import ScenarioComparator
from engines.scenario_optimizer.tradeoff_analyzer import TradeOffAnalyzer
from models.waterfall import WaterfallStructure, WaterfallNode, PayeeType

router = APIRouter()


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
    1. Generates multiple capital stack scenarios
    2. Optimizes each for different objectives (max leverage, tax optimized, balanced, low risk)
    3. Evaluates each scenario with comprehensive metrics
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

        # Initialize components
        constraint_manager = ConstraintManager()
        evaluator = ScenarioEvaluator(waterfall_structure)
        optimizer = CapitalStackOptimizer(constraint_manager, evaluator)
        generator = ScenarioGenerator(optimizer, constraint_manager)

        # Set objective weights (use defaults if not provided)
        objective_weights = (
            request.objective_weights.model_dump()
            if request.objective_weights
            else {
                "equity_irr": Decimal("30.0"),
                "cost_of_capital": Decimal("25.0"),
                "tax_incentive_capture": Decimal("20.0"),
                "risk_minimization": Decimal("25.0"),
            }
        )

        # Generate scenarios
        generated_scenarios = generator.generate_scenarios(
            project_budget=request.project_budget,
            waterfall_structure=waterfall_structure,
            objective_weights=objective_weights,
            num_scenarios=request.num_scenarios,
        )

        # Convert to API format
        scenarios = []
        best_score = Decimal("0")
        best_scenario_id = ""

        for gen_scenario in generated_scenarios:
            # Extract capital structure
            capital_structure = CapitalStructure(
                senior_debt=_get_instrument_amount(gen_scenario["capital_stack"], "SeniorDebt"),
                gap_financing=_get_instrument_amount(
                    gen_scenario["capital_stack"], "GapFinancing"
                ),
                mezzanine_debt=_get_instrument_amount(
                    gen_scenario["capital_stack"], "MezzanineDebt"
                ),
                equity=_get_instrument_amount(gen_scenario["capital_stack"], "Equity"),
                tax_incentives=_get_instrument_amount(
                    gen_scenario["capital_stack"], "TaxIncentive"
                ),
                presales=_get_instrument_amount(gen_scenario["capital_stack"], "PreSale"),
                grants=_get_instrument_amount(gen_scenario["capital_stack"], "Grant"),
            )

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

            # Extract evaluation metrics
            evaluation = gen_scenario["evaluation"]

            # Create scenario metrics
            metrics = ScenarioMetrics(
                equity_irr=evaluation["equity_irr"],
                cost_of_capital=evaluation["weighted_cost_of_capital"],
                tax_incentive_rate=evaluation["tax_incentive_rate"],
                risk_score=evaluation["risk_score"],
                debt_coverage_ratio=evaluation.get("debt_coverage_ratio", Decimal("2.0")),
                probability_of_recoupment=evaluation.get(
                    "probability_of_recoupment", Decimal("80.0")
                ),
                total_debt=total_debt,
                total_equity=total_equity,
                debt_to_equity_ratio=debt_to_equity_ratio,
            )

            # Generate strengths and weaknesses
            strengths, weaknesses = _analyze_scenario_strengths_weaknesses(
                capital_structure, metrics
            )

            # Create scenario
            scenario = Scenario(
                scenario_id=gen_scenario["scenario_name"].lower().replace(" ", "_"),
                scenario_name=gen_scenario["scenario_name"],
                optimization_score=gen_scenario["optimization_score"],
                capital_structure=capital_structure,
                metrics=metrics,
                strengths=strengths,
                weaknesses=weaknesses,
                validation_passed=gen_scenario["validation"]["is_valid"],
                validation_errors=gen_scenario["validation"]["errors"],
            )

            scenarios.append(scenario)

            # Track best scenario
            if gen_scenario["optimization_score"] > best_score:
                best_score = gen_scenario["optimization_score"]
                best_scenario_id = scenario.scenario_id

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


def _get_instrument_amount(capital_stack: "CapitalStack", instrument_type: str) -> Decimal:
    """Extract amount for a specific instrument type from capital stack."""
    for component in capital_stack.components:
        if component.__class__.__name__ == instrument_type:
            return component.amount
    return Decimal("0")


def _analyze_scenario_strengths_weaknesses(
    structure: CapitalStructure, metrics: ScenarioMetrics
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

    # If no weaknesses found
    if not weaknesses:
        weaknesses.append("No significant weaknesses")

    return strengths, weaknesses
