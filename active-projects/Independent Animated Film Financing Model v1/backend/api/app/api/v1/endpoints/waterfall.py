"""
Waterfall Analysis Endpoints (Engine 2)
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict
from decimal import Decimal

from app.schemas.waterfall import (
    WaterfallExecutionRequest,
    WaterfallExecutionResponse,
    StakeholderReturn,
    QuarterlyDistribution,
    RevenueWindow,
    MonteCarloResults,
    MonteCarloPercentiles,
    SensitivityAnalysisRequest,
    SensitivityAnalysisResponse,
    SensitivityResultData,
    TornadoChartDataSchema,
    SensitivityVariableInput,
)

# Import Engine 2 (path setup done in api.py)
from engines.waterfall_executor.waterfall_executor import WaterfallExecutor
from engines.waterfall_executor.stakeholder_analyzer import StakeholderAnalyzer
from engines.waterfall_executor.monte_carlo_simulator import MonteCarloSimulator
from engines.waterfall_executor.revenue_projector import RevenueProjector
from engines.waterfall_executor.sensitivity_analyzer import (
    SensitivityAnalyzer,
    SensitivityVariable,
)
from models.capital_stack import CapitalStack
from models.waterfall import WaterfallStructure
from models.financial_instruments import *

router = APIRouter()


@router.post(
    "/execute",
    response_model=WaterfallExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Waterfall Analysis",
    description="Execute waterfall distribution with stakeholder returns and optional Monte Carlo simulation",
)
async def execute_waterfall(request: WaterfallExecutionRequest):
    """
    Execute waterfall distribution analysis.

    This endpoint:
    1. Projects revenue across distribution windows
    2. Executes waterfall distribution to stakeholders
    3. Calculates IRR/NPV for each stakeholder
    4. Optionally runs Monte Carlo simulation for risk analysis

    Args:
        request: Waterfall execution parameters

    Returns:
        Complete waterfall analysis with stakeholder returns and distributions

    Raises:
        HTTPException: If execution fails or validation errors occur
    """
    try:
        # TODO: Load capital stack and waterfall structure from database
        # For now, create sample structures for testing

        # Create sample capital stack (this should come from database)
        capital_stack = _create_sample_capital_stack(request.project_id)

        # Create sample waterfall structure (this should come from database)
        waterfall_structure = _create_sample_waterfall(
            request.project_id, request.waterfall_id
        )

        # Initialize revenue projector
        revenue_projector = RevenueProjector()

        # Project revenue by window
        revenue_projection = revenue_projector.project_revenue(
            total_ultimate_revenue=request.total_revenue,
            release_strategy=request.release_strategy,
        )

        # Initialize waterfall executor
        executor = WaterfallExecutor(waterfall_structure, capital_stack)

        # Execute waterfall
        distributions = executor.execute(revenue_projection)

        # Initialize stakeholder analyzer
        analyzer = StakeholderAnalyzer(capital_stack, distributions)

        # Analyze stakeholder returns
        stakeholder_analysis = analyzer.analyze_all_stakeholders()

        # Build stakeholder returns
        stakeholder_returns = []
        for stakeholder_id, analysis in stakeholder_analysis.items():
            stakeholder_returns.append(
                StakeholderReturn(
                    stakeholder_id=stakeholder_id,
                    stakeholder_name=analysis["name"],
                    stakeholder_type=analysis["type"],
                    invested=analysis["invested"],
                    received=analysis["total_received"],
                    profit=analysis["total_received"] - analysis["invested"],
                    cash_on_cash=analysis["cash_on_cash"],
                    irr=analysis["irr"],
                )
            )

        # Build distribution timeline (quarterly)
        distribution_timeline = _build_distribution_timeline(distributions)

        # Build revenue breakdown by window
        revenue_by_window = [
            RevenueWindow(
                window=window,
                revenue=amount,
                percentage=(amount / request.total_revenue * Decimal("100")),
            )
            for window, amount in revenue_projection.metadata[
                "revenue_by_window"
            ].items()
        ]

        # Run Monte Carlo simulation if requested
        monte_carlo_results = None
        if request.run_monte_carlo:
            monte_carlo_results = _run_monte_carlo_simulation(
                capital_stack=capital_stack,
                waterfall_structure=waterfall_structure,
                base_projection=revenue_projection,
                iterations=request.monte_carlo_iterations,
            )

        # Calculate totals
        total_distributed = sum(s.received for s in stakeholder_returns)
        total_recouped = sum(
            s.received for s in stakeholder_returns if s.invested > 0 and s.received >= s.invested
        )

        return WaterfallExecutionResponse(
            project_id=request.project_id,
            total_revenue=request.total_revenue,
            total_distributed=total_distributed,
            total_recouped=total_recouped,
            stakeholder_returns=stakeholder_returns,
            distribution_timeline=distribution_timeline,
            revenue_by_window=revenue_by_window,
            monte_carlo_results=monte_carlo_results,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Waterfall execution failed: {str(e)}",
        )


def _create_sample_capital_stack(project_id: str) -> CapitalStack:
    """Create a sample capital stack for testing."""
    from models.financial_instruments import (
        SeniorDebt,
        GapFinancing,
        MezzanineDebt,
        Equity,
    )
    from models.waterfall import RecoupmentPriority
    from models.capital_stack import CapitalComponent

    # Create financial instruments
    senior_debt = SeniorDebt(
        amount=Decimal("12000000"),
        interest_rate=Decimal("8.0"),
        term_months=36,
        recoupment_priority=RecoupmentPriority.SENIOR_DEBT,
    )
    gap_financing = GapFinancing(
        amount=Decimal("4500000"),
        interest_rate=Decimal("12.0"),
        term_months=24,
        recoupment_priority=RecoupmentPriority.SENIOR_DEBT,
    )
    mezzanine_debt = MezzanineDebt(
        amount=Decimal("3000000"),
        interest_rate=Decimal("15.0"),
        term_months=24,
        recoupment_priority=RecoupmentPriority.MEZZANINE_DEBT,  # Fixed: was MEZZANINE
    )
    equity = Equity(
        amount=Decimal("7500000"),
        ownership_percentage=Decimal("100.0"),  # Required field
        preferred_return=Decimal("12.0"),
        recoupment_priority=RecoupmentPriority.EQUITY,
    )

    # Wrap in CapitalComponents with position
    components = [
        CapitalComponent(instrument=senior_debt, position=1),
        CapitalComponent(instrument=gap_financing, position=2),
        CapitalComponent(instrument=mezzanine_debt, position=3),
        CapitalComponent(instrument=equity, position=4),
    ]

    return CapitalStack(
        project_id=project_id, components=components, project_budget=Decimal("30000000")
    )


def _create_sample_waterfall(project_id: str, waterfall_id: str) -> WaterfallStructure:
    """Create a sample waterfall structure for testing."""
    from models.waterfall import WaterfallNode, WaterfallStructure, PayeeType, RecoupmentPriority, RecoupmentBasis

    nodes = [
        # Senior Debt
        WaterfallNode(
            node_id="senior_debt",
            description="Senior Debt Recoupment",
            priority=RecoupmentPriority.SENIOR_DEBT,
            payee_type=PayeeType.LENDER,
            payee_name="Senior Lender",
            recoupment_basis=RecoupmentBasis.REMAINING_POOL,
            fixed_amount=None,
            percentage_of_receipts=Decimal("100"),
            capped_at=None,
        ),
        # Gap Financing
        WaterfallNode(
            node_id="gap_financing",
            description="Gap Financing Recoupment",
            priority=RecoupmentPriority.MEZZANINE_DEBT,
            payee_type=PayeeType.LENDER,
            payee_name="Gap Lender",
            recoupment_basis=RecoupmentBasis.REMAINING_POOL,
            fixed_amount=None,
            percentage_of_receipts=Decimal("100"),
            capped_at=None,
        ),
        # Mezzanine
        WaterfallNode(
            node_id="mezzanine_debt",
            description="Mezzanine Debt Recoupment",
            priority=RecoupmentPriority.MEZZANINE_DEBT,
            payee_type=PayeeType.LENDER,
            payee_name="Mezzanine Lender",
            recoupment_basis=RecoupmentBasis.REMAINING_POOL,
            fixed_amount=None,
            percentage_of_receipts=Decimal("100"),
            capped_at=None,
        ),
        # Equity
        WaterfallNode(
            node_id="equity",
            description="Equity Recoupment",
            priority=RecoupmentPriority.EQUITY_RECOUPMENT,
            payee_type=PayeeType.INVESTOR,
            payee_name="Equity Investor",
            recoupment_basis=RecoupmentBasis.REMAINING_POOL,
            fixed_amount=None,
            percentage_of_receipts=Decimal("100"),
            capped_at=None,
        ),
        # Backend/Profit participation
        WaterfallNode(
            node_id="backend",
            description="Backend Participation",
            priority=RecoupmentPriority.BACKEND_PARTICIPATION,
            payee_type=PayeeType.TALENT,
            payee_name="Producer",
            recoupment_basis=RecoupmentBasis.REMAINING_POOL,
            fixed_amount=None,
            percentage_of_receipts=Decimal("50"),
            capped_at=None,
        ),
    ]

    return WaterfallStructure(
        waterfall_id=waterfall_id,
        project_id=project_id,
        waterfall_name="Standard Waterfall",
        default_distribution_fee_rate=Decimal("30.0"),
        nodes=nodes,
    )


def _build_distribution_timeline(distributions: Dict) -> list[QuarterlyDistribution]:
    """Build quarterly distribution timeline from waterfall results."""
    # This is a simplified version - in production, you'd aggregate by quarter
    timeline = []

    # For now, return sample quarterly data
    # In production, you would aggregate distributions by quarter
    for quarter in range(1, 9):
        timeline.append(
            QuarterlyDistribution(
                quarter=quarter,
                distributions={
                    "senior-debt": Decimal("0"),
                    "gap-financing": Decimal("0"),
                    "mezzanine": Decimal("0"),
                    "equity": Decimal("0"),
                    "backend": Decimal("0"),
                },
            )
        )

    return timeline


def _run_monte_carlo_simulation(
    capital_stack: CapitalStack,
    waterfall_structure: WaterfallStructure,
    base_projection: "RevenueProjection",
    iterations: int,
) -> MonteCarloResults:
    """Run Monte Carlo simulation for risk analysis."""
    from engines.waterfall_executor.monte_carlo_simulator import MonteCarloSimulator

    simulator = MonteCarloSimulator(
        capital_stack=capital_stack,
        waterfall_structure=waterfall_structure,
        base_projection=base_projection,
    )

    results = simulator.run_simulation(num_iterations=iterations)

    # Extract equity IRR percentiles
    equity_irr_percentiles = MonteCarloPercentiles(
        p10=results["equity_irr"]["p10"],
        p50=results["equity_irr"]["p50"],
        p90=results["equity_irr"]["p90"],
    )

    # Extract probability of recoupment
    probability_of_recoupment = {
        stakeholder_id: Decimal(str(prob))
        for stakeholder_id, prob in results["probability_of_recoupment"].items()
    }

    return MonteCarloResults(
        equity_irr=equity_irr_percentiles,
        probability_of_recoupment=probability_of_recoupment,
    )


@router.post(
    "/sensitivity-analysis",
    response_model=SensitivityAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Sensitivity Analysis",
    description="Perform sensitivity analysis to identify which variables have the biggest impact on returns (tornado charts)",
)
async def sensitivity_analysis(request: SensitivityAnalysisRequest):
    """
    Run sensitivity analysis on waterfall returns.

    This endpoint:
    1. Creates base case revenue projection
    2. Defines variables to test (revenue, interest rates, timing, etc.)
    3. Runs waterfall for base/low/high scenarios for each variable
    4. Calculates impact on target metrics (e.g., equity IRR)
    5. Returns tornado chart data showing variable impacts

    Args:
        request: Sensitivity analysis parameters

    Returns:
        Sensitivity results with tornado chart data for visualization

    Raises:
        HTTPException: If analysis fails or validation errors occur
    """
    try:
        # Create sample capital stack and waterfall structure
        capital_stack = _create_sample_capital_stack(request.project_id)
        waterfall_structure = _create_sample_waterfall(
            request.project_id, request.waterfall_id
        )

        # Initialize revenue projector
        revenue_projector = RevenueProjector()

        # Project base case revenue
        base_projection = revenue_projector.project(
            total_ultimate_revenue=request.base_total_revenue,
            release_strategy=request.release_strategy,
        )

        # Prepare sensitivity variables
        if request.custom_variables:
            # Use custom variables provided by user
            sensitivity_variables = [
                SensitivityVariable(
                    variable_name=var.variable_name,
                    base_value=var.base_value,
                    low_value=var.low_value,
                    high_value=var.high_value,
                    variable_type=var.variable_type,
                )
                for var in request.custom_variables
            ]
        else:
            # Auto-generate standard variables with variation percentage
            variation_pct = request.variation_percentage / Decimal("100")

            # Revenue multiplier
            revenue_low = request.base_total_revenue * (Decimal("1") - variation_pct)
            revenue_high = request.base_total_revenue * (Decimal("1") + variation_pct)

            sensitivity_variables = [
                SensitivityVariable(
                    variable_name="revenue_multiplier",
                    base_value=request.base_total_revenue,
                    low_value=revenue_low,
                    high_value=revenue_high,
                    variable_type="revenue",
                )
            ]

        # Initialize sensitivity analyzer
        analyzer = SensitivityAnalyzer(
            waterfall_structure=waterfall_structure,
            capital_stack=capital_stack,
            base_revenue_projection=base_projection,
        )

        # Run sensitivity analysis
        sensitivity_results = analyzer.analyze(
            variables=sensitivity_variables,
            target_metrics=request.target_metrics,
        )

        # Build response data
        results_by_metric = {}
        tornado_charts = {}

        for metric, results in sensitivity_results.items():
            # Convert SensitivityResult objects to SensitivityResultData schemas
            result_data_list = []
            for result in results:
                result_data_list.append(
                    SensitivityResultData(
                        variable_name=result.variable.variable_name,
                        variable_type=result.variable.variable_type,
                        base_value=result.variable.base_value,
                        low_value=result.variable.low_value,
                        high_value=result.variable.high_value,
                        base_case_metric=result.base_case[metric],
                        low_case_metric=result.low_case[metric],
                        high_case_metric=result.high_case[metric],
                        delta_low=result.delta_low[metric],
                        delta_high=result.delta_high[metric],
                        impact_score=result.impact_score,
                    )
                )
            results_by_metric[metric] = result_data_list

            # Generate tornado chart data
            tornado_data = analyzer.generate_tornado_chart_data(results, metric)
            tornado_charts[metric] = TornadoChartDataSchema(
                target_metric=tornado_data.target_metric,
                variables=tornado_data.variables,
                base_value=tornado_data.base_value,
                low_deltas=tornado_data.low_deltas,
                high_deltas=tornado_data.high_deltas,
            )

        return SensitivityAnalysisResponse(
            project_id=request.project_id,
            base_total_revenue=request.base_total_revenue,
            target_metrics=request.target_metrics,
            results_by_metric=results_by_metric,
            tornado_charts=tornado_charts,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sensitivity analysis failed: {str(e)}",
        )
