"""
Unit Tests for CashFlowProjector

Tests covering cash flow projection, timing distribution, S-curve generation,
and scenario comparison.
"""

import pytest
from decimal import Decimal
from pathlib import Path

from engines.incentive_calculator import (
    CashFlowProjector,
    CashFlowEvent,
    CashFlowProjection,
    IncentiveCalculator,
    JurisdictionSpend,
    PolicyLoader,
    PolicyRegistry,
)
from models.incentive_policy import MonetizationMethod


@pytest.fixture
def policies_dir():
    """Get path to policies directory"""
    base_path = Path(__file__).parent.parent.parent.parent
    return base_path / "data" / "policies"


@pytest.fixture
def loader(policies_dir):
    """Create PolicyLoader"""
    return PolicyLoader(policies_dir)


@pytest.fixture
def registry(loader):
    """Create PolicyRegistry"""
    return PolicyRegistry(loader)


@pytest.fixture
def calculator(registry):
    """Create IncentiveCalculator"""
    return IncentiveCalculator(registry)


@pytest.fixture
def projector():
    """Create CashFlowProjector"""
    return CashFlowProjector()


@pytest.fixture
def sample_incentive_result(calculator):
    """Create sample incentive result for testing"""
    uk_spend = JurisdictionSpend(
        jurisdiction="United Kingdom",
        policy_ids=["UK-AVEC-2025"],
        qualified_spend=Decimal("5000000"),
        total_spend=Decimal("6000000"),
        labor_spend=Decimal("3000000")
    )

    return calculator.calculate_single_jurisdiction(
        policy_id="UK-AVEC-2025",
        jurisdiction_spend=uk_spend,
        monetization_method=MonetizationMethod.DIRECT_CASH
    )


class TestCashFlowEvent:
    """Test CashFlowEvent dataclass"""

    def test_cash_flow_event_initialization(self):
        """Test CashFlowEvent initialization"""
        event = CashFlowEvent(
            month=5,
            event_type="production_spend",
            description="Production spending - Month 6",
            amount=Decimal("-500000"),
            cumulative_balance=Decimal("-2500000")
        )

        assert event.month == 5
        assert event.event_type == "production_spend"
        assert event.amount == Decimal("-500000")
        assert event.policy_id is None

    def test_cash_flow_event_to_dict(self):
        """Test CashFlowEvent serialization"""
        event = CashFlowEvent(
            month=10,
            event_type="incentive_receipt",
            description="UK AVEC",
            amount=Decimal("1950000"),
            cumulative_balance=Decimal("500000"),
            policy_id="UK-AVEC-2025"
        )

        event_dict = event.to_dict()

        assert event_dict["month"] == 10
        assert event_dict["event_type"] == "incentive_receipt"
        assert event_dict["policy_id"] == "UK-AVEC-2025"
        assert isinstance(event_dict["amount"], str)


class TestSCurveGeneration:
    """Test S-curve spend profile generation"""

    def test_generate_s_curve_18_months(self, projector):
        """Test S-curve generation for 18-month production"""
        curve = projector._generate_s_curve(18)

        # Should have 18 entries
        assert len(curve) == 18

        # Should sum to 1.0 (100%)
        total = sum(curve)
        assert abs(total - Decimal("1.0")) < Decimal("0.01")

        # All values should be positive
        assert all(c > Decimal("0") for c in curve)

        # Peak spending should be in reasonable range (not first or last month)
        max_spend_month = curve.index(max(curve))
        assert 0 < max_spend_month < len(curve) - 1

    def test_generate_s_curve_12_months(self, projector):
        """Test S-curve generation for 12-month production"""
        curve = projector._generate_s_curve(12)

        assert len(curve) == 12
        assert abs(sum(curve) - Decimal("1.0")) < Decimal("0.01")

    def test_generate_s_curve_short_production(self, projector):
        """Test S-curve for very short production (3 months)"""
        curve = projector._generate_s_curve(3)

        assert len(curve) == 3
        # Short productions should have even distribution
        assert abs(sum(curve) - Decimal("1.0")) < Decimal("0.01")

    def test_generate_s_curve_invalid_months(self, projector):
        """Test S-curve raises error for invalid months"""
        with pytest.raises(ValueError, match="at least 1 month"):
            projector._generate_s_curve(0)

        with pytest.raises(ValueError, match="at least 1 month"):
            projector._generate_s_curve(-5)


class TestCashFlowProjection:
    """Test cash flow projection"""

    def test_project_single_jurisdiction(self, projector, sample_incentive_result):
        """Test cash flow projection for single jurisdiction"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000"),
            labor_spend=Decimal("3000000")
        )

        projection = projector.project(
            production_budget=Decimal("6000000"),
            production_schedule_months=18,
            jurisdiction_spends=[uk_spend],
            incentive_results=[sample_incentive_result]
        )

        # Should have production spend events (18) + incentive receipt (1)
        assert len(projection.events) == 19

        # Should have correct production period
        assert projection.production_period_months == 18

        # Should have positive peak funding requirement
        assert projection.peak_funding_required > Decimal("0")

        # Total incentive receipts should match result
        assert projection.total_incentive_receipts == sample_incentive_result.net_cash_benefit

    def test_project_with_custom_spend_curve(self, projector, sample_incentive_result):
        """Test projection with custom spend curve"""
        # Custom 6-month even distribution
        custom_curve = [Decimal("1.0") / Decimal("6")] * 6

        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000"),
            labor_spend=Decimal("3000000")
        )

        projection = projector.project(
            production_budget=Decimal("6000000"),
            production_schedule_months=6,
            jurisdiction_spends=[uk_spend],
            incentive_results=[sample_incentive_result],
            spend_curve=custom_curve
        )

        # Should use custom curve
        assert len([e for e in projection.events if e.event_type == "production_spend"]) == 6

        # Each month should have ~equal spend
        monthly_spends = [e.amount for e in projection.events if e.event_type == "production_spend"]
        assert all(abs(s - monthly_spends[0]) < Decimal("1") for s in monthly_spends)

    def test_project_invalid_spend_curve_length(self, projector, sample_incentive_result):
        """Test projection raises error when spend curve length mismatches"""
        # Wrong length curve
        wrong_curve = [Decimal("0.5"), Decimal("0.5")]  # 2 months

        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000")
        )

        with pytest.raises(ValueError, match="Spend curve length"):
            projector.project(
                production_budget=Decimal("6000000"),
                production_schedule_months=18,  # But curve is 2!
                jurisdiction_spends=[uk_spend],
                incentive_results=[sample_incentive_result],
                spend_curve=wrong_curve
            )

    def test_project_invalid_spend_curve_sum(self, projector, sample_incentive_result):
        """Test projection raises error when spend curve doesn't sum to 1.0"""
        # Curve that doesn't sum to 1.0
        invalid_curve = [Decimal("0.25")] * 6  # Sums to 1.5

        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000")
        )

        with pytest.raises(ValueError, match="must sum to 1.0"):
            projector.project(
                production_budget=Decimal("6000000"),
                production_schedule_months=6,
                jurisdiction_spends=[uk_spend],
                incentive_results=[sample_incentive_result],
                spend_curve=invalid_curve
            )

    def test_projection_events_sorted_by_month(self, projector, sample_incentive_result):
        """Test that events are sorted chronologically"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000")
        )

        projection = projector.project(
            production_budget=Decimal("6000000"),
            production_schedule_months=12,
            jurisdiction_spends=[uk_spend],
            incentive_results=[sample_incentive_result]
        )

        # Events should be sorted by month
        months = [e.month for e in projection.events]
        assert months == sorted(months)

    def test_projection_cumulative_balance(self, projector, sample_incentive_result):
        """Test cumulative balance calculation"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000")
        )

        projection = projector.project(
            production_budget=Decimal("6000000"),
            production_schedule_months=12,
            jurisdiction_spends=[uk_spend],
            incentive_results=[sample_incentive_result]
        )

        # Manually verify cumulative balance
        running_balance = Decimal("0")
        for event in projection.events:
            running_balance += event.amount
            assert event.cumulative_balance == running_balance

    def test_projection_final_balance(self, projector, sample_incentive_result):
        """Test final balance calculation"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000")
        )

        projection = projector.project(
            production_budget=Decimal("6000000"),
            production_schedule_months=12,
            jurisdiction_spends=[uk_spend],
            incentive_results=[sample_incentive_result]
        )

        # Final balance = incentive receipts - production budget
        expected_final = sample_incentive_result.net_cash_benefit - Decimal("6000000")
        assert projection.final_balance == expected_final


class TestMultipleIncentiveReceipts:
    """Test projections with multiple incentive receipts"""

    def test_project_multiple_incentives_different_timing(self, projector, calculator):
        """Test projection with multiple incentives received at different times"""
        quebec_spend = JurisdictionSpend(
            jurisdiction="Canada-Quebec",
            policy_ids=["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],
            qualified_spend=Decimal("10000000"),
            total_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000")
        )

        # Calculate both incentives
        federal_result = calculator.calculate_single_jurisdiction(
            policy_id="CA-FEDERAL-CPTC-2025",
            jurisdiction_spend=quebec_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        provincial_result = calculator.calculate_single_jurisdiction(
            policy_id="CA-QC-PSTC-2025",
            jurisdiction_spend=quebec_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        projection = projector.project(
            production_budget=Decimal("10000000"),
            production_schedule_months=18,
            jurisdiction_spends=[quebec_spend],
            incentive_results=[federal_result, provincial_result]
        )

        # Should have 2 incentive receipt events
        incentive_events = [e for e in projection.events if e.event_type == "incentive_receipt"]
        assert len(incentive_events) == 2

        # Total receipts should match sum of both
        total_expected = federal_result.net_cash_benefit + provincial_result.net_cash_benefit
        assert projection.total_incentive_receipts == total_expected


class TestTimingComparison:
    """Test timing scenario comparisons"""

    def test_compare_timing_scenarios_loan_vs_direct(self, projector, calculator):
        """Test comparison of loan vs direct cash timing"""
        georgia_spend = JurisdictionSpend(
            jurisdiction="United States",
            policy_ids=["US-GA-GEFA-2025"],
            qualified_spend=Decimal("8000000"),
            total_spend=Decimal("8000000"),
            labor_spend=Decimal("6000000")
        )

        # Direct cash scenario
        direct_result = calculator.calculate_single_jurisdiction(
            policy_id="US-GA-GEFA-2025",
            jurisdiction_spend=georgia_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Loan scenario
        loan_result = calculator.calculate_single_jurisdiction(
            policy_id="US-GA-GEFA-2025",
            jurisdiction_spend=georgia_spend,
            monetization_method=MonetizationMethod.TAX_CREDIT_LOAN,
            transfer_discount=Decimal("10.0")
        )

        # Create projections
        direct_projection = projector.project(
            production_budget=Decimal("8000000"),
            production_schedule_months=18,
            jurisdiction_spends=[georgia_spend],
            incentive_results=[direct_result]
        )

        loan_projection = projector.project(
            production_budget=Decimal("8000000"),
            production_schedule_months=18,
            jurisdiction_spends=[georgia_spend],
            incentive_results=[loan_result]
        )

        # Compare
        comparison = projector.compare_timing_scenarios(
            base_projection=direct_projection,
            loan_projection=loan_projection
        )

        # Loan should provide cash earlier
        assert comparison["months_earlier"] >= 0

        # Loan cost should be calculated
        assert "loan_cost" in comparison
        assert comparison["loan_cost"] >= Decimal("0")

        # Peak funding difference should be calculated
        assert "peak_funding_difference" in comparison


class TestMonthlyView:
    """Test monthly view generation"""

    def test_monthly_view_dict(self, projector, sample_incentive_result):
        """Test monthly view dictionary generation"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000")
        )

        projection = projector.project(
            production_budget=Decimal("6000000"),
            production_schedule_months=12,
            jurisdiction_spends=[uk_spend],
            incentive_results=[sample_incentive_result]
        )

        monthly_view = projector.monthly_view_dict(projection)

        # Should have entries for all months
        assert len(monthly_view) > 12  # Production + receipt timing

        # Each month should have required fields
        for month, data in monthly_view.items():
            assert "spend" in data
            assert "incentive_receipts" in data
            assert "net_cash_flow" in data
            assert "cumulative_balance" in data
            assert "events" in data

        # Production months should have spend
        assert monthly_view[0]["spend"] > Decimal("0")

        # Sum of all spends should equal budget
        total_spend = sum(v["spend"] for v in monthly_view.values())
        assert abs(total_spend - Decimal("6000000")) < Decimal("10")

        # Sum of all receipts should equal incentive
        total_receipts = sum(v["incentive_receipts"] for v in monthly_view.values())
        assert total_receipts == sample_incentive_result.net_cash_benefit


class TestCashFlowProjectionSerialization:
    """Test CashFlowProjection to_dict() method"""

    def test_cash_flow_projection_to_dict(self, projector, sample_incentive_result):
        """Test CashFlowProjection serialization"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000")
        )

        projection = projector.project(
            production_budget=Decimal("6000000"),
            production_schedule_months=12,
            jurisdiction_spends=[uk_spend],
            incentive_results=[sample_incentive_result]
        )

        proj_dict = projection.to_dict()

        # Verify all fields are present
        assert "project_start_month" in proj_dict
        assert "production_period_months" in proj_dict
        assert "events" in proj_dict
        assert "monthly_summary" in proj_dict
        assert "cumulative_summary" in proj_dict
        assert "peak_funding_required" in proj_dict
        assert "total_incentive_receipts" in proj_dict
        assert "final_balance" in proj_dict

        # Verify Decimal fields are converted to strings
        assert isinstance(proj_dict["peak_funding_required"], str)
        assert isinstance(proj_dict["final_balance"], str)

        # Verify events are serialized
        assert isinstance(proj_dict["events"], list)
        assert all(isinstance(e, dict) for e in proj_dict["events"])
