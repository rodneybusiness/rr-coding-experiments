"""
Integration Tests for Engine 2

End-to-end tests covering complete workflows from revenue projection through
stakeholder analysis, Monte Carlo simulation, and sensitivity analysis.
"""

import pytest
from pathlib import Path
from decimal import Decimal

from backend.models.waterfall import WaterfallStructure, WaterfallNode, RecoupmentPriority
from backend.models.capital_stack import CapitalStack, CapitalComponent
from backend.models.financial_instruments import Equity, SeniorDebt

from backend.engines.waterfall_executor import (
    RevenueProjector,
    WaterfallExecutor,
    StakeholderAnalyzer,
    MonteCarloSimulator,
    SensitivityAnalyzer,
    RevenueDistribution,
    SensitivityVariable,
)


@pytest.fixture
def sample_waterfall():
    """Create sample waterfall structure"""
    waterfall = WaterfallStructure(
        waterfall_name="Test Waterfall",
        default_distribution_fee_rate=Decimal("30.0"),
        nodes=[
            WaterfallNode(
                priority=RecoupmentPriority.SENIOR_DEBT,
                payee="Senior Lender",
                amount=Decimal("10000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                payee="Equity Investors",
                amount=Decimal("15000000"),
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
    return waterfall


@pytest.fixture
def sample_capital_stack():
    """Create sample capital stack"""
    equity = Equity(
        amount=Decimal("15000000"),
        ownership_percentage=Decimal("100.0"),
        premium_percentage=Decimal("20.0")
    )

    senior_debt = SeniorDebt(
        amount=Decimal("10000000"),
        interest_rate=Decimal("8.0"),
        term_months=24,
        origination_fee_percentage=Decimal("2.0")
    )

    stack = CapitalStack(
        stack_name="Test Stack",
        project_budget=Decimal("30000000"),
        components=[
            CapitalComponent(instrument=equity, position=2),
            CapitalComponent(instrument=senior_debt, position=1)
        ]
    )

    return stack


class TestCompleteWorkflow:
    """Test complete end-to-end workflows"""

    def test_revenue_projection_basic(self):
        """Test basic revenue projection"""
        projector = RevenueProjector()

        projection = projector.project(
            total_ultimate_revenue=Decimal("100000000"),
            theatrical_box_office=Decimal("40000000"),
            release_strategy="wide_theatrical",
            project_name="Test Film"
        )

        # Should have revenue in multiple quarters
        assert len(projection.quarterly_revenue) > 0

        # Total should match
        total_revenue = sum(projection.quarterly_revenue.values())
        assert total_revenue == Decimal("100000000")

        # Should have window breakdown
        assert len(projection.by_window) > 0
        assert "theatrical" in projection.by_window

    def test_waterfall_execution(self, sample_waterfall):
        """Test waterfall execution over time"""
        # Create simple revenue projection
        projector = RevenueProjector()
        projection = projector.project(
            total_ultimate_revenue=Decimal("50000000"),
            release_strategy="wide_theatrical",
            project_name="Test Film"
        )

        # Execute waterfall
        executor = WaterfallExecutor(sample_waterfall)
        result = executor.execute_over_time(projection)

        # Should have executed multiple quarters
        assert len(result.quarterly_executions) > 0

        # Total receipts should match projection (minus fees)
        assert result.total_receipts == Decimal("50000000")

        # Should have paid out stakeholders
        assert len(result.total_paid_by_payee) > 0

    def test_stakeholder_analysis(self, sample_waterfall, sample_capital_stack):
        """Test stakeholder return analysis"""
        # Create revenue projection
        projector = RevenueProjector()
        projection = projector.project(
            total_ultimate_revenue=Decimal("60000000"),
            release_strategy="wide_theatrical",
            project_name="Test Film"
        )

        # Execute waterfall
        executor = WaterfallExecutor(sample_waterfall)
        waterfall_result = executor.execute_over_time(projection)

        # Analyze stakeholders
        analyzer = StakeholderAnalyzer(sample_capital_stack, discount_rate=Decimal("0.12"))
        stakeholder_analysis = analyzer.analyze(waterfall_result)

        # Should have stakeholders
        assert len(stakeholder_analysis.stakeholders) > 0

        # Each stakeholder should have metrics
        for stakeholder in stakeholder_analysis.stakeholders:
            assert stakeholder.initial_investment > 0
            assert stakeholder.cash_on_cash >= 0
            # IRR may be None if no positive cash flows

        # Should have summary stats
        assert "total_invested" in stakeholder_analysis.summary_statistics

    def test_monte_carlo_simulation(self, sample_waterfall, sample_capital_stack):
        """Test Monte Carlo simulation"""
        # Create base projection
        projector = RevenueProjector()
        base_projection = projector.project(
            total_ultimate_revenue=Decimal("60000000"),
            release_strategy="wide_theatrical",
            project_name="Test Film"
        )

        # Define revenue distribution
        revenue_dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="triangular",
            parameters={
                "min": Decimal("40000000"),
                "mode": Decimal("60000000"),
                "max": Decimal("100000000")
            }
        )

        # Run simulation (small number for test speed)
        simulator = MonteCarloSimulator(sample_waterfall, sample_capital_stack, base_projection)
        mc_result = simulator.simulate(revenue_dist, num_simulations=100, seed=42)

        # Should have scenarios
        assert len(mc_result.scenarios) == 100

        # Should have percentiles
        assert "p10" in mc_result.revenue_percentiles
        assert "p50" in mc_result.revenue_percentiles
        assert "p90" in mc_result.revenue_percentiles

        # Percentiles should be ordered
        assert mc_result.revenue_percentiles["p10"] <= mc_result.revenue_percentiles["p50"]
        assert mc_result.revenue_percentiles["p50"] <= mc_result.revenue_percentiles["p90"]

        # Should have stakeholder percentiles
        assert len(mc_result.stakeholder_percentiles) > 0

    def test_sensitivity_analysis(self, sample_waterfall, sample_capital_stack):
        """Test sensitivity analysis"""
        # Create base projection
        projector = RevenueProjector()
        base_projection = projector.project(
            total_ultimate_revenue=Decimal("60000000"),
            release_strategy="wide_theatrical",
            project_name="Test Film"
        )

        # Define variables to test
        variables = [
            SensitivityVariable(
                variable_name="total_revenue",
                base_value=Decimal("60000000"),
                low_value=Decimal("45000000"),
                high_value=Decimal("75000000")
            )
        ]

        # Run sensitivity analysis
        analyzer = SensitivityAnalyzer(sample_waterfall, sample_capital_stack, base_projection)
        results = analyzer.analyze(variables, target_metrics=["overall_recovery_rate"])

        # Should have results
        assert "overall_recovery_rate" in results
        assert len(results["overall_recovery_rate"]) > 0

        # Should have impact scores
        for result in results["overall_recovery_rate"]:
            assert result.impact_score >= 0

    def test_end_to_end_complete_workflow(self, sample_waterfall, sample_capital_stack):
        """Test complete workflow from projection to analysis"""
        # 1. Project revenue
        projector = RevenueProjector()
        projection = projector.project(
            total_ultimate_revenue=Decimal("75000000"),
            theatrical_box_office=Decimal("30000000"),
            svod_license_fee=Decimal("25000000"),
            release_strategy="wide_theatrical",
            project_name="Complete Test Film"
        )

        assert projection.total_quarters > 0
        assert sum(projection.quarterly_revenue.values()) == Decimal("75000000")

        # 2. Execute waterfall
        executor = WaterfallExecutor(sample_waterfall)
        waterfall_result = executor.execute_over_time(projection)

        assert len(waterfall_result.quarterly_executions) > 0
        assert waterfall_result.total_receipts > 0

        # 3. Analyze stakeholders
        analyzer = StakeholderAnalyzer(sample_capital_stack, discount_rate=Decimal("0.15"))
        stakeholder_analysis = analyzer.analyze(waterfall_result)

        assert len(stakeholder_analysis.stakeholders) == 2  # Equity + Senior Debt

        # 4. Check senior debt (should recoup fully at $10M investment)
        senior_debt_stakeholder = next(
            s for s in stakeholder_analysis.stakeholders
            if "Senior" in s.stakeholder_name
        )
        assert senior_debt_stakeholder.initial_investment == Decimal("10000000")
        # In this scenario with $75M revenue, debt should fully recoup
        assert senior_debt_stakeholder.total_receipts >= Decimal("10000000")
        assert senior_debt_stakeholder.cash_on_cash >= Decimal("1.0")

        # 5. Check equity (should get remainder after debt)
        equity_stakeholder = next(
            s for s in stakeholder_analysis.stakeholders
            if "Equity" in s.stakeholder_name
        )
        assert equity_stakeholder.initial_investment == Decimal("15000000")
        assert equity_stakeholder.total_receipts > 0

        # 6. Summary stats
        assert "total_invested" in stakeholder_analysis.summary_statistics
        total_invested = Decimal(stakeholder_analysis.summary_statistics["total_invested"])
        assert total_invested == Decimal("25000000")  # $10M debt + $15M equity

        logger.info("Complete end-to-end workflow test passed successfully")


class TestRevenueProjector:
    """Test revenue projector specifically"""

    def test_wide_theatrical_windows(self):
        """Test wide theatrical release window template"""
        projector = RevenueProjector()

        projection = projector.project(
            total_ultimate_revenue=Decimal("100000000"),
            release_strategy="wide_theatrical",
            project_name="Wide Release"
        )

        # Should have theatrical, PVOD, EST, SVOD, etc.
        assert "theatrical" in projection.by_window
        assert "svod" in projection.by_window

        # Theatrical should be significant portion (40-45%)
        theatrical_pct = (projection.by_window["theatrical"] / Decimal("100000000")) * Decimal("100")
        assert theatrical_pct >= Decimal("35.0")
        assert theatrical_pct <= Decimal("50.0")

    def test_streaming_first_windows(self):
        """Test streaming-first release window template"""
        projector = RevenueProjector()

        projection = projector.project(
            total_ultimate_revenue=Decimal("80000000"),
            release_strategy="streaming_first",
            project_name="Streaming First"
        )

        # SVOD should be dominant (70-80%)
        assert "svod" in projection.by_window
        svod_pct = (projection.by_window["svod"] / Decimal("80000000")) * Decimal("100")
        assert svod_pct >= Decimal("70.0")


class TestWaterfallExecutor:
    """Test waterfall executor specifically"""

    def test_cumulative_recoupment_tracking(self, sample_waterfall):
        """Test that cumulative recoupment is tracked correctly"""
        # Create projection
        projector = RevenueProjector()
        projection = projector.project(
            total_ultimate_revenue=Decimal("30000000"),
            release_strategy="wide_theatrical",
            project_name="Cumulative Test"
        )

        # Execute
        executor = WaterfallExecutor(sample_waterfall)
        result = executor.execute_over_time(projection)

        # Check that cumulative increases over time
        prev_cumulative = {}
        for execution in result.quarterly_executions:
            for node_id, cumulative in execution.cumulative_recouped.items():
                if node_id in prev_cumulative:
                    # Cumulative should only increase
                    assert cumulative >= prev_cumulative[node_id]
                prev_cumulative[node_id] = cumulative

    def test_node_stops_when_fully_recouped(self, sample_waterfall):
        """Test that nodes stop receiving payments when fully recouped"""
        # Create large revenue to fully recoup
        projector = RevenueProjector()
        projection = projector.project(
            total_ultimate_revenue=Decimal("100000000"),
            release_strategy="wide_theatrical",
            project_name="Full Recoup Test"
        )

        # Execute
        executor = WaterfallExecutor(sample_waterfall)
        result = executor.execute_over_time(projection)

        # Senior debt should be fully recouped ($10M)
        senior_node_id = f"{RecoupmentPriority.SENIOR_DEBT.value}_Senior Lender"
        final_cumulative = result.total_recouped_by_node.get(senior_node_id, Decimal("0"))

        # Should not exceed target amount
        assert final_cumulative <= Decimal("10000000")


import logging
logger = logging.getLogger(__name__)
