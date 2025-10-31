"""
Scenario Evaluator

Evaluates financing scenarios by integrating Engine 1 (Incentive Calculator)
and Engine 2 (Waterfall Execution) to produce comprehensive financial metrics.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal

from backend.models.capital_stack import CapitalStack
from backend.models.waterfall import WaterfallStructure, WaterfallNode, RecoupmentPriority
from backend.models.financial_instruments import TaxIncentive, Debt, Equity, PreSale

# Engine 1 imports
from backend.engines.incentive_calculator import (
    IncentiveCalculator,
    JurisdictionSpend
)

# Engine 2 imports
from backend.engines.waterfall_executor import (
    RevenueProjector,
    WaterfallExecutor,
    StakeholderAnalyzer,
    MonteCarloSimulator,
    RevenueDistribution
)

logger = logging.getLogger(__name__)


@dataclass
class ScenarioEvaluation:
    """
    Comprehensive evaluation of a financing scenario.

    Attributes:
        scenario_name: Scenario identifier
        capital_stack: Capital stack being evaluated

        # Tax Incentive Metrics (from Engine 1)
        tax_incentive_gross_credit: Total gross tax credit
        tax_incentive_net_benefit: Net cash benefit after discounts
        tax_incentive_effective_rate: Effective incentive rate

        # Waterfall Metrics (from Engine 2)
        total_revenue_projected: Total ultimate revenue projection
        stakeholder_irrs: Dict of stakeholder → IRR
        stakeholder_cash_on_cash: Dict of stakeholder → cash-on-cash multiple
        equity_irr: Average equity IRR
        senior_debt_recovery_rate: Senior debt recovery %

        # Risk Metrics (from Engine 2 Monte Carlo)
        probability_of_equity_recoupment: P(equity fully recoups)
        equity_irr_p10: 10th percentile IRR
        equity_irr_p50: 50th percentile IRR (median)
        equity_irr_p90: 90th percentile IRR

        # Cost Metrics
        weighted_cost_of_capital: WACC estimate
        total_interest_expense: Total debt interest
        total_fees: All financing fees

        # Summary Metrics
        overall_score: Composite score (0-100)
        strengths: List of strengths
        weaknesses: List of weaknesses

        metadata: Additional evaluation data
    """
    scenario_name: str
    capital_stack: CapitalStack

    # Tax Incentive Metrics
    tax_incentive_gross_credit: Decimal = Decimal("0")
    tax_incentive_net_benefit: Decimal = Decimal("0")
    tax_incentive_effective_rate: Decimal = Decimal("0")

    # Waterfall Metrics
    total_revenue_projected: Decimal = Decimal("0")
    stakeholder_irrs: Dict[str, Decimal] = field(default_factory=dict)
    stakeholder_cash_on_cash: Dict[str, Decimal] = field(default_factory=dict)
    equity_irr: Optional[Decimal] = None
    senior_debt_recovery_rate: Decimal = Decimal("0")

    # Risk Metrics
    probability_of_equity_recoupment: Decimal = Decimal("0")
    equity_irr_p10: Optional[Decimal] = None
    equity_irr_p50: Optional[Decimal] = None
    equity_irr_p90: Optional[Decimal] = None

    # Cost Metrics
    weighted_cost_of_capital: Decimal = Decimal("0")
    total_interest_expense: Decimal = Decimal("0")
    total_fees: Decimal = Decimal("0")

    # Summary
    overall_score: Decimal = Decimal("0")
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


class ScenarioEvaluator:
    """
    Evaluate financing scenarios using Engines 1 & 2.

    Integrates tax incentive calculation, waterfall execution, and risk analysis
    to produce comprehensive financial metrics for scenario comparison.
    """

    def __init__(
        self,
        base_revenue_projection: Decimal = Decimal("75000000"),
        discount_rate: Decimal = Decimal("0.12")
    ):
        """
        Initialize evaluator.

        Args:
            base_revenue_projection: Default total ultimate revenue
            discount_rate: Discount rate for NPV (12% default)
        """
        self.base_revenue_projection = base_revenue_projection
        self.discount_rate = discount_rate

        logger.info(f"ScenarioEvaluator initialized (base revenue: ${base_revenue_projection:,.0f})")

    def evaluate(
        self,
        capital_stack: CapitalStack,
        waterfall_structure: WaterfallStructure,
        revenue_projection: Optional[Decimal] = None,
        run_monte_carlo: bool = True,
        num_simulations: int = 1000
    ) -> ScenarioEvaluation:
        """
        Evaluate financing scenario comprehensively.

        Args:
            capital_stack: CapitalStack to evaluate
            waterfall_structure: WaterfallStructure for distributions
            revenue_projection: Total ultimate revenue (uses base if None)
            run_monte_carlo: Whether to run Monte Carlo simulation
            num_simulations: Number of Monte Carlo scenarios

        Returns:
            ScenarioEvaluation with complete metrics
        """
        scenario_name = capital_stack.stack_name
        logger.info(f"Evaluating scenario: {scenario_name}")

        evaluation = ScenarioEvaluation(
            scenario_name=scenario_name,
            capital_stack=capital_stack
        )

        revenue = revenue_projection or self.base_revenue_projection
        evaluation.total_revenue_projected = revenue

        # 1. Calculate tax incentives (Engine 1)
        self._evaluate_tax_incentives(capital_stack, evaluation)

        # 2. Project revenue (Engine 2)
        projector = RevenueProjector()
        rev_projection = projector.project(
            total_ultimate_revenue=revenue,
            release_strategy="wide_theatrical",
            project_name=scenario_name
        )

        # 3. Execute waterfall (Engine 2)
        executor = WaterfallExecutor(waterfall_structure)
        waterfall_result = executor.execute_over_time(rev_projection)

        # 4. Analyze stakeholders (Engine 2)
        analyzer = StakeholderAnalyzer(capital_stack, discount_rate=self.discount_rate)
        stakeholder_analysis = analyzer.analyze(waterfall_result)

        # Extract stakeholder metrics
        for stakeholder in stakeholder_analysis.stakeholders:
            if stakeholder.irr:
                evaluation.stakeholder_irrs[stakeholder.stakeholder_id] = stakeholder.irr
            evaluation.stakeholder_cash_on_cash[stakeholder.stakeholder_id] = stakeholder.cash_on_cash

        # Calculate average equity IRR
        equity_irrs = [
            s.irr for s in stakeholder_analysis.stakeholders
            if "equity" in s.stakeholder_type.lower() and s.irr is not None
        ]
        if equity_irrs:
            evaluation.equity_irr = sum(equity_irrs) / Decimal(str(len(equity_irrs)))

        # Calculate senior debt recovery
        senior_debt_stakeholders = [
            s for s in stakeholder_analysis.stakeholders
            if "senior" in s.stakeholder_type.lower()
        ]
        if senior_debt_stakeholders:
            total_invested = sum(s.initial_investment for s in senior_debt_stakeholders)
            total_recovered = sum(s.total_receipts for s in senior_debt_stakeholders)
            if total_invested > 0:
                evaluation.senior_debt_recovery_rate = (total_recovered / total_invested) * Decimal("100")

        # 5. Run Monte Carlo if requested (Engine 2)
        if run_monte_carlo:
            self._run_monte_carlo_analysis(
                waterfall_structure,
                capital_stack,
                rev_projection,
                revenue,
                evaluation,
                num_simulations
            )

        # 6. Calculate cost metrics
        self._calculate_cost_metrics(capital_stack, evaluation)

        # 7. Calculate overall score
        self._calculate_overall_score(evaluation)

        # 8. Identify strengths and weaknesses
        self._identify_strengths_weaknesses(evaluation)

        logger.info(f"Evaluation complete. Score: {evaluation.overall_score:.1f}/100")

        return evaluation

    def _evaluate_tax_incentives(
        self,
        capital_stack: CapitalStack,
        evaluation: ScenarioEvaluation
    ):
        """Calculate tax incentive metrics using Engine 1."""
        tax_incentive_components = [
            c.instrument for c in capital_stack.components
            if isinstance(c.instrument, TaxIncentive)
        ]

        if not tax_incentive_components:
            return

        # Sum up tax incentive benefits
        gross_credit = sum(ti.amount for ti in tax_incentive_components)
        evaluation.tax_incentive_gross_credit = gross_credit

        # Estimate net benefit (assume 20% discount for monetization)
        discount_rate = Decimal("0.20")
        net_benefit = gross_credit * (Decimal("1") - discount_rate)
        evaluation.tax_incentive_net_benefit = net_benefit

        # Calculate effective rate
        if capital_stack.project_budget > 0:
            evaluation.tax_incentive_effective_rate = (gross_credit / capital_stack.project_budget) * Decimal("100")

    def _run_monte_carlo_analysis(
        self,
        waterfall_structure: WaterfallStructure,
        capital_stack: CapitalStack,
        base_projection: Any,
        base_revenue: Decimal,
        evaluation: ScenarioEvaluation,
        num_simulations: int
    ):
        """Run Monte Carlo simulation for risk analysis."""
        try:
            # Define revenue distribution (triangular: -25% to +50%)
            revenue_dist = RevenueDistribution(
                variable_name="total_revenue",
                distribution_type="triangular",
                parameters={
                    "min": base_revenue * Decimal("0.75"),
                    "mode": base_revenue,
                    "max": base_revenue * Decimal("1.50")
                }
            )

            # Run simulation
            simulator = MonteCarloSimulator(
                waterfall_structure,
                capital_stack,
                base_projection
            )

            mc_result = simulator.simulate(revenue_dist, num_simulations=num_simulations, seed=42)

            # Extract equity metrics
            equity_stakeholder_ids = [
                sid for sid, percentiles in mc_result.stakeholder_percentiles.items()
                if "equity" in sid.lower()
            ]

            if equity_stakeholder_ids:
                # Use first equity stakeholder (or average if multiple)
                equity_id = equity_stakeholder_ids[0]
                percentiles = mc_result.stakeholder_percentiles[equity_id]

                evaluation.equity_irr_p10 = percentiles.get("irr_p10")
                evaluation.equity_irr_p50 = percentiles.get("irr_p50")
                evaluation.equity_irr_p90 = percentiles.get("irr_p90")

                # Probability of recoupment
                evaluation.probability_of_equity_recoupment = mc_result.probability_of_recoupment.get(
                    equity_id,
                    Decimal("0")
                )

            logger.info(f"Monte Carlo complete: {num_simulations} simulations")

        except Exception as e:
            logger.warning(f"Monte Carlo simulation failed: {e}")

    def _calculate_cost_metrics(
        self,
        capital_stack: CapitalStack,
        evaluation: ScenarioEvaluation
    ):
        """Calculate cost of capital metrics."""
        total_capital = capital_stack.project_budget
        weighted_cost = Decimal("0")
        total_interest = Decimal("0")
        total_fees = Decimal("0")

        for component in capital_stack.components:
            instrument = component.instrument
            amount = instrument.amount
            weight = amount / total_capital

            if isinstance(instrument, Debt):
                # Debt cost = interest rate
                cost = instrument.interest_rate
                weighted_cost += weight * cost

                # Calculate interest expense
                term_years = Decimal(str(instrument.term_months)) / Decimal("12")
                interest = amount * (instrument.interest_rate / Decimal("100")) * term_years
                total_interest += interest

                # Add origination fees if present
                if hasattr(instrument, "origination_fee_percentage"):
                    fee = amount * (instrument.origination_fee_percentage / Decimal("100"))
                    total_fees += fee

            elif isinstance(instrument, Equity):
                # Equity cost = target return (assume 20%)
                cost = Decimal("20.0")
                weighted_cost += weight * cost

            elif isinstance(instrument, PreSale):
                # Pre-sale cost = discount rate
                cost = instrument.discount_rate
                weighted_cost += weight * cost

            elif isinstance(instrument, TaxIncentive):
                # Tax incentive = negative cost (benefit)
                # Assume net cost of -5% (after monetization costs)
                cost = Decimal("-5.0")
                weighted_cost += weight * cost

        evaluation.weighted_cost_of_capital = weighted_cost
        evaluation.total_interest_expense = total_interest
        evaluation.total_fees = total_fees

    def _calculate_overall_score(self, evaluation: ScenarioEvaluation):
        """
        Calculate composite score (0-100).

        Weighted factors:
        - Equity IRR (30%): Higher is better
        - Tax incentives (20%): Higher is better
        - Risk (20%): Lower risk is better (P(recoupment) high)
        - Cost of capital (15%): Lower is better
        - Debt recovery (15%): Higher is better
        """
        score = Decimal("0")

        # Factor 1: Equity IRR (30 points)
        if evaluation.equity_irr:
            # Target 20% IRR = full points
            irr_score = min(evaluation.equity_irr / Decimal("20.0"), Decimal("1.0"))
            score += irr_score * Decimal("30")

        # Factor 2: Tax Incentives (20 points)
        # Target 20% of budget = full points
        incentive_score = min(evaluation.tax_incentive_effective_rate / Decimal("20.0"), Decimal("1.0"))
        score += incentive_score * Decimal("20")

        # Factor 3: Risk (20 points)
        # P(recoupment) > 80% = full points
        risk_score = min(evaluation.probability_of_equity_recoupment / Decimal("0.80"), Decimal("1.0"))
        score += risk_score * Decimal("20")

        # Factor 4: Cost of Capital (15 points)
        # Lower WACC is better. Target 12% = full points
        if evaluation.weighted_cost_of_capital > 0:
            cost_score = Decimal("12.0") / evaluation.weighted_cost_of_capital
            cost_score = min(cost_score, Decimal("1.0"))
            score += cost_score * Decimal("15")

        # Factor 5: Debt Recovery (15 points)
        # 100% recovery = full points
        debt_score = min(evaluation.senior_debt_recovery_rate / Decimal("100.0"), Decimal("1.0"))
        score += debt_score * Decimal("15")

        evaluation.overall_score = score

    def _identify_strengths_weaknesses(self, evaluation: ScenarioEvaluation):
        """Identify scenario strengths and weaknesses."""
        strengths = []
        weaknesses = []

        # Equity IRR
        if evaluation.equity_irr:
            if evaluation.equity_irr >= Decimal("25.0"):
                strengths.append(f"Excellent equity returns (IRR: {evaluation.equity_irr:.1f}%)")
            elif evaluation.equity_irr < Decimal("15.0"):
                weaknesses.append(f"Low equity returns (IRR: {evaluation.equity_irr:.1f}%)")

        # Tax Incentives
        if evaluation.tax_incentive_effective_rate >= Decimal("20.0"):
            strengths.append(f"Strong tax incentive capture ({evaluation.tax_incentive_effective_rate:.1f}%)")
        elif evaluation.tax_incentive_effective_rate < Decimal("10.0"):
            weaknesses.append("Limited tax incentive utilization")

        # Risk
        if evaluation.probability_of_equity_recoupment >= Decimal("0.80"):
            strengths.append(f"High probability of equity recoupment ({evaluation.probability_of_equity_recoupment * Decimal('100'):.0f}%)")
        elif evaluation.probability_of_equity_recoupment < Decimal("0.50"):
            weaknesses.append(f"Low probability of equity recoupment ({evaluation.probability_of_equity_recoupment * Decimal('100'):.0f}%)")

        # Cost of Capital
        if evaluation.weighted_cost_of_capital <= Decimal("12.0"):
            strengths.append(f"Low cost of capital ({evaluation.weighted_cost_of_capital:.1f}%)")
        elif evaluation.weighted_cost_of_capital >= Decimal("18.0"):
            weaknesses.append(f"High cost of capital ({evaluation.weighted_cost_of_capital:.1f}%)")

        # Debt Recovery
        if evaluation.senior_debt_recovery_rate >= Decimal("100.0"):
            strengths.append("Full senior debt recovery")
        elif evaluation.senior_debt_recovery_rate < Decimal("80.0"):
            weaknesses.append(f"Weak debt coverage ({evaluation.senior_debt_recovery_rate:.0f}%)")

        evaluation.strengths = strengths
        evaluation.weaknesses = weaknesses
