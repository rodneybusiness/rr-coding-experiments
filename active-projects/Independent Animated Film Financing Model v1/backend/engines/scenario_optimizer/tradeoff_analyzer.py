"""
Trade-Off Analyzer

Identifies Pareto frontier and analyzes trade-offs between competing objectives
(e.g., equity ownership vs. risk, tax incentives vs. cost of capital).
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from backend.engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluation

logger = logging.getLogger(__name__)


@dataclass
class TradeOffPoint:
    """
    Point on the trade-off curve.

    Attributes:
        scenario_name: Scenario identifier
        evaluation: Full ScenarioEvaluation
        objective_1_value: Value for first objective
        objective_2_value: Value for second objective
        is_pareto_optimal: Whether on Pareto frontier
        dominated_by: List of scenarios that dominate this one
    """
    scenario_name: str
    evaluation: ScenarioEvaluation
    objective_1_value: Decimal
    objective_2_value: Decimal
    is_pareto_optimal: bool = False
    dominated_by: List[str] = field(default_factory=list)


@dataclass
class ParetoFrontier:
    """
    Pareto frontier for two objectives.

    Attributes:
        objective_1_name: First objective name
        objective_2_name: Second objective name
        frontier_points: List of Pareto-optimal points
        dominated_points: List of dominated points
        trade_off_slope: Average trade-off rate (ΔObj1 / ΔObj2)
        insights: Human-readable insights
    """
    objective_1_name: str
    objective_2_name: str
    frontier_points: List[TradeOffPoint]
    dominated_points: List[TradeOffPoint]
    trade_off_slope: Optional[Decimal] = None
    insights: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Sort frontier points by objective 1."""
        self.frontier_points.sort(key=lambda p: p.objective_1_value, reverse=True)


@dataclass
class TradeOffAnalysis:
    """
    Complete trade-off analysis.

    Attributes:
        pareto_frontiers: List of Pareto frontiers for different objective pairs
        recommended_scenarios: Recommended scenarios based on preferences
        trade_off_summary: Human-readable summary
    """
    pareto_frontiers: List[ParetoFrontier]
    recommended_scenarios: Dict[str, str]  # preference → scenario_name
    trade_off_summary: str = ""


class TradeOffAnalyzer:
    """
    Analyze trade-offs between competing objectives.

    Identifies Pareto-optimal scenarios and explains trade-offs between
    objectives like equity ownership, risk, cost, and tax incentives.
    """

    # Common trade-off pairs
    COMMON_TRADE_OFFS = [
        ("equity_irr", "probability_of_recoupment"),  # Returns vs. Risk
        ("equity_irr", "cost_of_capital"),  # Returns vs. Cost
        ("tax_incentive_effective_rate", "equity_irr"),  # Incentives vs. Returns
        ("tax_incentive_effective_rate", "weighted_cost_of_capital"),  # Incentives vs. Cost
        ("senior_debt_recovery_rate", "equity_irr")  # Debt safety vs. Equity returns
    ]

    def __init__(self):
        """Initialize analyzer."""
        logger.info("TradeOffAnalyzer initialized")

    def analyze(
        self,
        evaluations: List[ScenarioEvaluation],
        objective_pairs: Optional[List[Tuple[str, str]]] = None
    ) -> TradeOffAnalysis:
        """
        Perform comprehensive trade-off analysis.

        Args:
            evaluations: List of ScenarioEvaluation objects
            objective_pairs: List of (obj1, obj2) tuples to analyze (uses common pairs if None)

        Returns:
            TradeOffAnalysis with Pareto frontiers
        """
        if not evaluations:
            logger.warning("No scenarios to analyze")
            return TradeOffAnalysis(pareto_frontiers=[], recommended_scenarios={})

        logger.info(f"Analyzing trade-offs for {len(evaluations)} scenarios")

        objective_pairs = objective_pairs or self.COMMON_TRADE_OFFS

        pareto_frontiers = []

        for obj1_name, obj2_name in objective_pairs:
            frontier = self.identify_pareto_frontier(
                evaluations,
                obj1_name,
                obj2_name
            )
            pareto_frontiers.append(frontier)

        # Generate recommendations
        recommended_scenarios = self._generate_recommendations(pareto_frontiers, evaluations)

        # Generate summary
        trade_off_summary = self._generate_summary(pareto_frontiers)

        analysis = TradeOffAnalysis(
            pareto_frontiers=pareto_frontiers,
            recommended_scenarios=recommended_scenarios,
            trade_off_summary=trade_off_summary
        )

        logger.info("Trade-off analysis complete")

        return analysis

    def identify_pareto_frontier(
        self,
        evaluations: List[ScenarioEvaluation],
        objective_1_name: str,
        objective_2_name: str,
        maximize_both: bool = True
    ) -> ParetoFrontier:
        """
        Identify Pareto frontier for two objectives.

        Args:
            evaluations: List of evaluations
            objective_1_name: First objective (attribute of ScenarioEvaluation)
            objective_2_name: Second objective
            maximize_both: Whether both objectives are maximized (vs. one minimized)

        Returns:
            ParetoFrontier with optimal and dominated points
        """
        logger.info(f"Identifying Pareto frontier: {objective_1_name} vs {objective_2_name}")

        # Extract objective values
        points = []
        for evaluation in evaluations:
            obj1_value = self._get_objective_value(evaluation, objective_1_name)
            obj2_value = self._get_objective_value(evaluation, objective_2_name)

            point = TradeOffPoint(
                scenario_name=evaluation.scenario_name,
                evaluation=evaluation,
                objective_1_value=obj1_value,
                objective_2_value=obj2_value
            )
            points.append(point)

        # Identify Pareto-optimal points
        frontier_points = []
        dominated_points = []

        for point in points:
            is_dominated = False
            dominated_by = []

            for other_point in points:
                if other_point.scenario_name == point.scenario_name:
                    continue

                # Check if other_point dominates point
                if maximize_both:
                    # Other dominates if it's >= on both objectives and > on at least one
                    if (other_point.objective_1_value >= point.objective_1_value and
                        other_point.objective_2_value >= point.objective_2_value and
                        (other_point.objective_1_value > point.objective_1_value or
                         other_point.objective_2_value > point.objective_2_value)):
                        is_dominated = True
                        dominated_by.append(other_point.scenario_name)

            if is_dominated:
                point.dominated_by = dominated_by
                dominated_points.append(point)
            else:
                point.is_pareto_optimal = True
                frontier_points.append(point)

        # Calculate trade-off slope
        trade_off_slope = self._calculate_trade_off_slope(frontier_points)

        # Generate insights
        insights = self._generate_frontier_insights(
            frontier_points,
            dominated_points,
            objective_1_name,
            objective_2_name,
            trade_off_slope
        )

        frontier = ParetoFrontier(
            objective_1_name=objective_1_name,
            objective_2_name=objective_2_name,
            frontier_points=frontier_points,
            dominated_points=dominated_points,
            trade_off_slope=trade_off_slope,
            insights=insights
        )

        logger.info(f"Pareto frontier identified: {len(frontier_points)} optimal, {len(dominated_points)} dominated")

        return frontier

    def get_pareto_optimal_scenarios(
        self,
        evaluations: List[ScenarioEvaluation],
        objectives: List[str]
    ) -> List[ScenarioEvaluation]:
        """
        Get Pareto-optimal scenarios for multiple objectives.

        Args:
            evaluations: List of evaluations
            objectives: List of objective names

        Returns:
            List of Pareto-optimal evaluations
        """
        if len(objectives) < 2:
            raise ValueError("Need at least 2 objectives for Pareto analysis")

        # For multi-objective, check if any scenario dominates another on ALL objectives
        pareto_optimal = []

        for evaluation in evaluations:
            is_dominated = False

            for other_eval in evaluations:
                if other_eval.scenario_name == evaluation.scenario_name:
                    continue

                # Check if other dominates on all objectives
                dominates_on_all = True
                strictly_better_on_one = False

                for objective in objectives:
                    eval_value = self._get_objective_value(evaluation, objective)
                    other_value = self._get_objective_value(other_eval, objective)

                    if other_value < eval_value:
                        dominates_on_all = False
                        break
                    if other_value > eval_value:
                        strictly_better_on_one = True

                if dominates_on_all and strictly_better_on_one:
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_optimal.append(evaluation)

        logger.info(f"Multi-objective Pareto analysis: {len(pareto_optimal)}/{len(evaluations)} optimal")

        return pareto_optimal

    def explain_trade_off(
        self,
        scenario_a: ScenarioEvaluation,
        scenario_b: ScenarioEvaluation,
        objective_1_name: str,
        objective_2_name: str
    ) -> str:
        """
        Explain trade-off between two scenarios.

        Args:
            scenario_a: First scenario
            scenario_b: Second scenario
            objective_1_name: First objective
            objective_2_name: Second objective

        Returns:
            Human-readable explanation
        """
        obj1_a = self._get_objective_value(scenario_a, objective_1_name)
        obj1_b = self._get_objective_value(scenario_b, objective_1_name)

        obj2_a = self._get_objective_value(scenario_a, objective_2_name)
        obj2_b = self._get_objective_value(scenario_b, objective_2_name)

        delta_obj1 = obj1_b - obj1_a
        delta_obj2 = obj2_b - obj2_a

        explanation = (
            f"Moving from '{scenario_a.scenario_name}' to '{scenario_b.scenario_name}':\n"
            f"  {objective_1_name}: {obj1_a:.2f} → {obj1_b:.2f} "
            f"({'+' if delta_obj1 >= 0 else ''}{delta_obj1:.2f}, "
            f"{'+' if delta_obj1 >= 0 else ''}{(delta_obj1 / obj1_a * Decimal('100')):.1f}%)\n"
            f"  {objective_2_name}: {obj2_a:.2f} → {obj2_b:.2f} "
            f"({'+' if delta_obj2 >= 0 else ''}{delta_obj2:.2f}, "
            f"{'+' if delta_obj2 >= 0 else ''}{(delta_obj2 / obj2_a * Decimal('100')):.1f}%)\n"
        )

        if delta_obj1 > 0 and delta_obj2 > 0:
            explanation += "  → Scenario B dominates A on both objectives."
        elif delta_obj1 < 0 and delta_obj2 < 0:
            explanation += "  → Scenario A dominates B on both objectives."
        else:
            explanation += f"  → Trade-off: Gain in one objective, loss in the other."

        return explanation

    def _get_objective_value(
        self,
        evaluation: ScenarioEvaluation,
        objective_name: str
    ) -> Decimal:
        """Extract objective value from evaluation."""
        if hasattr(evaluation, objective_name):
            value = getattr(evaluation, objective_name)
            if value is None:
                return Decimal("0")
            return Decimal(str(value)) if not isinstance(value, Decimal) else value
        else:
            logger.warning(f"Unknown objective: {objective_name}")
            return Decimal("0")

    def _calculate_trade_off_slope(
        self,
        frontier_points: List[TradeOffPoint]
    ) -> Optional[Decimal]:
        """
        Calculate average trade-off slope along Pareto frontier.

        Returns:
            Average Δobj1 / Δobj2
        """
        if len(frontier_points) < 2:
            return None

        # Sort by objective 1
        sorted_points = sorted(frontier_points, key=lambda p: p.objective_1_value)

        slopes = []
        for i in range(len(sorted_points) - 1):
            p1 = sorted_points[i]
            p2 = sorted_points[i + 1]

            delta_obj1 = p2.objective_1_value - p1.objective_1_value
            delta_obj2 = p2.objective_2_value - p1.objective_2_value

            if delta_obj2 != 0:
                slope = delta_obj1 / delta_obj2
                slopes.append(slope)

        if slopes:
            return sum(slopes) / Decimal(str(len(slopes)))
        return None

    def _generate_frontier_insights(
        self,
        frontier_points: List[TradeOffPoint],
        dominated_points: List[TradeOffPoint],
        obj1_name: str,
        obj2_name: str,
        slope: Optional[Decimal]
    ) -> List[str]:
        """Generate human-readable insights about the frontier."""
        insights = []

        # Insight 1: Number of Pareto-optimal scenarios
        insights.append(f"{len(frontier_points)} scenarios are Pareto-optimal for {obj1_name} vs {obj2_name}")

        # Insight 2: Range of values
        if frontier_points:
            obj1_min = min(p.objective_1_value for p in frontier_points)
            obj1_max = max(p.objective_1_value for p in frontier_points)
            obj2_min = min(p.objective_2_value for p in frontier_points)
            obj2_max = max(p.objective_2_value for p in frontier_points)

            insights.append(
                f"{obj1_name} range: {obj1_min:.2f} to {obj1_max:.2f} "
                f"({((obj1_max - obj1_min) / obj1_max * Decimal('100')):.1f}% spread)"
            )
            insights.append(
                f"{obj2_name} range: {obj2_min:.2f} to {obj2_max:.2f} "
                f"({((obj2_max - obj2_min) / obj2_max * Decimal('100')):.1f}% spread)"
            )

        # Insight 3: Trade-off slope
        if slope:
            insights.append(
                f"Average trade-off: {abs(slope):.2f} units of {obj1_name} per unit of {obj2_name}"
            )

        # Insight 4: Dominated scenarios
        if dominated_points:
            insights.append(f"{len(dominated_points)} scenarios are dominated and can be eliminated")

        return insights

    def _generate_recommendations(
        self,
        frontiers: List[ParetoFrontier],
        evaluations: List[ScenarioEvaluation]
    ) -> Dict[str, str]:
        """Generate scenario recommendations for different preferences."""
        recommendations = {}

        # Recommendation 1: Highest equity IRR (risk-taking investor)
        highest_irr_eval = max(evaluations, key=lambda e: e.equity_irr or Decimal("0"))
        recommendations["high_return_seeking"] = highest_irr_eval.scenario_name

        # Recommendation 2: Highest recoupment probability (risk-averse investor)
        safest_eval = max(evaluations, key=lambda e: e.probability_of_equity_recoupment)
        recommendations["risk_averse"] = safest_eval.scenario_name

        # Recommendation 3: Highest tax incentives (producer)
        highest_incentive_eval = max(evaluations, key=lambda e: e.tax_incentive_effective_rate)
        recommendations["producer_focused"] = highest_incentive_eval.scenario_name

        # Recommendation 4: Lowest cost of capital (efficient financing)
        lowest_cost_eval = min(evaluations, key=lambda e: e.weighted_cost_of_capital)
        recommendations["cost_efficient"] = lowest_cost_eval.scenario_name

        # Recommendation 5: Highest overall score (balanced)
        highest_score_eval = max(evaluations, key=lambda e: e.overall_score)
        recommendations["balanced"] = highest_score_eval.scenario_name

        return recommendations

    def _generate_summary(self, frontiers: List[ParetoFrontier]) -> str:
        """Generate trade-off analysis summary."""
        summary_lines = ["TRADE-OFF ANALYSIS SUMMARY", "=" * 50, ""]

        for frontier in frontiers:
            summary_lines.append(f"{frontier.objective_1_name} vs {frontier.objective_2_name}:")
            summary_lines.append(f"  - {len(frontier.frontier_points)} Pareto-optimal scenarios")

            if frontier.trade_off_slope:
                summary_lines.append(f"  - Trade-off rate: {abs(frontier.trade_off_slope):.2f}")

            for insight in frontier.insights:
                summary_lines.append(f"  - {insight}")

            summary_lines.append("")

        return "\n".join(summary_lines)

    def print_frontier_report(self, frontier: ParetoFrontier):
        """Print formatted Pareto frontier report."""
        print("\n" + "=" * 80)
        print(f"PARETO FRONTIER: {frontier.objective_1_name} vs {frontier.objective_2_name}")
        print("=" * 80)

        print(f"\nPareto-Optimal Scenarios ({len(frontier.frontier_points)}):")
        for point in frontier.frontier_points:
            print(f"  • {point.scenario_name}")
            print(f"      {frontier.objective_1_name}: {point.objective_1_value:.2f}")
            print(f"      {frontier.objective_2_name}: {point.objective_2_value:.2f}")

        if frontier.dominated_points:
            print(f"\nDominated Scenarios ({len(frontier.dominated_points)}):")
            for point in frontier.dominated_points:
                print(f"  • {point.scenario_name} (dominated by: {', '.join(point.dominated_by)})")

        print("\nInsights:")
        for insight in frontier.insights:
            print(f"  - {insight}")

        print("\n" + "=" * 80)
