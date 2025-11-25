"""
Unit Tests for Monte Carlo Simulator

Tests distribution creation, percentile calculations, convergence,
and edge cases for Monte Carlo simulations.
"""

import pytest
from decimal import Decimal
import random

from engines.waterfall_executor.monte_carlo_simulator import (
    RevenueDistribution,
    MonteCarloScenario,
    MonteCarloResult,
    MonteCarloSimulator
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
                amount=Decimal("5000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                payee="Equity Investors",
                amount=Decimal("10000000"),
                percentage=None
            ),
        ]
    )


@pytest.fixture
def simple_capital_stack():
    """Create simple capital stack for testing"""
    equity = Equity(
        amount=Decimal("10000000"),
        ownership_percentage=Decimal("100.0"),
        premium_percentage=Decimal("20.0")
    )

    senior_debt = SeniorDebt(
        amount=Decimal("5000000"),
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


class TestRevenueDistribution:
    """Test RevenueDistribution class"""

    def test_triangular_distribution_valid(self):
        """Test valid triangular distribution"""
        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="triangular",
            parameters={
                "min": Decimal("20000000"),
                "mode": Decimal("30000000"),
                "max": Decimal("50000000")
            }
        )

        assert dist.variable_name == "total_revenue"
        assert dist.distribution_type == "triangular"
        assert dist.parameters["min"] == Decimal("20000000")
        assert dist.parameters["mode"] == Decimal("30000000")
        assert dist.parameters["max"] == Decimal("50000000")

    def test_triangular_distribution_missing_param(self):
        """Test triangular distribution with missing parameter"""
        with pytest.raises(ValueError, match="Triangular distribution requires"):
            RevenueDistribution(
                variable_name="total_revenue",
                distribution_type="triangular",
                parameters={
                    "min": Decimal("20000000"),
                    "max": Decimal("50000000")
                    # Missing "mode"
                }
            )

    def test_uniform_distribution_valid(self):
        """Test valid uniform distribution"""
        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="uniform",
            parameters={
                "min": Decimal("20000000"),
                "max": Decimal("50000000")
            }
        )

        assert dist.distribution_type == "uniform"
        assert "min" in dist.parameters
        assert "max" in dist.parameters

    def test_normal_distribution_valid(self):
        """Test valid normal distribution"""
        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="normal",
            parameters={
                "mean": Decimal("30000000"),
                "std": Decimal("5000000")
            }
        )

        assert dist.distribution_type == "normal"
        assert "mean" in dist.parameters
        assert "std" in dist.parameters


class TestMonteCarloScenario:
    """Test MonteCarloScenario dataclass"""

    def test_scenario_creation(self):
        """Test scenario creation"""
        scenario = MonteCarloScenario(
            scenario_id=1,
            total_revenue=Decimal("35000000"),
            stakeholder_results={
                "equity_Equity Investors": {
                    "irr": Decimal("0.15"),
                    "cash_on_cash": Decimal("1.5"),
                    "total_receipts": Decimal("15000000"),
                    "fully_recouped": True
                }
            }
        )

        assert scenario.scenario_id == 1
        assert scenario.total_revenue == Decimal("35000000")
        assert len(scenario.stakeholder_results) == 1
        assert scenario.stakeholder_results["equity_Equity Investors"]["irr"] == Decimal("0.15")


class TestMonteCarloSimulator:
    """Test MonteCarloSimulator class"""

    def test_simulator_initialization(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test simulator initialization"""
        simulator = MonteCarloSimulator(
            simple_waterfall,
            simple_capital_stack,
            base_projection
        )

        assert simulator.waterfall == simple_waterfall
        assert simulator.capital_stack == simple_capital_stack
        assert simulator.base_projection == base_projection

    def test_sample_from_triangular_distribution(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test sampling from triangular distribution"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="test",
            distribution_type="triangular",
            parameters={
                "min": Decimal("20000000"),
                "mode": Decimal("30000000"),
                "max": Decimal("50000000")
            }
        )

        # Set seed for reproducibility
        random.seed(42)

        # Sample multiple times
        samples = [simulator._sample_from_distribution(dist) for _ in range(100)]

        # All samples should be within range
        for sample in samples:
            assert sample >= Decimal("20000000")
            assert sample <= Decimal("50000000")

    def test_sample_from_uniform_distribution(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test sampling from uniform distribution"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="test",
            distribution_type="uniform",
            parameters={
                "min": Decimal("20000000"),
                "max": Decimal("50000000")
            }
        )

        random.seed(42)
        samples = [simulator._sample_from_distribution(dist) for _ in range(100)]

        # All samples should be within range
        for sample in samples:
            assert sample >= Decimal("20000000")
            assert sample <= Decimal("50000000")

    def test_sample_from_normal_distribution(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test sampling from normal distribution"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="test",
            distribution_type="normal",
            parameters={
                "mean": Decimal("30000000"),
                "std": Decimal("5000000")
            }
        )

        random.seed(42)
        samples = [simulator._sample_from_distribution(dist) for _ in range(100)]

        # All samples should be non-negative (normal can be clamped at 0)
        for sample in samples:
            assert sample >= Decimal("0")

    def test_sample_unsupported_distribution(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test sampling from unsupported distribution type"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="test",
            distribution_type="invalid_type",
            parameters={}
        )

        with pytest.raises(ValueError, match="Unsupported distribution type"):
            simulator._sample_from_distribution(dist)

    def test_scale_projection(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test scaling revenue projection"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        # Scale by 0.5 (50%)
        scaled = simulator._scale_projection(base_projection, Decimal("0.5"))

        # Quarterly revenue should be scaled
        for quarter, original_amount in base_projection.quarterly_revenue.items():
            expected = original_amount * Decimal("0.5")
            # Use quantize to avoid precision issues
            assert abs(scaled.quarterly_revenue[quarter] - expected) < Decimal("0.01")

        # Total should be scaled (allow small precision tolerance)
        original_total = sum(base_projection.quarterly_revenue.values())
        scaled_total = sum(scaled.quarterly_revenue.values())
        expected_total = original_total * Decimal("0.5")
        assert abs(scaled_total - expected_total) < Decimal("0.01")

        # Windows should be scaled
        for window, original_amount in base_projection.by_window.items():
            expected = original_amount * Decimal("0.5")
            assert abs(scaled.by_window[window] - expected) < Decimal("0.01")

    def test_scale_projection_double(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test scaling projection by 2x"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        scaled = simulator._scale_projection(base_projection, Decimal("2.0"))

        original_total = sum(base_projection.quarterly_revenue.values())
        scaled_total = sum(scaled.quarterly_revenue.values())
        expected_total = original_total * Decimal("2.0")

        # Allow small precision tolerance
        assert abs(scaled_total - expected_total) < Decimal("0.01")

    def test_calculate_percentile(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test percentile calculation"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        values = [Decimal(str(x)) for x in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]

        # P50 should be around median (implementation uses index-based approach)
        p50 = simulator._calculate_percentile(values, 50)
        # The implementation calculates index as int(len * 50 / 100) = int(10 * 0.5) = 5
        # This gives us values[5] = 60 (0-indexed)
        assert p50 == Decimal("60")

        # P10 calculates as int(10 * 0.1) = 1, giving values[1] = 20
        p10 = simulator._calculate_percentile(values, 10)
        assert p10 == Decimal("20")

        # P90 calculates as int(10 * 0.9) = 9, giving values[9] = 100
        p90 = simulator._calculate_percentile(values, 90)
        assert p90 == Decimal("100")

    def test_calculate_percentile_empty_list(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test percentile calculation with empty list"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        result = simulator._calculate_percentile([], 50)
        assert result == Decimal("0")

    def test_simulate_single_simulation(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test running single Monte Carlo simulation"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="triangular",
            parameters={
                "min": Decimal("25000000"),
                "mode": Decimal("30000000"),
                "max": Decimal("40000000")
            }
        )

        result = simulator.simulate(dist, num_simulations=1, seed=42)

        assert result.num_simulations == 1
        assert len(result.scenarios) == 1
        assert "p10" in result.revenue_percentiles
        assert "p50" in result.revenue_percentiles
        assert "p90" in result.revenue_percentiles

    def test_simulate_multiple_simulations(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test running multiple Monte Carlo simulations"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="triangular",
            parameters={
                "min": Decimal("25000000"),
                "mode": Decimal("30000000"),
                "max": Decimal("40000000")
            }
        )

        result = simulator.simulate(dist, num_simulations=50, seed=42)

        assert result.num_simulations == 50
        assert len(result.scenarios) == 50

        # Percentiles should be ordered
        assert result.revenue_percentiles["p10"] <= result.revenue_percentiles["p50"]
        assert result.revenue_percentiles["p50"] <= result.revenue_percentiles["p90"]

        # All scenarios should have revenue within bounds
        for scenario in result.scenarios:
            assert scenario.total_revenue >= Decimal("25000000")
            assert scenario.total_revenue <= Decimal("40000000")

    def test_simulate_reproducibility_with_seed(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test that simulations with same seed produce same results"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="triangular",
            parameters={
                "min": Decimal("25000000"),
                "mode": Decimal("30000000"),
                "max": Decimal("40000000")
            }
        )

        result1 = simulator.simulate(dist, num_simulations=20, seed=123)
        result2 = simulator.simulate(dist, num_simulations=20, seed=123)

        # Should produce identical results
        for i in range(20):
            assert result1.scenarios[i].total_revenue == result2.scenarios[i].total_revenue

    def test_simulate_large_n(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test convergence with large number of simulations"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="uniform",
            parameters={
                "min": Decimal("20000000"),
                "max": Decimal("40000000")
            }
        )

        # Run large simulation
        result = simulator.simulate(dist, num_simulations=500, seed=42)

        assert result.num_simulations == 500
        assert len(result.scenarios) == 500

        # For uniform distribution, P50 should be near midpoint
        midpoint = Decimal("30000000")
        p50 = result.revenue_percentiles["p50"]

        # Allow 10% tolerance due to sampling variance
        tolerance = midpoint * Decimal("0.1")
        assert abs(p50 - midpoint) < tolerance

    def test_simulate_stakeholder_percentiles(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test that stakeholder percentiles are calculated"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="triangular",
            parameters={
                "min": Decimal("25000000"),
                "mode": Decimal("30000000"),
                "max": Decimal("40000000")
            }
        )

        result = simulator.simulate(dist, num_simulations=30, seed=42)

        # Should have stakeholder percentiles
        assert len(result.stakeholder_percentiles) > 0

        for stakeholder_id, percentiles in result.stakeholder_percentiles.items():
            # Should have IRR percentiles
            assert "irr_p10" in percentiles
            assert "irr_p50" in percentiles
            assert "irr_p90" in percentiles

            # Should have CoC percentiles
            assert "coc_p10" in percentiles
            assert "coc_p50" in percentiles
            assert "coc_p90" in percentiles

            # Percentiles should be ordered
            assert percentiles["irr_p10"] <= percentiles["irr_p50"] <= percentiles["irr_p90"]
            assert percentiles["coc_p10"] <= percentiles["coc_p50"] <= percentiles["coc_p90"]

    def test_simulate_probability_of_recoupment(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test probability of recoupment calculation"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="triangular",
            parameters={
                "min": Decimal("25000000"),
                "mode": Decimal("30000000"),
                "max": Decimal("40000000")
            }
        )

        result = simulator.simulate(dist, num_simulations=50, seed=42)

        # Should have probability of recoupment for each stakeholder
        assert len(result.probability_of_recoupment) > 0

        for stakeholder_id, probability in result.probability_of_recoupment.items():
            # Probability should be between 0 and 1
            assert probability >= Decimal("0")
            assert probability <= Decimal("1")

    def test_simulate_metadata(self, simple_waterfall, simple_capital_stack, base_projection):
        """Test that simulation metadata is captured"""
        simulator = MonteCarloSimulator(simple_waterfall, simple_capital_stack, base_projection)

        dist = RevenueDistribution(
            variable_name="total_revenue",
            distribution_type="triangular",
            parameters={
                "min": Decimal("25000000"),
                "mode": Decimal("30000000"),
                "max": Decimal("40000000")
            }
        )

        result = simulator.simulate(dist, num_simulations=10, seed=999)

        assert result.metadata["distribution"] == "triangular"
        assert result.metadata["seed"] == 999
