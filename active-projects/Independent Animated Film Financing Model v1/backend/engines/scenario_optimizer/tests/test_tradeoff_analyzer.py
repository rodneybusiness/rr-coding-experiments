"""
Unit Tests for TradeOffAnalyzer

Tests Pareto frontier identification, dominated scenario detection, and trade-off metrics.
"""

import pytest
from decimal import Decimal

from engines.scenario_optimizer import (
    TradeOffAnalyzer,
    TradeOffPoint,
    ParetoFrontier
)
from engines.scenario_optimizer.tradeoff_analyzer import TradeOffAnalysis
from engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluation
from models.capital_stack import CapitalStack, CapitalComponent
from models.financial_instruments import Equity


def create_minimal_capital_stack(name: str = "test", budget: Decimal = Decimal("30000000")) -> CapitalStack:
    """Create a minimal valid capital stack with one equity component for testing."""
    equity = Equity(amount=budget, ownership_percentage=Decimal("100.0"))
    component = CapitalComponent(instrument=equity, position=1)
    return CapitalStack(stack_name=name, project_budget=budget, components=[component])


class TestTradeOffAnalyzer:
    """Test TradeOffAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return TradeOffAnalyzer()

    @pytest.fixture
    def sample_evaluations(self):
        """Create sample scenario evaluations for testing."""
        # Scenario 1: High returns, low safety
        eval1 = ScenarioEvaluation(
            scenario_name="high_risk_high_return",
            capital_stack=create_minimal_capital_stack("test1"),
            equity_irr=Decimal("25.0"),
            probability_of_equity_recoupment=Decimal("0.50"),
            tax_incentive_effective_rate=Decimal("15.0"),
            weighted_cost_of_capital=Decimal("15.0"),
            senior_debt_recovery_rate=Decimal("85.0"),
            overall_score=Decimal("65.0")
        )

        # Scenario 2: Medium returns, high safety
        eval2 = ScenarioEvaluation(
            scenario_name="balanced",
            capital_stack=create_minimal_capital_stack("test2"),
            equity_irr=Decimal("18.0"),
            probability_of_equity_recoupment=Decimal("0.80"),
            tax_incentive_effective_rate=Decimal("20.0"),
            weighted_cost_of_capital=Decimal("12.0"),
            senior_debt_recovery_rate=Decimal("95.0"),
            overall_score=Decimal("75.0")
        )

        # Scenario 3: Low returns, very high safety
        eval3 = ScenarioEvaluation(
            scenario_name="low_risk_low_return",
            capital_stack=create_minimal_capital_stack("test3"),
            equity_irr=Decimal("12.0"),
            probability_of_equity_recoupment=Decimal("0.90"),
            tax_incentive_effective_rate=Decimal("25.0"),
            weighted_cost_of_capital=Decimal("10.0"),
            senior_debt_recovery_rate=Decimal("100.0"),
            overall_score=Decimal("70.0")
        )

        # Scenario 4: Dominated scenario (worse on both dimensions)
        eval4 = ScenarioEvaluation(
            scenario_name="dominated",
            capital_stack=create_minimal_capital_stack("test4"),
            equity_irr=Decimal("10.0"),
            probability_of_equity_recoupment=Decimal("0.40"),
            tax_incentive_effective_rate=Decimal("10.0"),
            weighted_cost_of_capital=Decimal("18.0"),
            senior_debt_recovery_rate=Decimal("75.0"),
            overall_score=Decimal("45.0")
        )

        return [eval1, eval2, eval3, eval4]

    @pytest.fixture
    def two_evaluations(self, sample_evaluations):
        """Just first two evaluations."""
        return sample_evaluations[:2]

    # Initialization Tests

    def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer is not None
        assert hasattr(analyzer, 'COMMON_TRADE_OFFS')
        assert len(analyzer.COMMON_TRADE_OFFS) > 0

    def test_common_trade_offs_defined(self, analyzer):
        """Test that common trade-off pairs are defined."""
        assert ("equity_irr", "probability_of_recoupment") in analyzer.COMMON_TRADE_OFFS
        assert ("tax_incentive_effective_rate", "equity_irr") in analyzer.COMMON_TRADE_OFFS

    # Pareto Frontier Tests

    def test_identify_pareto_frontier_basic(self, analyzer, sample_evaluations):
        """Test identifying Pareto frontier for two objectives."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        assert isinstance(frontier, ParetoFrontier)
        assert frontier.objective_1_name == "equity_irr"
        assert frontier.objective_2_name == "probability_of_equity_recoupment"
        assert len(frontier.frontier_points) > 0
        assert len(frontier.frontier_points) <= len(sample_evaluations)

    def test_pareto_frontier_identifies_dominated_scenarios(self, analyzer, sample_evaluations):
        """Test that dominated scenarios are correctly identified."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        # The "dominated" scenario should be in dominated_points
        dominated_names = [p.scenario_name for p in frontier.dominated_points]
        assert "dominated" in dominated_names

    def test_pareto_frontier_points_are_optimal(self, analyzer, sample_evaluations):
        """Test that frontier points are marked as Pareto-optimal."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        for point in frontier.frontier_points:
            assert point.is_pareto_optimal

    def test_pareto_frontier_sorted_by_objective_1(self, analyzer, sample_evaluations):
        """Test that frontier points are sorted by objective 1."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        if len(frontier.frontier_points) > 1:
            for i in range(len(frontier.frontier_points) - 1):
                assert frontier.frontier_points[i].objective_1_value >= frontier.frontier_points[i + 1].objective_1_value

    def test_pareto_frontier_calculates_trade_off_slope(self, analyzer, sample_evaluations):
        """Test that trade-off slope is calculated."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        if len(frontier.frontier_points) >= 2:
            assert frontier.trade_off_slope is not None
            assert isinstance(frontier.trade_off_slope, Decimal)

    def test_pareto_frontier_has_insights(self, analyzer, sample_evaluations):
        """Test that frontier includes insights."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        assert len(frontier.insights) > 0
        assert isinstance(frontier.insights[0], str)

    # Multi-Objective Pareto Tests

    def test_get_pareto_optimal_scenarios_multi_objective(self, analyzer, sample_evaluations):
        """Test getting Pareto-optimal scenarios for multiple objectives."""
        objectives = ["equity_irr", "probability_of_equity_recoupment", "tax_incentive_effective_rate"]

        pareto_optimal = analyzer.get_pareto_optimal_scenarios(
            sample_evaluations,
            objectives
        )

        assert len(pareto_optimal) > 0
        assert len(pareto_optimal) <= len(sample_evaluations)

        # Dominated scenario should not be in pareto optimal
        pareto_names = [e.scenario_name for e in pareto_optimal]
        assert "dominated" not in pareto_names

    def test_multi_objective_requires_minimum_objectives(self, analyzer, sample_evaluations):
        """Test that multi-objective analysis requires at least 2 objectives."""
        with pytest.raises(ValueError, match="at least 2 objectives"):
            analyzer.get_pareto_optimal_scenarios(sample_evaluations, ["equity_irr"])

    # Trade-Off Explanation Tests

    def test_explain_trade_off(self, analyzer, two_evaluations):
        """Test explaining trade-off between two scenarios."""
        explanation = analyzer.explain_trade_off(
            two_evaluations[0],
            two_evaluations[1],
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        assert isinstance(explanation, str)
        assert two_evaluations[0].scenario_name in explanation
        assert two_evaluations[1].scenario_name in explanation
        assert "equity_irr" in explanation
        assert "probability_of_equity_recoupment" in explanation

    def test_explain_trade_off_shows_changes(self, analyzer, two_evaluations):
        """Test that explanation shows value changes."""
        explanation = analyzer.explain_trade_off(
            two_evaluations[0],
            two_evaluations[1],
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        # Should show directional changes
        assert "→" in explanation or "->" in explanation

    def test_explain_trade_off_identifies_domination(self, analyzer, sample_evaluations):
        """Test that explanation identifies when one scenario dominates."""
        # Compare dominated scenario with balanced
        explanation = analyzer.explain_trade_off(
            sample_evaluations[3],  # dominated
            sample_evaluations[1],  # balanced
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        assert "dominates" in explanation.lower()

    # Complete Analysis Tests

    def test_analyze_complete(self, analyzer, sample_evaluations):
        """Test complete trade-off analysis."""
        analysis = analyzer.analyze(sample_evaluations)

        assert isinstance(analysis, TradeOffAnalysis)
        assert len(analysis.pareto_frontiers) > 0
        assert len(analysis.recommended_scenarios) > 0
        assert analysis.trade_off_summary != ""

    def test_analyze_with_custom_objective_pairs(self, analyzer, sample_evaluations):
        """Test analysis with custom objective pairs."""
        custom_pairs = [
            ("equity_irr", "weighted_cost_of_capital"),
            ("tax_incentive_effective_rate", "senior_debt_recovery_rate")
        ]

        analysis = analyzer.analyze(sample_evaluations, objective_pairs=custom_pairs)

        assert len(analysis.pareto_frontiers) == len(custom_pairs)

    def test_analyze_generates_recommendations(self, analyzer, sample_evaluations):
        """Test that analysis generates scenario recommendations."""
        analysis = analyzer.analyze(sample_evaluations)

        assert "high_return_seeking" in analysis.recommended_scenarios
        assert "risk_averse" in analysis.recommended_scenarios
        assert "producer_focused" in analysis.recommended_scenarios
        assert "balanced" in analysis.recommended_scenarios

    def test_analyze_empty_evaluations(self, analyzer):
        """Test analyzing empty list of evaluations."""
        analysis = analyzer.analyze([])

        assert len(analysis.pareto_frontiers) == 0
        assert len(analysis.recommended_scenarios) == 0

    # Objective Value Extraction Tests

    def test_get_objective_value_equity_irr(self, analyzer, sample_evaluations):
        """Test extracting equity IRR objective value."""
        value = analyzer._get_objective_value(sample_evaluations[0], "equity_irr")

        assert value == Decimal("25.0")

    def test_get_objective_value_probability(self, analyzer, sample_evaluations):
        """Test extracting probability of recoupment."""
        value = analyzer._get_objective_value(sample_evaluations[0], "probability_of_equity_recoupment")

        assert value == Decimal("0.50")

    def test_get_objective_value_unknown_returns_zero(self, analyzer, sample_evaluations):
        """Test that unknown objective returns zero."""
        value = analyzer._get_objective_value(sample_evaluations[0], "nonexistent_objective")

        assert value == Decimal("0")

    # Recommendation Tests

    def test_recommendations_identify_high_return_scenario(self, analyzer, sample_evaluations):
        """Test that high return scenario is recommended correctly."""
        analysis = analyzer.analyze(sample_evaluations)

        high_return_scenario = analysis.recommended_scenarios.get("high_return_seeking")
        assert high_return_scenario == "high_risk_high_return"  # Highest IRR

    def test_recommendations_identify_risk_averse_scenario(self, analyzer, sample_evaluations):
        """Test that risk-averse scenario is recommended correctly."""
        analysis = analyzer.analyze(sample_evaluations)

        risk_averse_scenario = analysis.recommended_scenarios.get("risk_averse")
        assert risk_averse_scenario == "low_risk_low_return"  # Highest recoupment probability

    def test_recommendations_identify_producer_focused(self, analyzer, sample_evaluations):
        """Test that producer-focused scenario is recommended correctly."""
        analysis = analyzer.analyze(sample_evaluations)

        producer_scenario = analysis.recommended_scenarios.get("producer_focused")
        assert producer_scenario == "low_risk_low_return"  # Highest tax incentives

    # Trade-Off Slope Tests

    def test_trade_off_slope_calculation(self, analyzer, sample_evaluations):
        """Test trade-off slope calculation."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations[:3],  # Exclude dominated
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        if len(frontier.frontier_points) >= 2:
            slope = analyzer._calculate_trade_off_slope(frontier.frontier_points)
            assert slope is not None
            assert isinstance(slope, Decimal)

    def test_trade_off_slope_single_point(self, analyzer):
        """Test that single point returns None for slope."""
        point = TradeOffPoint(
            scenario_name="test",
            evaluation=ScenarioEvaluation(
                scenario_name="test",
                capital_stack=create_minimal_capital_stack()
            ),
            objective_1_value=Decimal("20.0"),
            objective_2_value=Decimal("0.75")
        )

        slope = analyzer._calculate_trade_off_slope([point])
        assert slope is None

    # Insight Generation Tests

    def test_frontier_insights_include_count(self, analyzer, sample_evaluations):
        """Test that insights include count of Pareto-optimal scenarios."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        # First insight should mention number of optimal scenarios
        assert any("Pareto-optimal" in insight for insight in frontier.insights)

    def test_frontier_insights_include_ranges(self, analyzer, sample_evaluations):
        """Test that insights include objective value ranges."""
        frontier = analyzer.identify_pareto_frontier(
            sample_evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        # Should have insights about ranges
        range_insights = [i for i in frontier.insights if "range" in i.lower()]
        assert len(range_insights) > 0

    # Summary Generation Tests

    def test_summary_generation(self, analyzer, sample_evaluations):
        """Test trade-off summary generation."""
        analysis = analyzer.analyze(sample_evaluations)

        assert "TRADE-OFF ANALYSIS SUMMARY" in analysis.trade_off_summary
        assert len(analysis.trade_off_summary) > 0

    def test_summary_includes_all_frontiers(self, analyzer, sample_evaluations):
        """Test that summary includes all analyzed frontiers."""
        analysis = analyzer.analyze(sample_evaluations)

        # Should have entries for multiple objective pairs
        assert "equity_irr" in analysis.trade_off_summary
        assert "probability_of_recoupment" in analysis.trade_off_summary


class TestTradeOffDataClasses:
    """Test trade-off data classes."""

    def test_trade_off_point_creation(self):
        """Test creating a trade-off point."""
        evaluation = ScenarioEvaluation(
            scenario_name="test",
            capital_stack=create_minimal_capital_stack()
        )

        point = TradeOffPoint(
            scenario_name="test_scenario",
            evaluation=evaluation,
            objective_1_value=Decimal("20.0"),
            objective_2_value=Decimal("0.75")
        )

        assert point.scenario_name == "test_scenario"
        assert point.evaluation == evaluation
        assert point.objective_1_value == Decimal("20.0")
        assert point.objective_2_value == Decimal("0.75")
        assert not point.is_pareto_optimal
        assert len(point.dominated_by) == 0

    def test_trade_off_point_with_domination(self):
        """Test trade-off point with domination info."""
        evaluation = ScenarioEvaluation(
            scenario_name="test",
            capital_stack=create_minimal_capital_stack()
        )

        point = TradeOffPoint(
            scenario_name="dominated_scenario",
            evaluation=evaluation,
            objective_1_value=Decimal("10.0"),
            objective_2_value=Decimal("0.50"),
            is_pareto_optimal=False,
            dominated_by=["scenario_a", "scenario_b"]
        )

        assert not point.is_pareto_optimal
        assert len(point.dominated_by) == 2
        assert "scenario_a" in point.dominated_by

    def test_pareto_frontier_creation(self):
        """Test creating a Pareto frontier."""
        evaluation = ScenarioEvaluation(
            scenario_name="test",
            capital_stack=create_minimal_capital_stack()
        )

        point1 = TradeOffPoint(
            scenario_name="scenario1",
            evaluation=evaluation,
            objective_1_value=Decimal("25.0"),
            objective_2_value=Decimal("0.60"),
            is_pareto_optimal=True
        )

        point2 = TradeOffPoint(
            scenario_name="scenario2",
            evaluation=evaluation,
            objective_1_value=Decimal("15.0"),
            objective_2_value=Decimal("0.85"),
            is_pareto_optimal=True
        )

        frontier = ParetoFrontier(
            objective_1_name="equity_irr",
            objective_2_name="probability_of_recoupment",
            frontier_points=[point1, point2],
            dominated_points=[]
        )

        assert frontier.objective_1_name == "equity_irr"
        assert frontier.objective_2_name == "probability_of_recoupment"
        assert len(frontier.frontier_points) == 2
        assert len(frontier.dominated_points) == 0

    def test_pareto_frontier_sorts_points(self):
        """Test that Pareto frontier auto-sorts points by objective 1."""
        evaluation = ScenarioEvaluation(
            scenario_name="test",
            capital_stack=create_minimal_capital_stack()
        )

        point1 = TradeOffPoint(
            scenario_name="scenario1",
            evaluation=evaluation,
            objective_1_value=Decimal("15.0"),  # Lower value
            objective_2_value=Decimal("0.85"),
            is_pareto_optimal=True
        )

        point2 = TradeOffPoint(
            scenario_name="scenario2",
            evaluation=evaluation,
            objective_1_value=Decimal("25.0"),  # Higher value
            objective_2_value=Decimal("0.60"),
            is_pareto_optimal=True
        )

        # Create with unsorted points
        frontier = ParetoFrontier(
            objective_1_name="equity_irr",
            objective_2_name="probability_of_recoupment",
            frontier_points=[point1, point2],  # Not sorted
            dominated_points=[]
        )

        # Should be sorted high to low by objective 1
        assert frontier.frontier_points[0].objective_1_value >= frontier.frontier_points[1].objective_1_value

    def test_trade_off_analysis_creation(self):
        """Test creating trade-off analysis."""
        frontier = ParetoFrontier(
            objective_1_name="equity_irr",
            objective_2_name="probability_of_recoupment",
            frontier_points=[],
            dominated_points=[]
        )

        analysis = TradeOffAnalysis(
            pareto_frontiers=[frontier],
            recommended_scenarios={
                "high_return_seeking": "scenario_a",
                "risk_averse": "scenario_b"
            },
            trade_off_summary="Test summary"
        )

        assert len(analysis.pareto_frontiers) == 1
        assert len(analysis.recommended_scenarios) == 2
        assert analysis.trade_off_summary == "Test summary"
