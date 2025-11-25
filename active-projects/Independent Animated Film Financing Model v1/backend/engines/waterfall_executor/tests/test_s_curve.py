"""
Comprehensive unit tests for S-curve functions.

Tests the s_curve, s_curve_distribution, and InvestmentDrawdown
implementations used for modeling realistic cash flow patterns.
"""

import math
import pytest
from decimal import Decimal
from typing import List

from engines.waterfall_executor.revenue_projector import (
    s_curve,
    s_curve_distribution,
    InvestmentDrawdown
)


class TestSCurveFunction:
    """Tests for the s_curve logistic function."""

    def test_midpoint_returns_approximately_half(self):
        """At the midpoint, s_curve should return approximately 0.5."""
        result = s_curve(t=0.5, k=10, midpoint=0.5)
        assert abs(result - 0.5) < 0.01, f"Expected ~0.5, got {result}"

    def test_t_zero_returns_low_value(self):
        """At t=0, s_curve should return a value close to 0."""
        result = s_curve(t=0.0, k=10, midpoint=0.5)
        assert result < 0.1, f"Expected value < 0.1 at t=0, got {result}"
        assert result > 0, f"Expected positive value, got {result}"

    def test_t_one_returns_high_value(self):
        """At t=1, s_curve should return a value close to 1."""
        result = s_curve(t=1.0, k=10, midpoint=0.5)
        assert result > 0.9, f"Expected value > 0.9 at t=1, got {result}"
        assert result < 1, f"Expected value < 1, got {result}"

    def test_monotonically_increasing(self):
        """S-curve should be monotonically increasing."""
        k = 10
        midpoint = 0.5

        previous = s_curve(0.0, k, midpoint)
        for t in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            current = s_curve(t, k, midpoint)
            assert current > previous, f"S-curve not increasing at t={t}"
            previous = current

    def test_different_steepness_values(self):
        """Different steepness values should affect curve sharpness."""
        t = 0.5
        midpoint = 0.5

        # Lower k = gentler slope
        gentle = s_curve(t, k=2, midpoint=midpoint)
        medium = s_curve(t, k=10, midpoint=midpoint)
        sharp = s_curve(t, k=20, midpoint=midpoint)

        # All should be near 0.5 at the midpoint
        assert abs(gentle - 0.5) < 0.01
        assert abs(medium - 0.5) < 0.01
        assert abs(sharp - 0.5) < 0.01

        # Check slope at t=0.4 (before midpoint)
        gentle_before = s_curve(0.4, k=2, midpoint=midpoint)
        sharp_before = s_curve(0.4, k=20, midpoint=midpoint)

        # Sharper curve should have lower value before midpoint
        # and higher value after midpoint
        assert gentle_before > sharp_before, "Gentler curve should have higher value before midpoint"

    def test_different_midpoint_values(self):
        """Different midpoint values should shift the curve."""
        k = 10

        early_midpoint = s_curve(0.3, k=k, midpoint=0.3)
        middle_midpoint = s_curve(0.5, k=k, midpoint=0.5)
        late_midpoint = s_curve(0.7, k=k, midpoint=0.7)

        # Each should be ~0.5 at its own midpoint
        assert abs(early_midpoint - 0.5) < 0.01
        assert abs(middle_midpoint - 0.5) < 0.01
        assert abs(late_midpoint - 0.5) < 0.01

    def test_handles_negative_t_gracefully(self):
        """S-curve should handle negative t values without error."""
        result = s_curve(t=-0.5, k=10, midpoint=0.5)
        assert isinstance(result, float)
        assert result > 0
        assert result < 0.1, "Negative t should give very low value"

    def test_handles_t_greater_than_one(self):
        """S-curve should handle t > 1 without error."""
        result = s_curve(t=1.5, k=10, midpoint=0.5)
        assert isinstance(result, float)
        assert result > 0.9, "t > 1 should give very high value"
        assert result < 1, "Should still be less than 1"

    def test_symmetry_around_midpoint(self):
        """S-curve should be symmetric around the midpoint."""
        k = 10
        midpoint = 0.5

        # Distance from midpoint
        delta = 0.1

        value_before = s_curve(midpoint - delta, k, midpoint)
        value_after = s_curve(midpoint + delta, k, midpoint)

        # Should be symmetric: before is as far from 0.5 as after
        distance_before = 0.5 - value_before
        distance_after = value_after - 0.5

        assert abs(distance_before - distance_after) < 0.01, \
            f"Not symmetric: {distance_before} vs {distance_after}"


class TestSCurveDistributionValidation:
    """Tests for s_curve_distribution input validation (QC Fixes)."""

    def test_negative_total_raises_value_error(self):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            s_curve_distribution(Decimal("-1000000"), periods=12)

        assert "total must be non-negative" in str(exc_info.value)
        assert "-1000000" in str(exc_info.value)

    def test_zero_total_is_valid(self):
        """Test that zero total is valid (returns distribution of zeros)."""
        distribution = s_curve_distribution(Decimal("0"), periods=12)

        assert len(distribution) == 12
        assert sum(distribution) == Decimal("0")
        assert all(amount == Decimal("0") for amount in distribution)

    def test_steepness_zero_raises_value_error(self):
        """Test that steepness <= 0 raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            s_curve_distribution(Decimal("1000000"), periods=12, steepness=0)

        assert "steepness must be positive" in str(exc_info.value)
        assert "0" in str(exc_info.value)

    def test_steepness_negative_raises_value_error(self):
        """Test that negative steepness raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            s_curve_distribution(Decimal("1000000"), periods=12, steepness=-5.0)

        assert "steepness must be positive" in str(exc_info.value)
        assert "-5" in str(exc_info.value)

    def test_very_small_positive_steepness_is_valid(self):
        """Test that very small positive steepness values are accepted."""
        # Should not raise
        distribution = s_curve_distribution(Decimal("1000000"), periods=12, steepness=0.001)

        assert len(distribution) == 12
        assert sum(distribution) == Decimal("1000000")

    def test_very_large_steepness_is_valid(self):
        """Test that very large steepness values are accepted."""
        # Should not raise
        distribution = s_curve_distribution(Decimal("1000000"), periods=12, steepness=1000.0)

        assert len(distribution) == 12
        assert sum(distribution) == Decimal("1000000")

    def test_negative_total_with_valid_steepness_raises_error(self):
        """Test that negative total raises ValueError even with valid steepness."""
        with pytest.raises(ValueError) as exc_info:
            s_curve_distribution(Decimal("-100"), periods=12, steepness=8.0)

        assert "total must be non-negative" in str(exc_info.value)

    def test_steepness_zero_with_valid_total_raises_error(self):
        """Test that steepness=0 raises ValueError even with valid total."""
        with pytest.raises(ValueError) as exc_info:
            s_curve_distribution(Decimal("1000000"), periods=12, steepness=0.0)

        assert "steepness must be positive" in str(exc_info.value)


class TestSCurveDistribution:
    """Tests for s_curve_distribution function."""

    def test_sum_equals_total(self):
        """Sum of distributed periods should equal the total."""
        total = Decimal("1000000")
        periods = 12

        distribution = s_curve_distribution(total, periods)

        assert len(distribution) == periods
        assert sum(distribution) == total

    def test_distribution_follows_s_curve_pattern(self):
        """Distribution should follow S-curve pattern: slow start, rapid middle, tapering end."""
        total = Decimal("1000000")
        periods = 12

        distribution = s_curve_distribution(total, periods, steepness=8, midpoint=0.5)

        # Early periods should be smaller than middle periods
        early_avg = sum(distribution[0:3]) / 3
        middle_avg = sum(distribution[4:8]) / 4

        assert middle_avg > early_avg, \
            f"Middle periods ({middle_avg}) should be larger than early ({early_avg})"

        # Late periods should be smaller than middle periods
        late_avg = sum(distribution[9:12]) / 3
        assert middle_avg > late_avg, \
            f"Middle periods ({middle_avg}) should be larger than late ({late_avg})"

    def test_works_with_different_period_counts(self):
        """Should work correctly with different numbers of periods."""
        total = Decimal("1000000")

        for periods in [1, 4, 8, 12, 24, 36]:
            distribution = s_curve_distribution(total, periods)

            assert len(distribution) == periods
            assert sum(distribution) == total
            assert all(amount >= 0 for amount in distribution), \
                f"All amounts should be non-negative for {periods} periods"

    def test_single_period_returns_total(self):
        """With 1 period, should return the full total."""
        total = Decimal("1000000")

        distribution = s_curve_distribution(total, periods=1)

        assert len(distribution) == 1
        assert distribution[0] == total

    def test_zero_periods_returns_empty_list(self):
        """With 0 periods, should return empty list."""
        total = Decimal("1000000")

        distribution = s_curve_distribution(total, periods=0)

        assert distribution == []

    def test_different_steepness_values(self):
        """Different steepness values should affect the distribution shape."""
        total = Decimal("1000000")
        periods = 12

        gentle = s_curve_distribution(total, periods, steepness=4, midpoint=0.5)
        sharp = s_curve_distribution(total, periods, steepness=16, midpoint=0.5)

        # Both should sum to total
        assert sum(gentle) == total
        assert sum(sharp) == total

        # Sharp curve should have more extreme differences
        gentle_range = max(gentle) - min(gentle)
        sharp_range = max(sharp) - min(sharp)

        assert sharp_range > gentle_range, \
            "Sharper curve should have larger range between min and max"

    def test_different_midpoint_values(self):
        """Different midpoint values should shift peak distribution."""
        total = Decimal("1000000")
        periods = 12

        early = s_curve_distribution(total, periods, steepness=8, midpoint=0.3)
        middle = s_curve_distribution(total, periods, steepness=8, midpoint=0.5)
        late = s_curve_distribution(total, periods, steepness=8, midpoint=0.7)

        # All should sum to total
        assert sum(early) == total
        assert sum(middle) == total
        assert sum(late) == total

        # Find index of maximum value
        early_peak = early.index(max(early))
        middle_peak = middle.index(max(middle))
        late_peak = late.index(max(late))

        # Peak should shift based on midpoint
        assert early_peak < middle_peak < late_peak, \
            f"Peak should shift: early={early_peak}, middle={middle_peak}, late={late_peak}"

    def test_all_amounts_non_negative(self):
        """All distributed amounts should be non-negative."""
        total = Decimal("1000000")
        periods = 12

        distribution = s_curve_distribution(total, periods)

        assert all(amount >= 0 for amount in distribution), \
            "All amounts should be non-negative"

    def test_precise_decimal_arithmetic(self):
        """Should use precise Decimal arithmetic throughout."""
        total = Decimal("1000000.123456789")
        periods = 12

        distribution = s_curve_distribution(total, periods)

        # Sum should be exact, not close
        assert sum(distribution) == total, \
            f"Sum {sum(distribution)} should exactly equal {total}"

    def test_handles_small_totals(self):
        """Should handle small totals correctly."""
        total = Decimal("1.00")
        periods = 10

        distribution = s_curve_distribution(total, periods)

        assert len(distribution) == periods
        assert sum(distribution) == total

    def test_handles_large_totals(self):
        """Should handle large totals correctly."""
        total = Decimal("1000000000000")  # 1 trillion
        periods = 12

        distribution = s_curve_distribution(total, periods)

        assert len(distribution) == periods
        assert sum(distribution) == total


class TestInvestmentDrawdown:
    """Tests for InvestmentDrawdown class."""

    def test_create_method_works(self):
        """create() method should produce valid InvestmentDrawdown instance."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(
            total_investment=total,
            draw_periods=periods,
            steepness=8.0,
            midpoint=0.4
        )

        assert isinstance(drawdown, InvestmentDrawdown)
        assert drawdown.total_investment == total
        assert drawdown.draw_periods == periods
        assert drawdown.steepness == 8.0
        assert drawdown.midpoint == 0.4
        assert len(drawdown.quarterly_draws) == periods
        assert len(drawdown.cumulative_draws) == periods

    def test_quarterly_draws_sum_to_total(self):
        """Quarterly draws should sum exactly to total_investment."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(total, periods)

        draws_sum = sum(drawdown.quarterly_draws)
        assert draws_sum == total, \
            f"Draws sum {draws_sum} should equal total {total}"

    def test_cumulative_draws_increase_monotonically(self):
        """Cumulative draws should increase monotonically."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(total, periods)

        for i in range(1, len(drawdown.cumulative_draws)):
            assert drawdown.cumulative_draws[i] > drawdown.cumulative_draws[i-1], \
                f"Cumulative draws should increase: period {i-1}={drawdown.cumulative_draws[i-1]}, period {i}={drawdown.cumulative_draws[i]}"

    def test_cumulative_draws_final_equals_total(self):
        """Final cumulative draw should equal total investment."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(total, periods)

        assert drawdown.cumulative_draws[-1] == total, \
            f"Final cumulative {drawdown.cumulative_draws[-1]} should equal total {total}"

    def test_different_draw_periods(self):
        """Should work correctly with different draw period counts."""
        total = Decimal("5000000")

        for periods in [4, 8, 12, 16, 24]:
            drawdown = InvestmentDrawdown.create(total, periods)

            assert len(drawdown.quarterly_draws) == periods
            assert len(drawdown.cumulative_draws) == periods
            assert sum(drawdown.quarterly_draws) == total
            assert drawdown.cumulative_draws[-1] == total

    def test_different_steepness_values(self):
        """Different steepness values should affect draw patterns."""
        total = Decimal("5000000")
        periods = 12

        gentle = InvestmentDrawdown.create(total, periods, steepness=4.0)
        sharp = InvestmentDrawdown.create(total, periods, steepness=16.0)

        # Both should sum to total
        assert sum(gentle.quarterly_draws) == total
        assert sum(sharp.quarterly_draws) == total

        # Sharp curve should have more extreme variation
        gentle_range = max(gentle.quarterly_draws) - min(gentle.quarterly_draws)
        sharp_range = max(sharp.quarterly_draws) - min(sharp.quarterly_draws)

        assert sharp_range > gentle_range, \
            "Sharper curve should have larger range"

    def test_different_midpoint_values(self):
        """Different midpoint values should shift peak draw timing."""
        total = Decimal("5000000")
        periods = 12

        early = InvestmentDrawdown.create(total, periods, midpoint=0.3)
        middle = InvestmentDrawdown.create(total, periods, midpoint=0.5)
        late = InvestmentDrawdown.create(total, periods, midpoint=0.7)

        # All should sum to total
        assert sum(early.quarterly_draws) == total
        assert sum(middle.quarterly_draws) == total
        assert sum(late.quarterly_draws) == total

        # Peak draw should occur at different times
        early_peak = early.quarterly_draws.index(max(early.quarterly_draws))
        middle_peak = middle.quarterly_draws.index(max(middle.quarterly_draws))
        late_peak = late.quarterly_draws.index(max(late.quarterly_draws))

        assert early_peak <= middle_peak <= late_peak, \
            f"Peak should shift: early={early_peak}, middle={middle_peak}, late={late_peak}"

    def test_accepts_non_decimal_total(self):
        """Should accept and convert non-Decimal total_investment."""
        drawdown = InvestmentDrawdown.create(
            total_investment=5000000,  # int, not Decimal
            draw_periods=12
        )

        assert isinstance(drawdown.total_investment, Decimal)
        assert drawdown.total_investment == Decimal("5000000")

    def test_to_dict_method(self):
        """to_dict() should produce serializable dictionary."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(total, periods, steepness=8.0, midpoint=0.4)
        result = drawdown.to_dict()

        assert isinstance(result, dict)
        assert result["total_investment"] == str(total)
        assert result["draw_periods"] == periods
        assert result["steepness"] == 8.0
        assert result["midpoint"] == 0.4
        assert len(result["quarterly_draws"]) == periods
        assert len(result["cumulative_draws"]) == periods

        # All amounts should be strings
        assert all(isinstance(d, str) for d in result["quarterly_draws"])
        assert all(isinstance(c, str) for c in result["cumulative_draws"])

    def test_get_draw_percentage(self):
        """get_draw_percentage() should return correct percentages."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(total, periods)

        # First period should be small percentage
        first_pct = drawdown.get_draw_percentage(0)
        assert first_pct > 0
        assert first_pct < 20, f"First period {first_pct}% should be < 20%"

        # Last period should be 100%
        last_pct = drawdown.get_draw_percentage(periods - 1)
        assert last_pct == Decimal("100"), f"Last period should be 100%, got {last_pct}"

        # Percentages should increase
        for i in range(1, periods):
            prev_pct = drawdown.get_draw_percentage(i - 1)
            curr_pct = drawdown.get_draw_percentage(i)
            assert curr_pct > prev_pct, \
                f"Percentage should increase: period {i-1}={prev_pct}%, period {i}={curr_pct}%"

    def test_get_draw_percentage_out_of_bounds(self):
        """get_draw_percentage() should handle out-of-bounds indices."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(total, periods)

        # Negative index should return 0%
        assert drawdown.get_draw_percentage(-1) == Decimal("0")
        assert drawdown.get_draw_percentage(-5) == Decimal("0")

        # Index >= periods should return 100%
        assert drawdown.get_draw_percentage(periods) == Decimal("100")
        assert drawdown.get_draw_percentage(periods + 5) == Decimal("100")

    def test_front_loaded_with_early_midpoint(self):
        """With early midpoint, draws should be front-loaded."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(total, periods, midpoint=0.3)

        # First half should have more than 60% of total
        first_half = sum(drawdown.quarterly_draws[:6])
        first_half_pct = (first_half / total) * 100

        assert first_half_pct > 60, \
            f"With early midpoint, first half should have > 60%, got {first_half_pct}%"

    def test_back_loaded_with_late_midpoint(self):
        """With late midpoint, draws should be back-loaded."""
        total = Decimal("5000000")
        periods = 12

        drawdown = InvestmentDrawdown.create(total, periods, midpoint=0.7)

        # Second half should have more than 60% of total
        second_half = sum(drawdown.quarterly_draws[6:])
        second_half_pct = (second_half / total) * 100

        assert second_half_pct > 60, \
            f"With late midpoint, second half should have > 60%, got {second_half_pct}%"

    def test_realistic_film_production_scenario(self):
        """Test realistic film production draw schedule."""
        # $10M film budget drawn over 18 months
        total = Decimal("10000000")
        periods = 18

        # Production-heavy at 40% of timeline (period 7-8)
        drawdown = InvestmentDrawdown.create(
            total_investment=total,
            draw_periods=periods,
            steepness=8.0,
            midpoint=0.4  # Peak at 40% through timeline
        )

        # Verify basic properties
        assert sum(drawdown.quarterly_draws) == total
        assert drawdown.cumulative_draws[-1] == total

        # First 3 months (pre-production) should be < 15%
        pre_prod_pct = drawdown.get_draw_percentage(2)
        assert pre_prod_pct < 15, \
            f"Pre-production (3 months) should be < 15%, got {pre_prod_pct}%"

        # By month 9 (halfway), should be > 65% drawn (front-loaded with 0.4 midpoint)
        halfway_pct = drawdown.get_draw_percentage(8)
        assert halfway_pct > 65, \
            f"Halfway through should be > 65% drawn, got {halfway_pct}%"

        # Final 3 months (post-production wrap) should be < 10% of remaining
        final_three = sum(drawdown.quarterly_draws[-3:])
        final_three_pct = (final_three / total) * 100
        assert final_three_pct < 10, \
            f"Final 3 months should be < 10% of total, got {final_three_pct}%"
