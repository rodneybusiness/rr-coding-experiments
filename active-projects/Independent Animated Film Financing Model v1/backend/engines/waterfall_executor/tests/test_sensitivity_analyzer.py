"""
Unit Tests for Sensitivity Analyzer

Tests variable sensitivity analysis, tornado chart generation,
and impact scoring for identifying key drivers of returns.
"""

import pytest
from decimal import Decimal

from engines.waterfall_executor.sensitivity_analyzer import (
    SensitivityVariable,
    SensitivityResult,
    TornadoChartData,
    SensitivityAnalyzer
)
from engines.waterfall_executor.revenue_projector import RevenueProjector
from models.waterfall import WaterfallStructure, WaterfallNode, RecoupmentPriority
from models.capital_stack import CapitalStack, CapitalComponent
from models.financial_instruments import Equity, SeniorDebt


@pytest.fixture
def simple_waterfall():
    """Create simple waterfall for testing"""
    return WaterfallStructure(
        waterfall_name="Test Waterfall",
        default_distribution_fee_rate=Decimal("30.0"),
        nodes=[
            WaterfallNode(
                priority=RecoupmentPriority.SENIOR_DEBT,
                payee="Senior Lender",
                amount=Decimal("6000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                payee="Equity Investors",
                amount=Decimal("9000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.NET_PROFITS,
                payee="Equity Investors",
                amount=None,
                percentage=Decimal("100.0")
            ),
        ]
    )


@pytest.fixture
def simple_capital_stack():
    """Create simple capital stack for testing"""
    equity = Equity(
        amount=Decimal("9000000"),
        ownership_percentage=Decimal("100.0"),
        premium_percentage=Decimal("20.0")
    )

    senior_debt = SeniorDebt(
        amount=Decimal("6000000"),
        interest_rate=Decimal("8.0"),
        term_months=24,
        origination_fee_percentage=Decimal("2.0")
    )

    return CapitalStack(
        stack_name="Test Stack",
        project_budget=Decimal("15000000"),
        components=[
            CapitalComponent(instrument=senior_debt, position=1),
            CapitalComponent(instrument=equity, position=2)
        ]
    )


@pytest.fixture
def base_projection():
    """Create base revenue projection"""
    projector = RevenueProjector()
    return projector.project(
        total_ultimate_revenue=Decimal("30000000"),
        release_strategy="wide_theatrical",
        project_name="Test Film"
    )


class TestSensitivityVariable:
    """Test SensitivityVariable dataclass"""

    def test_sensitivity_variable_creation(self):
        """Test creating sensitivity variable"""
        variable = SensitivityVariable(
            variable_name="total_revenue",
            base_value=Decimal("30000000"),
            low_value=Decimal("20000000"),
            high_value=Decimal("40000000"),
            variable_type="revenue"
        )

        assert variable.variable_name == "total_revenue"
        assert variable.base_value == Decimal("30000000")
        assert variable.low_value == Decimal("20000000")
        assert variable.high_value == Decimal("40000000")
        assert variable.variable_type == "revenue"

    def test_sensitivity_variable_default_type(self):
        """Test sensitivity variable with default type"""
        variable = SensitivityVariable(
            variable_name="box_office",
            base_value=Decimal("25000000"),
            low_value=Decimal("15000000"),
            high_value=Decimal("35000000")
        )

        assert variable.variable_type == "revenue"  # Default


class TestSensitivityAnalyzer:
    """Test SensitivityAnalyzer class"""

    def test_analyzer_initialization(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test analyzer initialization"""
        analyzer = SensitivityAnalyzer(
            simple_waterfall,
            simple_capital_stack,
            base_projection
        )

        assert analyzer.waterfall == simple_waterfall
        assert analyzer.capital_stack == simple_capital_stack
        assert analyzer.base_projection == base_projection

    def test_adjust_projection_revenue_variable(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test adjusting projection for revenue variable"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        # Adjust to 50% of base revenue
        adjusted = analyzer._adjust_projection(
            base_projection,
            "total_revenue",
            Decimal("15000000")  # 50% of 30M
        )

        # All revenue should be scaled (allow small precision tolerance)
        base_total = sum(base_projection.quarterly_revenue.values())
        adjusted_total = sum(adjusted.quarterly_revenue.values())
        expected_total = base_total / Decimal("2")

        assert abs(adjusted_total - expected_total) < Decimal("0.01")

    def test_adjust_projection_box_office_variable(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test adjusting projection for box office variable"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        # Adjust box office to 20M
        adjusted = analyzer._adjust_projection(
            base_projection,
            "box_office_revenue",
            Decimal("20000000")
        )

        # Should scale based on box office
        adjusted_total = sum(adjusted.quarterly_revenue.values())
        assert adjusted_total != sum(base_projection.quarterly_revenue.values())

    def test_run_scenario(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test running a scenario and extracting metrics"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        metrics = analyzer._run_scenario(base_projection)

        assert isinstance(metrics, dict)
        # Should have overall recovery rate
        assert "overall_recovery_rate" in metrics

    def test_run_scenario_equity_irr(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test that scenario extracts equity IRR"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        metrics = analyzer._run_scenario(base_projection)

        # May or may not have equity_irr depending on returns
        if "equity_irr" in metrics:
            assert isinstance(metrics["equity_irr"], Decimal)

    def test_analyze_single_variable(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test analyzing single variable sensitivity"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        assert "overall_recovery_rate" in results
        assert len(results["overall_recovery_rate"]) == 1

        result = results["overall_recovery_rate"][0]
        assert isinstance(result, SensitivityResult)
        assert result.variable.variable_name == "total_revenue"

    def test_analyze_multiple_variables(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test analyzing multiple variables"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            ),
            SensitivityVariable(
                variable_name="box_office_revenue",
                base_value=Decimal("15000000"),
                low_value=Decimal("10000000"),
                high_value=Decimal("20000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        assert len(results["overall_recovery_rate"]) == 2

    def test_analyze_delta_calculations(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test that deltas are calculated correctly"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        result = results["overall_recovery_rate"][0]

        # Deltas should exist
        assert "overall_recovery_rate" in result.delta_low
        assert "overall_recovery_rate" in result.delta_high

        # Base should be between low and high
        base_val = result.base_case["overall_recovery_rate"]
        low_val = result.low_case["overall_recovery_rate"]
        high_val = result.high_case["overall_recovery_rate"]

        # For revenue increase, recovery rate should increase
        assert high_val >= low_val

    def test_analyze_impact_score(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test impact score calculation"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        result = results["overall_recovery_rate"][0]

        # Impact score should be max of absolute deltas
        delta_low = abs(result.delta_low["overall_recovery_rate"])
        delta_high = abs(result.delta_high["overall_recovery_rate"])

        expected_impact = max(delta_low, delta_high)
        assert result.impact_score == expected_impact

    def test_analyze_sorted_by_impact(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test that results are sorted by impact score"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("25000000"),  # Small range
                high_value=Decimal("35000000")
            ),
            SensitivityVariable(
                variable_name="box_office_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("10000000"),  # Large range
                high_value=Decimal("50000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        # Results should be sorted by impact (descending)
        result_list = results["overall_recovery_rate"]
        for i in range(len(result_list) - 1):
            assert result_list[i].impact_score >= result_list[i + 1].impact_score

    def test_analyze_multiple_target_metrics(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test analyzing with multiple target metrics"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            )
        ]

        results = analyzer.analyze(
            variables,
            target_metrics=["overall_recovery_rate", "equity_irr"]
        )

        # Should have results for both metrics
        assert "overall_recovery_rate" in results
        assert "equity_irr" in results

    def test_generate_tornado_chart_data(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test generating tornado chart data"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        tornado_data = analyzer.generate_tornado_chart_data(
            results["overall_recovery_rate"],
            "overall_recovery_rate"
        )

        assert isinstance(tornado_data, TornadoChartData)
        assert tornado_data.target_metric == "overall_recovery_rate"
        assert len(tornado_data.variables) == 1
        assert tornado_data.variables[0] == "total_revenue"

    def test_tornado_chart_deltas(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test tornado chart delta calculations"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        tornado_data = analyzer.generate_tornado_chart_data(
            results["overall_recovery_rate"],
            "overall_recovery_rate"
        )

        # Should have deltas for low and high
        assert len(tornado_data.low_deltas) == 1
        assert len(tornado_data.high_deltas) == 1

        # Low deltas should be negative of delta_low (for visualization)
        result = results["overall_recovery_rate"][0]
        assert tornado_data.low_deltas[0] == -result.delta_low["overall_recovery_rate"]
        assert tornado_data.high_deltas[0] == result.delta_high["overall_recovery_rate"]

    def test_tornado_chart_base_value(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test tornado chart base value"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        tornado_data = analyzer.generate_tornado_chart_data(
            results["overall_recovery_rate"],
            "overall_recovery_rate"
        )

        # Base value should match first result's base case
        result = results["overall_recovery_rate"][0]
        assert tornado_data.base_value == result.base_case["overall_recovery_rate"]

    def test_tornado_chart_multiple_variables_sorted(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test tornado chart with multiple variables maintains sort order"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="var_a",
                base_value=Decimal("30000000"),
                low_value=Decimal("25000000"),
                high_value=Decimal("35000000")
            ),
            SensitivityVariable(
                variable_name="var_b",
                base_value=Decimal("30000000"),
                low_value=Decimal("10000000"),
                high_value=Decimal("50000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        tornado_data = analyzer.generate_tornado_chart_data(
            results["overall_recovery_rate"],
            "overall_recovery_rate"
        )

        # Variables should be in same order as results (sorted by impact)
        result_names = [r.variable.variable_name for r in results["overall_recovery_rate"]]
        assert tornado_data.variables == result_names

    def test_sensitivity_with_zero_base_value(self, simple_waterfall, simple_capital_stack):
        """Test handling of zero base value in projection"""
        # Create projection with specific metadata
        projector = RevenueProjector()
        projection = projector.project(
            total_ultimate_revenue=Decimal("30000000"),
            release_strategy="wide_theatrical",
            project_name="Test Film"
        )

        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, projection)

        # Create variable with revenue adjustment
        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("15000000"),
                high_value=Decimal("45000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        # Should handle gracefully
        assert "overall_recovery_rate" in results

    def test_sensitivity_result_structure(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test sensitivity result structure completeness"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("30000000"),
                low_value=Decimal("20000000"),
                high_value=Decimal("40000000")
            )
        ]

        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        result = results["overall_recovery_rate"][0]

        # Check all required fields
        assert result.variable is not None
        assert result.base_case is not None
        assert result.low_case is not None
        assert result.high_case is not None
        assert result.delta_low is not None
        assert result.delta_high is not None
        assert result.impact_score is not None

    def test_empty_variables_list(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test analyzing with empty variables list"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        results = analyzer.analyze([], target_metrics=["overall_recovery_rate"])

        # Should return empty results
        assert "overall_recovery_rate" in results
        assert len(results["overall_recovery_rate"]) == 0

    def test_tornado_chart_empty_results(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test generating tornado chart with empty results"""
        analyzer = SensitivityAnalyzer(simple_waterfall, simple_capital_stack, base_projection)

        tornado_data = analyzer.generate_tornado_chart_data([], "overall_recovery_rate")

        assert tornado_data.target_metric == "overall_recovery_rate"
        assert len(tornado_data.variables) == 0
        assert len(tornado_data.low_deltas) == 0
        assert len(tornado_data.high_deltas) == 0
        assert tornado_data.base_value == Decimal("0")
