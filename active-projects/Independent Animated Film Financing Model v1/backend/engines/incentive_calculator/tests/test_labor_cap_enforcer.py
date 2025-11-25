"""
Tests for LaborCapEnforcer

Comprehensive tests covering labor cap enforcement, labor-specific rates,
VFX/animation special rates, labor uplift, and edge cases.
"""

import pytest
from decimal import Decimal
from datetime import date

from engines.incentive_calculator.labor_cap_enforcer import (
    LaborCapEnforcer,
    LaborEnforcementResult,
    LaborAdjustment
)
from models.incentive_policy import (
    IncentivePolicy,
    QPEDefinition,
    QPECategory,
    IncentiveType,
    MonetizationMethod,
    CulturalTest
)


# ============= Test Fixtures and Helpers =============

@pytest.fixture
def enforcer():
    """Create LaborCapEnforcer instance"""
    return LaborCapEnforcer()


def create_mock_policy(
    policy_id: str,
    headline_rate: Decimal,
    labor_max_percent: Decimal = None,
    labor_specific_rate: Decimal = None,
    labor_uplift_rate: Decimal = None,
    vfx_animation_rate: Decimal = None,
    labor_only_credit: bool = False,
    labor_resident_rate: Decimal = None,
    labor_nonresident_rate: Decimal = None
) -> IncentivePolicy:
    """Create a mock policy for testing labor cap enforcement"""
    qpe_def = QPEDefinition(
        included_categories=[
            QPECategory.LABOR_RESIDENT,
            QPECategory.LABOR_NON_RESIDENT,
            QPECategory.GOODS_SERVICES_LOCAL,
            QPECategory.VFX_ANIMATION
        ],
        excludes_financing_costs=True,
        excludes_distribution_costs=True,
        labor_max_percent_of_spend=labor_max_percent,
        labor_specific_rate=labor_specific_rate,
        labor_uplift_rate=labor_uplift_rate,
        vfx_animation_rate=vfx_animation_rate,
        labor_only_credit=labor_only_credit,
        labor_resident_rate=labor_resident_rate,
        labor_nonresident_rate=labor_nonresident_rate
    )

    return IncentivePolicy(
        policy_id=policy_id,
        jurisdiction="Test Country",
        program_name="Test Program",
        headline_rate=headline_rate,
        incentive_type=IncentiveType.REFUNDABLE_TAX_CREDIT,
        qpe_definition=qpe_def,
        monetization_methods=[MonetizationMethod.DIRECT_CASH],
        last_updated=date.today(),
        cultural_test=CulturalTest(requires_cultural_test=False)
    )


# ============= Basic Labor Cap Enforcement Tests =============

class TestBasicLaborCapEnforcement:
    """Tests for basic labor cap enforcement (e.g., CPTC 60% cap)"""

    def test_labor_within_cap_no_adjustment(self, enforcer):
        """Test labor spend within cap requires no adjustment"""
        # 60% cap, labor is 50% of qualified spend
        policy = create_mock_policy(
            policy_id="TEST-CAP-60",
            headline_rate=Decimal("25.0"),
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("5000000")  # 50% of qualified spend
        )

        # No adjustment should be made
        assert result.adjusted_labor_spend == Decimal("5000000")
        assert result.adjusted_qualified_spend == Decimal("10000000")
        assert result.labor_cap_applied is False
        assert len(result.adjustments) == 0
        assert len(result.warnings) == 0

    def test_labor_at_cap_no_adjustment(self, enforcer):
        """Test labor spend exactly at cap requires no adjustment"""
        policy = create_mock_policy(
            policy_id="TEST-CAP-60",
            headline_rate=Decimal("25.0"),
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000")  # Exactly 60%
        )

        assert result.adjusted_labor_spend == Decimal("6000000")
        assert result.labor_cap_applied is False
        assert len(result.adjustments) == 0

    def test_labor_exceeds_cap_adjustment_applied(self, enforcer):
        """Test labor exceeding cap is adjusted down"""
        # CPTC-style: 60% cap
        policy = create_mock_policy(
            policy_id="TEST-CPTC-60",
            headline_rate=Decimal("25.0"),
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000")  # 80%, exceeds 60% cap
        )

        # Labor should be capped at 60% of $10M = $6M
        expected_labor = Decimal("6000000")
        assert result.adjusted_labor_spend == expected_labor
        assert result.labor_cap_applied is True

        # Should have one adjustment
        assert len(result.adjustments) == 1
        adjustment = result.adjustments[0]
        assert adjustment.adjustment_type == "percent_cap"
        assert adjustment.original_amount == Decimal("8000000")
        assert adjustment.adjusted_amount == expected_labor
        assert adjustment.reduction == Decimal("2000000")
        assert "60" in adjustment.description

    def test_labor_cap_70_percent(self, enforcer):
        """Test 70% labor cap scenario"""
        policy = create_mock_policy(
            policy_id="TEST-CAP-70",
            headline_rate=Decimal("30.0"),
            labor_max_percent=Decimal("70.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("5000000"),
            labor_spend=Decimal("4000000")  # 80%, exceeds 70%
        )

        # Should be capped at 70% of $5M = $3.5M
        expected_labor = Decimal("3500000")
        assert result.adjusted_labor_spend == expected_labor
        assert result.labor_cap_applied is True

        # Verify reduction
        adjustment = result.adjustments[0]
        assert adjustment.reduction == Decimal("500000")


# ============= Labor-Only Credit Tests =============

class TestLaborOnlyCredit:
    """Tests for labor-only credit policies (e.g., Ontario OCASE)"""

    def test_labor_only_credit_basic(self, enforcer):
        """Test basic labor-only credit scenario"""
        # Ontario OCASE-style: only labor qualifies
        policy = create_mock_policy(
            policy_id="TEST-OCASE",
            headline_rate=Decimal("18.0"),
            labor_only_credit=True
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),  # Total spend
            labor_spend=Decimal("6000000")  # Only this qualifies
        )

        # Qualified spend should be reduced to labor spend only
        assert result.adjusted_qualified_spend == Decimal("6000000")
        assert result.adjusted_labor_spend == Decimal("6000000")

        # Should have labor_only adjustment
        assert len(result.adjustments) == 1
        adjustment = result.adjustments[0]
        assert adjustment.adjustment_type == "labor_only"
        assert adjustment.original_amount == Decimal("10000000")
        assert adjustment.adjusted_amount == Decimal("6000000")
        assert adjustment.reduction == Decimal("4000000")

        # Non-labor credit should be zero
        assert result.non_labor_credit_component == Decimal("0")

        # Total credit should be labor only: $6M * 18% = $1,080,000
        expected_credit = Decimal("6000000") * Decimal("0.18")
        assert result.total_credit == expected_credit
        assert result.labor_credit_component == expected_credit

    def test_labor_only_with_cap(self, enforcer):
        """Test labor-only credit combined with percentage cap"""
        policy = create_mock_policy(
            policy_id="TEST-LABOR-ONLY-CAP",
            headline_rate=Decimal("20.0"),
            labor_only_credit=True,
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000")  # Exceeds 60% cap
        )

        # Labor should be capped first, then qualified spend adjusted
        expected_labor = Decimal("6000000")  # 60% of $10M
        assert result.adjusted_labor_spend == expected_labor
        assert result.adjusted_qualified_spend == expected_labor  # Labor only

        # Should have both adjustments
        assert len(result.adjustments) == 2
        assert result.labor_cap_applied is True


# ============= VFX/Animation Special Rate Tests =============

class TestVFXAnimationRates:
    """Tests for VFX/animation special rates"""

    def test_vfx_special_rate_basic(self, enforcer):
        """Test VFX labor at special rate"""
        # Quebec-style: animation has special rate
        policy = create_mock_policy(
            policy_id="TEST-QC-ANIMATION",
            headline_rate=Decimal("36.0"),
            vfx_animation_rate=Decimal("45.0")  # Higher for VFX
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000"),
            vfx_labor_spend=Decimal("2000000")
        )

        # VFX labor: $2M * 45% = $900,000
        expected_vfx_credit = Decimal("2000000") * Decimal("0.45")

        # Regular labor: $4M * 36% = $1,440,000
        regular_labor = Decimal("4000000")
        expected_regular_credit = regular_labor * Decimal("0.36")

        # Total labor credit
        expected_labor_credit = expected_vfx_credit + expected_regular_credit
        assert result.labor_credit_component == expected_labor_credit

        # Should have VFX adjustment
        vfx_adjustments = [a for a in result.adjustments if a.adjustment_type == "vfx_rate"]
        assert len(vfx_adjustments) == 1

    def test_vfx_exceeds_total_labor(self, enforcer):
        """Test VFX labor capped at total labor spend"""
        policy = create_mock_policy(
            policy_id="TEST-VFX",
            headline_rate=Decimal("30.0"),
            vfx_animation_rate=Decimal("40.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("5000000"),
            vfx_labor_spend=Decimal("7000000")  # Exceeds total labor
        )

        # VFX should be capped at total labor
        # All labor treated as VFX: $5M * 40% = $2M
        expected_credit = Decimal("5000000") * Decimal("0.40")
        assert result.labor_credit_component == expected_credit

    def test_vfx_with_labor_cap(self, enforcer):
        """Test VFX rate with labor percentage cap"""
        policy = create_mock_policy(
            policy_id="TEST-VFX-CAP",
            headline_rate=Decimal("25.0"),
            labor_max_percent=Decimal("60.0"),
            vfx_animation_rate=Decimal("35.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000"),  # Exceeds 60% cap
            vfx_labor_spend=Decimal("3000000")
        )

        # Labor capped at 60% = $6M
        # VFX portion: min($3M, $6M) = $3M
        # Regular labor: $6M - $3M = $3M
        expected_vfx_credit = Decimal("3000000") * Decimal("0.35")
        expected_regular_credit = Decimal("3000000") * Decimal("0.25")

        assert result.labor_credit_component == expected_vfx_credit + expected_regular_credit
        assert result.labor_cap_applied is True


# ============= Labor Uplift Rate Tests =============

class TestLaborUpliftRates:
    """Tests for labor uplift rates (e.g., Quebec animation uplift)"""

    def test_labor_uplift_basic(self, enforcer):
        """Test basic labor uplift rate"""
        # Quebec animation: 36% base + 16% uplift = 52%
        policy = create_mock_policy(
            policy_id="TEST-QC-UPLIFT",
            headline_rate=Decimal("36.0"),
            labor_uplift_rate=Decimal("16.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000")
        )

        # Labor should get 36% + 16% = 52%
        effective_labor_rate = Decimal("52.0")
        expected_labor_credit = Decimal("6000000") * (effective_labor_rate / Decimal("100"))
        assert result.labor_credit_component == expected_labor_credit

        # Non-labor at base rate: $4M * 36% = $1,440,000
        expected_non_labor_credit = Decimal("4000000") * Decimal("0.36")
        assert result.non_labor_credit_component == expected_non_labor_credit

        # Should have uplift adjustment
        uplift_adjustments = [a for a in result.adjustments if a.adjustment_type == "labor_uplift"]
        assert len(uplift_adjustments) == 1
        assert "16" in uplift_adjustments[0].description

    def test_labor_uplift_with_specific_rate(self, enforcer):
        """Test uplift applied to specific labor rate, not headline rate"""
        policy = create_mock_policy(
            policy_id="TEST-UPLIFT-SPECIFIC",
            headline_rate=Decimal("30.0"),
            labor_specific_rate=Decimal("25.0"),
            labor_uplift_rate=Decimal("10.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("5000000")
        )

        # Labor: 25% + 10% = 35%
        expected_labor_credit = Decimal("5000000") * Decimal("0.35")
        assert result.labor_credit_component == expected_labor_credit

        # Non-labor at headline rate: $5M * 30%
        expected_non_labor_credit = Decimal("5000000") * Decimal("0.30")
        assert result.non_labor_credit_component == expected_non_labor_credit


# ============= Labor-Specific Rate Tests =============

class TestLaborSpecificRates:
    """Tests for labor-specific rates different from headline rate"""

    def test_labor_specific_rate_basic(self, enforcer):
        """Test labor at different rate than non-labor"""
        policy = create_mock_policy(
            policy_id="TEST-LABOR-RATE",
            headline_rate=Decimal("30.0"),
            labor_specific_rate=Decimal("20.0")  # Lower for labor
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000")
        )

        # Labor at 20%: $6M * 20% = $1,200,000
        expected_labor_credit = Decimal("6000000") * Decimal("0.20")
        assert result.labor_credit_component == expected_labor_credit

        # Non-labor at 30%: $4M * 30% = $1,200,000
        expected_non_labor_credit = Decimal("4000000") * Decimal("0.30")
        assert result.non_labor_credit_component == expected_non_labor_credit

    def test_labor_rate_higher_than_headline(self, enforcer):
        """Test labor rate higher than headline rate"""
        policy = create_mock_policy(
            policy_id="TEST-LABOR-HIGHER",
            headline_rate=Decimal("25.0"),
            labor_specific_rate=Decimal("35.0")  # Higher for labor
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("5000000")
        )

        # Labor at 35%
        expected_labor_credit = Decimal("5000000") * Decimal("0.35")
        assert result.labor_credit_component == expected_labor_credit

        # Non-labor at 25%
        expected_non_labor_credit = Decimal("5000000") * Decimal("0.25")
        assert result.non_labor_credit_component == expected_non_labor_credit


# ============= Edge Cases Tests =============

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_labor_exceeds_qualified_spend_capped(self, enforcer):
        """Test labor spend exceeding qualified spend is capped"""
        policy = create_mock_policy(
            policy_id="TEST-EDGE",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("5000000"),
            labor_spend=Decimal("7000000")  # Exceeds qualified spend!
        )

        # Labor should be capped at qualified spend
        assert result.adjusted_labor_spend == Decimal("5000000")

        # Should have warning
        assert len(result.warnings) == 1
        assert "exceeds qualified spend" in result.warnings[0]
        assert "Capping labor" in result.warnings[0]

    def test_zero_labor_spend(self, enforcer):
        """Test zero labor spend scenario"""
        policy = create_mock_policy(
            policy_id="TEST-ZERO-LABOR",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("0")
        )

        assert result.adjusted_labor_spend == Decimal("0")
        assert result.labor_credit_component == Decimal("0")

        # Non-labor credit should still apply
        expected_credit = Decimal("10000000") * Decimal("0.30")
        assert result.non_labor_credit_component == expected_credit
        assert result.total_credit == expected_credit

    def test_zero_qualified_spend(self, enforcer):
        """Test zero qualified spend scenario"""
        policy = create_mock_policy(
            policy_id="TEST-ZERO-QUALIFIED",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("0"),
            labor_spend=Decimal("0")
        )

        assert result.adjusted_qualified_spend == Decimal("0")
        assert result.adjusted_labor_spend == Decimal("0")
        assert result.total_credit == Decimal("0")
        assert result.effective_rate == Decimal("0")

    def test_labor_only_credit_zero_labor(self, enforcer):
        """Test labor-only credit with zero labor results in zero credit"""
        policy = create_mock_policy(
            policy_id="TEST-LABOR-ONLY-ZERO",
            headline_rate=Decimal("25.0"),
            labor_only_credit=True
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("0")
        )

        assert result.adjusted_qualified_spend == Decimal("0")
        assert result.total_credit == Decimal("0")

    def test_all_spend_is_labor(self, enforcer):
        """Test scenario where all qualified spend is labor"""
        policy = create_mock_policy(
            policy_id="TEST-ALL-LABOR",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("10000000")
        )

        assert result.adjusted_labor_spend == Decimal("10000000")
        assert result.non_labor_credit_component == Decimal("0")

        # All credit from labor
        expected_credit = Decimal("10000000") * Decimal("0.30")
        assert result.labor_credit_component == expected_credit
        assert result.total_credit == expected_credit

    def test_labor_cap_with_all_labor_spend(self, enforcer):
        """Test labor cap when all spend is labor"""
        policy = create_mock_policy(
            policy_id="TEST-CAP-ALL-LABOR",
            headline_rate=Decimal("25.0"),
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("10000000")  # 100% labor
        )

        # Should be capped at 60%
        expected_labor = Decimal("6000000")
        assert result.adjusted_labor_spend == expected_labor
        assert result.labor_cap_applied is True

    def test_very_small_amounts(self, enforcer):
        """Test with very small dollar amounts"""
        policy = create_mock_policy(
            policy_id="TEST-SMALL",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("100.00"),
            labor_spend=Decimal("60.00")
        )

        expected_labor_credit = Decimal("60.00") * Decimal("0.30")
        expected_non_labor_credit = Decimal("40.00") * Decimal("0.30")

        assert result.labor_credit_component == expected_labor_credit
        assert result.non_labor_credit_component == expected_non_labor_credit

    def test_decimal_precision_maintained(self, enforcer):
        """Test that Decimal precision is maintained throughout calculations"""
        policy = create_mock_policy(
            policy_id="TEST-PRECISION",
            headline_rate=Decimal("33.333333"),
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("9999999.99"),
            labor_spend=Decimal("7000000.00")
        )

        # Verify result values are Decimal type
        assert isinstance(result.adjusted_labor_spend, Decimal)
        assert isinstance(result.total_credit, Decimal)
        assert isinstance(result.effective_rate, Decimal)


# ============= Effective Rate Calculation Tests =============

class TestEffectiveRateCalculation:
    """Tests for effective rate calculation accuracy"""

    def test_effective_rate_no_adjustments(self, enforcer):
        """Test effective rate equals headline rate with no adjustments"""
        policy = create_mock_policy(
            policy_id="TEST-EFFECTIVE",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("5000000")
        )

        # Effective rate should equal headline rate
        assert result.effective_rate == Decimal("30.0")

    def test_effective_rate_with_labor_cap(self, enforcer):
        """Test effective rate is lower when labor cap reduces credit"""
        policy = create_mock_policy(
            policy_id="TEST-EFFECTIVE-CAP",
            headline_rate=Decimal("30.0"),
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("9000000")  # Would be capped to $6M
        )

        # Credit: $6M * 30% + $4M * 30% = $1.8M + $1.2M = $3M
        # Effective rate: $3M / $10M = 30% (still 30% because non-labor fills the gap)
        assert result.effective_rate == Decimal("30.0")

    def test_effective_rate_labor_only(self, enforcer):
        """Test effective rate with labor-only credit"""
        policy = create_mock_policy(
            policy_id="TEST-EFFECTIVE-LABOR-ONLY",
            headline_rate=Decimal("20.0"),
            labor_only_credit=True
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000")
        )

        # Credit: $6M * 20% = $1.2M
        # Effective rate: $1.2M / $6M = 20% (based on adjusted qualified spend)
        assert result.effective_rate == Decimal("20.0")

    def test_effective_rate_with_uplift(self, enforcer):
        """Test effective rate is higher with labor uplift"""
        policy = create_mock_policy(
            policy_id="TEST-EFFECTIVE-UPLIFT",
            headline_rate=Decimal("30.0"),
            labor_uplift_rate=Decimal("10.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("5000000")
        )

        # Labor: $5M * 40% = $2M
        # Non-labor: $5M * 30% = $1.5M
        # Total: $3.5M on $10M = 35%
        assert result.effective_rate == Decimal("35.0")

    def test_effective_rate_zero_qualified_spend(self, enforcer):
        """Test effective rate is zero when qualified spend is zero"""
        policy = create_mock_policy(
            policy_id="TEST-EFFECTIVE-ZERO",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("0"),
            labor_spend=Decimal("0")
        )

        assert result.effective_rate == Decimal("0")


# ============= QC Fixes Tests =============

class TestQCFixes:
    """Tests for Quality Control fixes and validations"""

    def test_rate_bounds_validation_base_plus_uplift_exceeds_100_percent(self, enforcer):
        """Test that base rate + uplift > 100% is capped at 100% with warning"""
        # Quebec scenario where 36% base + 100% uplift would be 136% (invalid)
        policy = create_mock_policy(
            policy_id="TEST-RATE-BOUNDS",
            headline_rate=Decimal("36.0"),
            labor_specific_rate=Decimal("80.0"),  # High base
            labor_uplift_rate=Decimal("50.0")  # High uplift, together = 130%
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000")
        )

        # Rate should be capped at 100%
        # Labor credit: $6M * 100% = $6M
        # Non-labor: $4M * 36% = $1.44M
        # Total: $7.44M
        expected_labor_credit = Decimal("6000000") * Decimal("1.0")
        expected_non_labor_credit = Decimal("4000000") * Decimal("0.36")
        expected_total = expected_labor_credit + expected_non_labor_credit

        assert result.labor_credit_component == expected_labor_credit
        assert result.non_labor_credit_component == expected_non_labor_credit
        assert result.total_credit == expected_total

        # Should have a warning about rate exceeding 100%
        assert len(result.warnings) == 1
        assert "exceeds 100" in result.warnings[0].lower()
        assert "capping" in result.warnings[0].lower()

    def test_vfx_exceeds_labor_warning(self, enforcer):
        """Test that VFX labor exceeding total labor generates warning"""
        policy = create_mock_policy(
            policy_id="TEST-VFX-WARNING",
            headline_rate=Decimal("30.0"),
            vfx_animation_rate=Decimal("40.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("4000000"),
            vfx_labor_spend=Decimal("6000000")  # Exceeds total labor!
        )

        # Should have warning about VFX exceeding labor
        assert len(result.warnings) == 1
        assert "vfx" in result.warnings[0].lower()
        assert "exceeds total labor" in result.warnings[0].lower()
        assert "capping" in result.warnings[0].lower()

        # VFX should be capped at total labor ($4M)
        # Credit: $4M * 40% = $1.6M (all as VFX)
        expected_vfx_credit = Decimal("4000000") * Decimal("0.40")
        assert result.labor_credit_component == expected_vfx_credit

    def test_resident_nonresident_rate_differentiation(self, enforcer):
        """Test resident/non-resident labor rate differentiation"""
        # Policy with different rates for resident vs non-resident labor
        policy = create_mock_policy(
            policy_id="TEST-RESIDENCY-RATES",
            headline_rate=Decimal("30.0"),
            labor_resident_rate=Decimal("35.0"),
            labor_nonresident_rate=Decimal("25.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000"),
            resident_labor_spend=Decimal("4000000"),
            nonresident_labor_spend=Decimal("2000000")
        )

        # Resident labor credit: $4M * 35% = $1.4M
        # Non-resident labor credit: $2M * 25% = $0.5M
        # Labor total: $1.9M
        # Non-labor credit: $4M * 30% = $1.2M
        # Total credit: $3.1M

        expected_resident = Decimal("4000000") * Decimal("0.35")
        expected_nonresident = Decimal("2000000") * Decimal("0.25")
        expected_labor_credit = expected_resident + expected_nonresident
        expected_non_labor_credit = Decimal("4000000") * Decimal("0.30")
        expected_total = expected_labor_credit + expected_non_labor_credit

        assert result.labor_credit_component == expected_labor_credit
        assert result.non_labor_credit_component == expected_non_labor_credit
        assert result.total_credit == expected_total

        # Should have residency rate adjustment
        residency_adjustments = [a for a in result.adjustments if a.adjustment_type == "residency_rate"]
        assert len(residency_adjustments) == 1
        adjustment = residency_adjustments[0]
        assert "resident" in adjustment.description.lower()
        assert "non-resident" in adjustment.description.lower()

    def test_resident_nonresident_with_labor_cap(self, enforcer):
        """Test residency rates combined with labor percentage cap"""
        policy = create_mock_policy(
            policy_id="TEST-RESIDENCY-WITH-CAP",
            headline_rate=Decimal("25.0"),
            labor_max_percent=Decimal("60.0"),
            labor_resident_rate=Decimal("30.0"),
            labor_nonresident_rate=Decimal("20.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000"),  # Exceeds 60% cap
            resident_labor_spend=Decimal("5000000"),
            nonresident_labor_spend=Decimal("3000000")
        )

        # Labor capped at 60% = $6M
        assert result.adjusted_labor_spend == Decimal("6000000")
        assert result.labor_cap_applied is True

        # With residency rates, the provided resident/non-resident amounts are applied directly:
        # Resident labor: $5M at 30% = $1.5M
        # Non-resident labor: $3M at 20% = $0.6M
        # (Note: Code uses provided amounts, not proportional reduction)
        # Non-labor: $4M at 25% = $1M

        expected_resident = Decimal("5000000") * Decimal("0.30")
        expected_nonresident = Decimal("3000000") * Decimal("0.20")
        expected_labor_credit = expected_resident + expected_nonresident
        expected_non_labor_credit = Decimal("4000000") * Decimal("0.25")

        assert result.labor_credit_component == expected_labor_credit
        assert result.non_labor_credit_component == expected_non_labor_credit

        # Should have both cap and residency adjustments
        assert len(result.adjustments) >= 2
        adjustment_types = [a.adjustment_type for a in result.adjustments]
        assert "percent_cap" in adjustment_types
        assert "residency_rate" in adjustment_types


# ============= Validation Tests =============

class TestValidation:
    """Tests for validate_labor_spend method"""

    def test_validate_negative_labor_spend(self, enforcer):
        """Test validation catches negative labor spend"""
        errors = enforcer.validate_labor_spend(
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("-1000000")
        )

        assert len(errors) == 1
        assert "negative" in errors[0].lower()

    def test_validate_labor_exceeds_qualified(self, enforcer):
        """Test validation catches labor exceeding qualified spend"""
        errors = enforcer.validate_labor_spend(
            qualified_spend=Decimal("5000000"),
            labor_spend=Decimal("7000000")
        )

        assert len(errors) == 1
        assert "exceeds" in errors[0].lower()

    def test_validate_multiple_errors(self, enforcer):
        """Test validation returns multiple errors"""
        errors = enforcer.validate_labor_spend(
            qualified_spend=Decimal("5000000"),
            labor_spend=Decimal("-1000000")  # Both negative AND exceeds
        )

        # Should have at least the negative error
        assert len(errors) >= 1
        assert "negative" in errors[0].lower()

    def test_validate_valid_spend(self, enforcer):
        """Test validation passes for valid spend"""
        errors = enforcer.validate_labor_spend(
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000")
        )

        assert len(errors) == 0

    def test_validate_raise_on_error(self, enforcer):
        """Test validation raises ValueError when raise_on_error=True"""
        with pytest.raises(ValueError):
            enforcer.validate_labor_spend(
                qualified_spend=Decimal("10000000"),
                labor_spend=Decimal("-1000000"),
                raise_on_error=True
            )

    def test_validate_no_raise_on_error(self, enforcer):
        """Test validation does not raise when raise_on_error=False"""
        errors = enforcer.validate_labor_spend(
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("-1000000"),
            raise_on_error=False
        )

        # Should return errors but not raise
        assert len(errors) > 0


# ============= Serialization Tests =============

class TestSerialization:
    """Tests for to_dict() serialization"""

    def test_result_to_dict_basic(self, enforcer):
        """Test basic result serialization to dict"""
        policy = create_mock_policy(
            policy_id="TEST-SERIALIZE",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000")
        )

        result_dict = result.to_dict()

        # Verify structure
        assert "adjusted_qualified_spend" in result_dict
        assert "adjusted_labor_spend" in result_dict
        assert "labor_credit_component" in result_dict
        assert "non_labor_credit_component" in result_dict
        assert "total_credit" in result_dict
        assert "effective_rate" in result_dict
        assert "adjustments" in result_dict
        assert "warnings" in result_dict
        assert "labor_cap_applied" in result_dict

        # Verify values are strings (for Decimal serialization)
        assert isinstance(result_dict["adjusted_qualified_spend"], str)
        assert isinstance(result_dict["total_credit"], str)

        # Verify boolean
        assert isinstance(result_dict["labor_cap_applied"], bool)

    def test_result_to_dict_with_adjustments(self, enforcer):
        """Test serialization includes adjustments"""
        policy = create_mock_policy(
            policy_id="TEST-SERIALIZE-ADJ",
            headline_rate=Decimal("25.0"),
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000")
        )

        result_dict = result.to_dict()

        # Should have adjustments
        assert len(result_dict["adjustments"]) > 0

        # Verify adjustment structure
        adjustment = result_dict["adjustments"][0]
        assert "type" in adjustment
        assert "original" in adjustment
        assert "adjusted" in adjustment
        assert "reduction" in adjustment
        assert "description" in adjustment

    def test_result_to_dict_with_warnings(self, enforcer):
        """Test serialization includes warnings"""
        policy = create_mock_policy(
            policy_id="TEST-SERIALIZE-WARN",
            headline_rate=Decimal("30.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("5000000"),
            labor_spend=Decimal("7000000")  # Exceeds qualified
        )

        result_dict = result.to_dict()

        # Should have warnings
        assert len(result_dict["warnings"]) > 0
        assert isinstance(result_dict["warnings"], list)


# ============= Complex Scenario Tests =============

class TestComplexScenarios:
    """Tests for complex multi-feature scenarios"""

    def test_quebec_animation_full_scenario(self, enforcer):
        """Test complete Quebec animation scenario: labor cap + uplift + VFX rate"""
        # Quebec PSTC for animation: 36% base, 16% uplift, 60% labor cap
        policy = create_mock_policy(
            policy_id="CA-QC-PSTC-TEST",
            headline_rate=Decimal("36.0"),
            labor_max_percent=Decimal("60.0"),
            labor_uplift_rate=Decimal("16.0"),
            vfx_animation_rate=Decimal("45.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000"),  # Exceeds 60% cap
            vfx_labor_spend=Decimal("3000000")
        )

        # Labor capped at 60% = $6M
        assert result.adjusted_labor_spend == Decimal("6000000")
        assert result.labor_cap_applied is True

        # VFX labor (capped): min($3M, $6M) = $3M at 45% = $1,350,000
        # Regular labor: $3M at (36% + 16%) = 52% = $1,560,000
        # Non-labor: $4M at 36% = $1,440,000
        expected_vfx = Decimal("3000000") * Decimal("0.45")
        expected_regular = Decimal("3000000") * Decimal("0.52")
        expected_non_labor = Decimal("4000000") * Decimal("0.36")

        assert result.labor_credit_component == expected_vfx + expected_regular
        assert result.non_labor_credit_component == expected_non_labor

    def test_cptc_scenario(self, enforcer):
        """Test Canadian CPTC scenario: 25% rate, 60% labor cap"""
        policy = create_mock_policy(
            policy_id="CA-FEDERAL-CPTC-TEST",
            headline_rate=Decimal("25.0"),
            labor_max_percent=Decimal("60.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("7000000")  # 70%, exceeds 60%
        )

        # Labor capped at $6M
        assert result.adjusted_labor_spend == Decimal("6000000")

        # Credit: ($6M + $4M) * 25% = $2.5M
        expected_credit = Decimal("10000000") * Decimal("0.25")
        assert result.total_credit == expected_credit

        # Effective rate should still be 25%
        assert result.effective_rate == Decimal("25.0")

    def test_mixed_rates_comprehensive(self, enforcer):
        """Test comprehensive scenario with all features"""
        policy = create_mock_policy(
            policy_id="TEST-COMPREHENSIVE",
            headline_rate=Decimal("30.0"),
            labor_specific_rate=Decimal("25.0"),
            labor_uplift_rate=Decimal("5.0"),
            labor_max_percent=Decimal("70.0"),
            vfx_animation_rate=Decimal("35.0")
        )

        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("20000000"),
            labor_spend=Decimal("16000000"),  # 80%, exceeds 70%
            vfx_labor_spend=Decimal("6000000")
        )

        # Labor capped at 70% = $14M
        assert result.adjusted_labor_spend == Decimal("14000000")

        # VFX: min($6M, $14M) = $6M at 35%
        # Regular labor: $8M at (25% + 5%) = 30%
        # Non-labor: $6M at 30%
        expected_vfx = Decimal("6000000") * Decimal("0.35")
        expected_regular = Decimal("8000000") * Decimal("0.30")
        expected_non_labor = Decimal("6000000") * Decimal("0.30")

        assert result.labor_credit_component == expected_vfx + expected_regular
        assert result.non_labor_credit_component == expected_non_labor

        # Should have multiple adjustments
        assert len(result.adjustments) >= 3  # Cap, uplift, VFX rate
