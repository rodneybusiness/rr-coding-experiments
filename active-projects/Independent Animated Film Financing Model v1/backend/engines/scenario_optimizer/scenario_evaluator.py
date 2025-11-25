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

# Engine 4 imports (Ownership & Control)
from backend.engines.scenario_optimizer.ownership_control_scorer import (
    OwnershipControlScorer,
    OwnershipControlResult
)

# DealBlock model
from backend.models.deal_block import DealBlock

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

    # Ownership & Control Metrics (from Engine 4)
    ownership_score: Optional[Decimal] = None
    control_score: Optional[Decimal] = None
    optionality_score: Optional[Decimal] = None
    friction_score: Optional[Decimal] = None
    strategic_composite_score: Optional[Decimal] = None
    ownership_control_impacts: List[Dict] = field(default_factory=list)
    strategic_recommendations: List[str] = field(default_factory=list)
    has_mfn_risk: bool = False
    has_control_concentration: bool = False
    has_reversion_opportunity: bool = False

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
        num_simulations: int = 1000,
        deal_blocks: Optional[List[DealBlock]] = None
    ) -> ScenarioEvaluation:
        """
        Evaluate financing scenario comprehensively.

        Args:
            capital_stack: CapitalStack to evaluate
            waterfall_structure: WaterfallStructure for distributions
            revenue_projection: Total ultimate revenue (uses base if None)
            run_monte_carlo: Whether to run Monte Carlo simulation
            num_simulations: Number of Monte Carlo scenarios
            deal_blocks: Optional list of DealBlocks for ownership/control scoring

        Returns:
            ScenarioEvaluation with complete metrics (financial + strategic)
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

        # 7. Score ownership & control if deal blocks provided (Engine 4)
        if deal_blocks:
            self._evaluate_ownership_control(deal_blocks, evaluation)

        # 8. Calculate overall score (now includes ownership if available)
        self._calculate_overall_score(evaluation)

        # 9. Identify strengths and weaknesses
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
                # Pre-sale cost = sales agent commission
                cost = instrument.sales_agent_commission if hasattr(instrument, 'sales_agent_commission') else Decimal("15.0")
                weighted_cost += weight * cost

            elif isinstance(instrument, TaxIncentive):
                # Tax incentive = negative cost (benefit)
                # Assume net cost of -5% (after monetization costs)
                cost = Decimal("-5.0")
                weighted_cost += weight * cost

        evaluation.weighted_cost_of_capital = weighted_cost
        evaluation.total_interest_expense = total_interest
        evaluation.total_fees = total_fees

    def _evaluate_ownership_control(
        self,
        deal_blocks: List[DealBlock],
        evaluation: ScenarioEvaluation
    ):
        """
        Score ownership & control using Engine 4 (OwnershipControlScorer).

        Adds strategic metrics beyond financial returns:
        - Ownership score: How much IP/revenue rights retained
        - Control score: Creative and business control retained
        - Optionality score: Future flexibility preserved
        - Friction score: Execution complexity/risk
        """
        try:
            scorer = OwnershipControlScorer()
            result = scorer.score_scenario(deal_blocks)

            # Populate evaluation with ownership/control metrics
            evaluation.ownership_score = result.ownership_score
            evaluation.control_score = result.control_score
            evaluation.optionality_score = result.optionality_score
            evaluation.friction_score = result.friction_score
            evaluation.strategic_composite_score = result.composite_score

            # Add explainability data
            evaluation.ownership_control_impacts = [
                {
                    "source": impact.source,
                    "dimension": impact.dimension,
                    "impact": impact.impact,
                    "explanation": impact.explanation
                }
                for impact in result.impacts
            ]
            evaluation.strategic_recommendations = result.recommendations

            # Set risk flags
            evaluation.has_mfn_risk = result.has_mfn_risk
            evaluation.has_control_concentration = result.has_control_concentration
            evaluation.has_reversion_opportunity = result.has_reversion_opportunity

            logger.info(
                f"Ownership scoring complete - "
                f"O:{result.ownership_score} C:{result.control_score} "
                f"Op:{result.optionality_score} F:{result.friction_score} "
                f"Composite:{result.composite_score:.1f}"
            )

        except Exception as e:
            logger.warning(f"Ownership/control scoring failed: {e}")

    def _calculate_overall_score(self, evaluation: ScenarioEvaluation):
        """
        Calculate composite score (0-100).

        Financial factors (when no deal blocks):
        - Equity IRR (30%): Higher is better
        - Tax incentives (20%): Higher is better
        - Risk (20%): Lower risk is better (P(recoupment) high)
        - Cost of capital (15%): Lower is better
        - Debt recovery (15%): Higher is better

        When deal blocks provided, blends financial (70%) with strategic (30%):
        - Financial score: 70 points (scaled from above)
        - Strategic composite: 30 points (from ownership/control scorer)
        """
        financial_score = Decimal("0")

        # Factor 1: Equity IRR (30 points base)
        if evaluation.equity_irr:
            # Target 20% IRR = full points
            irr_score = min(evaluation.equity_irr / Decimal("20.0"), Decimal("1.0"))
            financial_score += irr_score * Decimal("30")

        # Factor 2: Tax Incentives (20 points base)
        # Target 20% of budget = full points
        incentive_score = min(evaluation.tax_incentive_effective_rate / Decimal("20.0"), Decimal("1.0"))
        financial_score += incentive_score * Decimal("20")

        # Factor 3: Risk (20 points base)
        # P(recoupment) > 80% = full points
        risk_score = min(evaluation.probability_of_equity_recoupment / Decimal("0.80"), Decimal("1.0"))
        financial_score += risk_score * Decimal("20")

        # Factor 4: Cost of Capital (15 points base)
        # Lower WACC is better. Target 12% = full points
        if evaluation.weighted_cost_of_capital > 0:
            cost_score = Decimal("12.0") / evaluation.weighted_cost_of_capital
            cost_score = min(cost_score, Decimal("1.0"))
            financial_score += cost_score * Decimal("15")

        # Factor 5: Debt Recovery (15 points base)
        # 100% recovery = full points
        debt_score = min(evaluation.senior_debt_recovery_rate / Decimal("100.0"), Decimal("1.0"))
        financial_score += debt_score * Decimal("15")

        # Blend with strategic score if ownership/control metrics available
        if evaluation.strategic_composite_score is not None:
            # Financial contributes 70%, Strategic contributes 30%
            strategic_score = evaluation.strategic_composite_score * Decimal("0.30")
            financial_weighted = financial_score * Decimal("0.70")
            evaluation.overall_score = financial_weighted + strategic_score
        else:
            # No deal blocks: use pure financial score
            evaluation.overall_score = financial_score

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

        # Ownership & Control (if deal blocks were evaluated)
        if evaluation.ownership_score is not None:
            # Ownership
            if evaluation.ownership_score >= Decimal("80"):
                strengths.append(f"Strong IP ownership retention ({evaluation.ownership_score:.0f}/100)")
            elif evaluation.ownership_score < Decimal("50"):
                weaknesses.append(f"Significant ownership dilution ({evaluation.ownership_score:.0f}/100)")

            # Control
            if evaluation.control_score is not None:
                if evaluation.control_score >= Decimal("80"):
                    strengths.append(f"High creative control retained ({evaluation.control_score:.0f}/100)")
                elif evaluation.control_score < Decimal("50"):
                    weaknesses.append(f"Limited creative control ({evaluation.control_score:.0f}/100)")

            # Optionality
            if evaluation.optionality_score is not None:
                if evaluation.optionality_score >= Decimal("80"):
                    strengths.append(f"Strong future optionality ({evaluation.optionality_score:.0f}/100)")
                elif evaluation.optionality_score < Decimal("50"):
                    weaknesses.append(f"Limited future flexibility ({evaluation.optionality_score:.0f}/100)")

            # Friction (lower is better)
            if evaluation.friction_score is not None:
                if evaluation.friction_score <= Decimal("30"):
                    strengths.append(f"Low execution complexity ({evaluation.friction_score:.0f}/100)")
                elif evaluation.friction_score >= Decimal("60"):
                    weaknesses.append(f"High execution complexity ({evaluation.friction_score:.0f}/100)")

            # Risk flags
            if evaluation.has_mfn_risk:
                weaknesses.append("MFN clause limits deal flexibility")
            if evaluation.has_control_concentration:
                weaknesses.append("Control concentration risk (>40% to single party)")
            if evaluation.has_reversion_opportunity:
                strengths.append("Rights reversion opportunity exists")

        evaluation.strengths = strengths
        evaluation.weaknesses = weaknesses

    def evaluate_for_program(
        self,
        capital_stack: CapitalStack,
        waterfall_structure: WaterfallStructure,
        program_context: "CapitalProgramContext",
        deal_blocks: Optional[List[DealBlock]] = None,
        run_monte_carlo: bool = True,
        num_simulations: int = 1000
    ) -> "ProgramScenarioEvaluation":
        """
        Evaluate a financing scenario in the context of a capital program.

        Extends standard evaluation with program-specific considerations:
        - Constraint compliance checking
        - Portfolio fit analysis
        - Source selection optimization
        - Risk contribution to portfolio

        Args:
            capital_stack: CapitalStack to evaluate
            waterfall_structure: WaterfallStructure for distributions
            program_context: Context including program constraints and portfolio state
            deal_blocks: Optional list of DealBlocks for ownership/control scoring
            run_monte_carlo: Whether to run Monte Carlo simulation
            num_simulations: Number of Monte Carlo scenarios

        Returns:
            ProgramScenarioEvaluation with standard metrics plus program-specific analysis
        """
        # First, run standard evaluation
        base_evaluation = self.evaluate(
            capital_stack=capital_stack,
            waterfall_structure=waterfall_structure,
            revenue_projection=program_context.expected_revenue,
            run_monte_carlo=run_monte_carlo,
            num_simulations=num_simulations,
            deal_blocks=deal_blocks
        )

        # Check program constraints
        constraint_violations = []
        constraint_warnings = []

        if program_context.constraints:
            constraints = program_context.constraints

            # Check single project concentration
            if program_context.total_committed > 0:
                project_pct = (capital_stack.project_budget / program_context.total_committed) * Decimal("100")
                if project_pct > constraints.get("max_single_project_pct", Decimal("100")):
                    constraint_violations.append({
                        "constraint": "max_single_project_pct",
                        "current": str(project_pct),
                        "limit": str(constraints.get("max_single_project_pct")),
                        "blocking": True
                    })

            # Check budget range
            min_budget = constraints.get("min_project_budget")
            max_budget = constraints.get("max_project_budget")
            if min_budget and capital_stack.project_budget < min_budget:
                constraint_violations.append({
                    "constraint": "min_project_budget",
                    "current": str(capital_stack.project_budget),
                    "limit": str(min_budget),
                    "blocking": True
                })
            if max_budget and capital_stack.project_budget > max_budget:
                constraint_violations.append({
                    "constraint": "max_project_budget",
                    "current": str(capital_stack.project_budget),
                    "limit": str(max_budget),
                    "blocking": True
                })

            # Check prohibited jurisdictions
            prohibited = constraints.get("prohibited_jurisdictions", [])
            if program_context.jurisdiction and program_context.jurisdiction in prohibited:
                constraint_violations.append({
                    "constraint": "prohibited_jurisdiction",
                    "current": program_context.jurisdiction,
                    "limit": str(prohibited),
                    "blocking": True
                })

            # Check development stage limits (soft constraint / warning)
            if program_context.is_development:
                max_dev_pct = constraints.get("max_development_pct", Decimal("100"))
                current_dev_pct = program_context.current_development_pct or Decimal("0")
                if current_dev_pct >= max_dev_pct:
                    constraint_warnings.append(
                        f"Development allocation at limit ({current_dev_pct}% of {max_dev_pct}% max)"
                    )

        # Calculate portfolio fit score
        portfolio_fit_score = self._calculate_portfolio_fit(
            base_evaluation, program_context
        )

        # Recommend optimal source
        recommended_source = None
        source_rationale = None
        if program_context.available_sources:
            recommended_source, source_rationale = self._recommend_source(
                capital_stack, program_context
            )

        return ProgramScenarioEvaluation(
            base_evaluation=base_evaluation,
            program_id=program_context.program_id,
            constraint_violations=constraint_violations,
            constraint_warnings=constraint_warnings,
            passes_hard_constraints=len(constraint_violations) == 0,
            portfolio_fit_score=portfolio_fit_score,
            recommended_source_id=recommended_source,
            source_selection_rationale=source_rationale,
            expected_portfolio_contribution={
                "irr_contribution": base_evaluation.equity_irr or Decimal("0"),
                "risk_contribution": Decimal("100") - base_evaluation.probability_of_equity_recoupment * Decimal("100"),
                "strategic_contribution": base_evaluation.strategic_composite_score or Decimal("50")
            }
        )

    def _calculate_portfolio_fit(
        self,
        evaluation: ScenarioEvaluation,
        context: "CapitalProgramContext"
    ) -> Decimal:
        """
        Calculate how well this project fits the portfolio.

        Considers:
        - Return profile alignment with targets
        - Risk diversification benefit
        - Strategic value add
        """
        fit_score = Decimal("50")  # Base score

        # Return alignment (+/- 25 points)
        if context.target_irr and evaluation.equity_irr:
            irr_diff = abs(evaluation.equity_irr - context.target_irr)
            if irr_diff <= Decimal("5"):
                fit_score += Decimal("25")
            elif irr_diff <= Decimal("10"):
                fit_score += Decimal("15")
            else:
                fit_score -= Decimal("10")

        # Risk contribution (+/- 15 points)
        if evaluation.probability_of_equity_recoupment >= Decimal("0.80"):
            fit_score += Decimal("15")
        elif evaluation.probability_of_equity_recoupment < Decimal("0.50"):
            fit_score -= Decimal("15")

        # Strategic value (+/- 10 points)
        if evaluation.strategic_composite_score:
            if evaluation.strategic_composite_score >= Decimal("70"):
                fit_score += Decimal("10")
            elif evaluation.strategic_composite_score < Decimal("40"):
                fit_score -= Decimal("10")

        return max(Decimal("0"), min(Decimal("100"), fit_score))

    def _recommend_source(
        self,
        capital_stack: CapitalStack,
        context: "CapitalProgramContext"
    ) -> tuple:
        """
        Recommend the best capital source for this project.

        Selection criteria:
        1. Geographic restrictions match
        2. Budget range fit
        3. Available capacity
        4. Cost of capital
        """
        if not context.available_sources:
            return None, None

        best_source = None
        best_score = Decimal("-999")
        best_rationale = None

        for source in context.available_sources:
            score = Decimal("0")
            rationale_parts = []

            # Check geographic restrictions
            if source.get("geographic_restrictions"):
                if context.jurisdiction in source["geographic_restrictions"]:
                    score += Decimal("30")
                    rationale_parts.append("Jurisdiction match")
                else:
                    score -= Decimal("100")  # Disqualify
                    continue

            # Check budget range
            min_budget = source.get("budget_range_min")
            max_budget = source.get("budget_range_max")
            if min_budget and capital_stack.project_budget < min_budget:
                continue
            if max_budget and capital_stack.project_budget > max_budget:
                continue
            rationale_parts.append("Budget in range")
            score += Decimal("20")

            # Check available capacity
            available = source.get("available_amount", Decimal("0"))
            if available >= capital_stack.project_budget:
                score += Decimal("25")
                rationale_parts.append("Full capacity available")
            elif available >= capital_stack.project_budget * Decimal("0.5"):
                score += Decimal("10")
                rationale_parts.append("Partial capacity available")

            # Prefer lower cost sources
            interest_rate = source.get("interest_rate", Decimal("10"))
            if interest_rate <= Decimal("8"):
                score += Decimal("15")
                rationale_parts.append("Competitive cost")

            if score > best_score:
                best_score = score
                best_source = source.get("source_id")
                best_rationale = "; ".join(rationale_parts)

        return best_source, best_rationale


@dataclass
class CapitalProgramContext:
    """
    Context for evaluating a scenario within a capital program.
    """
    program_id: str
    program_name: str
    total_committed: Decimal = Decimal("0")
    total_deployed: Decimal = Decimal("0")
    target_irr: Optional[Decimal] = None
    constraints: Optional[Dict[str, Any]] = None
    available_sources: Optional[List[Dict[str, Any]]] = None
    jurisdiction: Optional[str] = None
    genre: Optional[str] = None
    is_development: bool = False
    is_first_time_director: bool = False
    current_development_pct: Optional[Decimal] = None
    expected_revenue: Optional[Decimal] = None


@dataclass
class ProgramScenarioEvaluation:
    """
    Extended evaluation result including program-specific analysis.
    """
    base_evaluation: ScenarioEvaluation
    program_id: str

    # Constraint analysis
    constraint_violations: List[Dict[str, Any]] = field(default_factory=list)
    constraint_warnings: List[str] = field(default_factory=list)
    passes_hard_constraints: bool = True

    # Portfolio analysis
    portfolio_fit_score: Decimal = Decimal("50")

    # Source recommendation
    recommended_source_id: Optional[str] = None
    source_selection_rationale: Optional[str] = None

    # Portfolio contribution
    expected_portfolio_contribution: Dict[str, Decimal] = field(default_factory=dict)
