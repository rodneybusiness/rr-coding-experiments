"""
Unit Tests for IncentiveCalculator

Tests covering single jurisdiction calculations, multi-jurisdiction scenarios,
labor cap integration, different policy types, and validation logic.
"""

import pytest
from decimal import Decimal
from pathlib import Path

from engines.incentive_calculator import (
    IncentiveCalculator,
    JurisdictionSpend,
    IncentiveResult,
    MultiJurisdictionResult,
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
    """Create PolicyRegistry with loaded policies"""
    return PolicyRegistry(loader)


@pytest.fixture
def calculator(registry):
    """Create IncentiveCalculator"""
    return IncentiveCalculator(registry)


@pytest.fixture
def sample_jurisdiction_spend():
    """Create sample JurisdictionSpend for testing"""
    return JurisdictionSpend(
        jurisdiction="Test Jurisdiction",
        policy_ids=["TEST-POLICY"],
        qualified_spend=Decimal("5000000"),
        total_spend=Decimal("6000000"),
        labor_spend=Decimal("3000000"),
        goods_services_spend=Decimal("1500000"),
        post_production_spend=Decimal("400000"),
        vfx_animation_spend=Decimal("100000")
    )


class TestJurisdictionSpend:
    """Test JurisdictionSpend dataclass"""

    def test_jurisdiction_spend_initialization(self):
        """Test basic initialization"""
        js = JurisdictionSpend(
            jurisdiction="Canada",
            policy_ids=["CA-FEDERAL-CPTC-2025"],
            qualified_spend=Decimal("10000000"),
            total_spend=Decimal("12000000")
        )

        assert js.jurisdiction == "Canada"
        assert js.qualified_spend == Decimal("10000000")
        assert js.total_spend == Decimal("12000000")
        assert js.labor_spend == Decimal("0")

    def test_jurisdiction_spend_auto_conversion_to_decimal(self):
        """Test automatic conversion of numbers to Decimal"""
        js = JurisdictionSpend(
            jurisdiction="Canada",
            policy_ids=["CA-FEDERAL-CPTC-2025"],
            qualified_spend=10000000,  # int
            total_spend=12000000.0,  # float
            labor_spend="8000000"  # string
        )

        assert isinstance(js.qualified_spend, Decimal)
        assert isinstance(js.total_spend, Decimal)
        assert isinstance(js.labor_spend, Decimal)

    def test_jurisdiction_spend_validation_qualified_exceeds_total(self):
        """Test validation fails when qualified > total"""
        with pytest.raises(ValueError, match="cannot exceed total spend"):
            JurisdictionSpend(
                jurisdiction="Canada",
                policy_ids=["CA-FEDERAL-CPTC-2025"],
                qualified_spend=Decimal("15000000"),
                total_spend=Decimal("10000000")  # Less than qualified!
            )


class TestSingleJurisdictionCalculation:
    """Test single jurisdiction incentive calculations"""

    def test_calculate_uk_avec_direct_cash(self, calculator):
        """Test UK AVEC calculation with direct cash monetization"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000"),
            labor_spend=Decimal("3000000"),
            goods_services_spend=Decimal("1500000"),
            post_production_spend=Decimal("400000"),
            vfx_animation_spend=Decimal("100000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="UK-AVEC-2025",
            jurisdiction_spend=uk_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # UK AVEC is 39%
        expected_credit = Decimal("5000000") * Decimal("0.39")
        assert result.gross_credit == expected_credit
        assert result.net_cash_benefit == expected_credit  # No discount for direct
        assert result.effective_rate == Decimal("39.0")
        assert result.policy_id == "UK-AVEC-2025"
        assert result.jurisdiction == "United Kingdom"

    def test_calculate_with_transfer_discount(self, calculator):
        """Test calculation with transfer discount applied"""
        georgia_spend = JurisdictionSpend(
            jurisdiction="United States",
            policy_ids=["US-GA-GEFA-2025"],
            qualified_spend=Decimal("8000000"),
            total_spend=Decimal("8000000"),
            labor_spend=Decimal("6000000"),
            goods_services_spend=Decimal("1500000"),
            post_production_spend=Decimal("400000"),
            vfx_animation_spend=Decimal("100000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="US-GA-GEFA-2025",
            jurisdiction_spend=georgia_spend,
            monetization_method=MonetizationMethod.TRANSFER_TO_INVESTOR,
            transfer_discount=Decimal("20.0")  # 20% discount
        )

        # Verify discount is applied
        assert result.transfer_discount == Decimal("20.0")
        assert result.discount_amount > Decimal("0")

        # Net benefit should be less than gross credit due to discount
        assert result.net_cash_benefit < result.gross_credit

        # Verify discount amount is 20% of gross credit
        expected_discount = result.gross_credit * Decimal("0.20")
        assert result.discount_amount == expected_discount

    def test_calculate_georgia_with_uplift(self, calculator):
        """Test Georgia calculation"""
        georgia_spend = JurisdictionSpend(
            jurisdiction="United States",
            policy_ids=["US-GA-GEFA-2025"],
            qualified_spend=Decimal("10000000"),
            total_spend=Decimal("10000000"),
            labor_spend=Decimal("7000000"),
            goods_services_spend=Decimal("2000000"),
            post_production_spend=Decimal("800000"),
            vfx_animation_spend=Decimal("200000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="US-GA-GEFA-2025",
            jurisdiction_spend=georgia_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Georgia has labor cap - verify result is calculated
        assert result.gross_credit > Decimal("0")
        assert result.policy_name == "Georgia Film, Music & Digital Entertainment Tax Credit"
        assert result.jurisdiction == "United States - Georgia"

    def test_calculate_ireland_sceal(self, calculator):
        """Test Ireland Section 481 calculation"""
        ireland_spend = JurisdictionSpend(
            jurisdiction="Ireland",
            policy_ids=["IE-S481-SCEAL-2025"],
            qualified_spend=Decimal("7500000"),
            total_spend=Decimal("7500000"),
            labor_spend=Decimal("5000000"),
            goods_services_spend=Decimal("2000000"),
            post_production_spend=Decimal("400000"),
            vfx_animation_spend=Decimal("100000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="IE-S481-SCEAL-2025",
            jurisdiction_spend=ireland_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Ireland SCEAL has a 32% rate
        assert result.gross_credit > Decimal("0")
        assert result.policy_name == "Section 481 Scéal Uplift - Enhanced Animation Feature Rate"
        assert result.jurisdiction == "Ireland"

    def test_policy_not_found_raises_error(self, calculator):
        """Test that invalid policy ID raises ValueError"""
        spend = JurisdictionSpend(
            jurisdiction="Test",
            policy_ids=["INVALID-POLICY"],
            qualified_spend=Decimal("1000000"),
            total_spend=Decimal("1000000")
        )

        with pytest.raises(ValueError, match="Policy not found"):
            calculator.calculate_single_jurisdiction(
                policy_id="INVALID-POLICY",
                jurisdiction_spend=spend,
                monetization_method=MonetizationMethod.DIRECT_CASH
            )

    def test_unsupported_monetization_method_raises_error(self, calculator):
        """Test that unsupported monetization method raises ValueError"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000"),
            labor_spend=Decimal("3000000")
        )

        # Check if transfer is not supported, then test
        policy = calculator.registry.get_by_id("UK-AVEC-2025")
        if MonetizationMethod.TRANSFER_TO_INVESTOR not in policy.monetization_methods:
            with pytest.raises(ValueError, match="not supported"):
                calculator.calculate_single_jurisdiction(
                    policy_id="UK-AVEC-2025",
                    jurisdiction_spend=uk_spend,
                    monetization_method=MonetizationMethod.TRANSFER_TO_INVESTOR
                )


class TestLaborCapIntegration:
    """Test labor cap enforcement integration"""

    def test_quebec_labor_cap_enforcement(self, calculator):
        """Test Quebec PSTC labor cap enforcement"""
        quebec_spend = JurisdictionSpend(
            jurisdiction="Canada-Quebec",
            policy_ids=["CA-QC-PSTC-2025"],
            qualified_spend=Decimal("10000000"),
            total_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000"),
            goods_services_spend=Decimal("1500000"),
            post_production_spend=Decimal("400000"),
            vfx_animation_spend=Decimal("100000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="CA-QC-PSTC-2025",
            jurisdiction_spend=quebec_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Quebec has labor-specific rates (36% labor, 20% non-labor)
        # Should calculate correctly
        assert result.gross_credit > Decimal("0")
        assert "labor_enforcement" in result.metadata

    def test_canada_federal_labor_cap(self, calculator):
        """Test Canada Federal CPTC with labor cap and per-project cap"""
        canada_spend = JurisdictionSpend(
            jurisdiction="Canada",
            policy_ids=["CA-FEDERAL-CPTC-2025"],
            qualified_spend=Decimal("12000000"),
            total_spend=Decimal("12000000"),
            labor_spend=Decimal("10000000"),
            goods_services_spend=Decimal("1500000"),
            post_production_spend=Decimal("400000"),
            vfx_animation_spend=Decimal("100000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="CA-FEDERAL-CPTC-2025",
            jurisdiction_spend=canada_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Federal CPTC has 15% of budget cap
        # Should be capped at 15% of $12M = $1.8M
        expected_cap = Decimal("12000000") * Decimal("0.15")
        assert result.gross_credit <= expected_cap


class TestMultiJurisdictionCalculation:
    """Test multi-jurisdiction calculations"""

    def test_multi_jurisdiction_quebec_federal_provincial(self, calculator):
        """Test Quebec with both federal and provincial stacking"""
        quebec_spend = JurisdictionSpend(
            jurisdiction="Canada-Quebec",
            policy_ids=["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],
            qualified_spend=Decimal("10000000"),
            total_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000"),
            goods_services_spend=Decimal("1500000"),
            post_production_spend=Decimal("400000"),
            vfx_animation_spend=Decimal("100000")
        )

        result = calculator.calculate_multi_jurisdiction(
            total_budget=Decimal("10000000"),
            jurisdiction_spends=[quebec_spend],
            monetization_preferences={
                "CA-FEDERAL-CPTC-2025": MonetizationMethod.DIRECT_CASH,
                "CA-QC-PSTC-2025": MonetizationMethod.DIRECT_CASH
            }
        )

        # Should have 2 results
        assert len(result.jurisdiction_results) == 2

        # Should have stacking info
        assert len(result.stacking_applied) > 0

        # Total benefits should be sum of both
        federal_result = next(r for r in result.jurisdiction_results if "FEDERAL" in r.policy_id)
        quebec_result = next(r for r in result.jurisdiction_results if "QC" in r.policy_id)

        expected_total = federal_result.net_cash_benefit + quebec_result.net_cash_benefit
        assert result.total_net_benefits == expected_total

    def test_multi_jurisdiction_three_jurisdictions(self, calculator):
        """Test calculation across three jurisdictions"""
        quebec_spend = JurisdictionSpend(
            jurisdiction="Canada-Quebec",
            policy_ids=["CA-QC-PSTC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("5000000"),
            labor_spend=Decimal("4000000")
        )

        ireland_spend = JurisdictionSpend(
            jurisdiction="Ireland",
            policy_ids=["IE-S481-SCEAL-2025"],
            qualified_spend=Decimal("3000000"),
            total_spend=Decimal("3000000"),
            labor_spend=Decimal("2000000")
        )

        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("2000000"),
            total_spend=Decimal("2000000"),
            labor_spend=Decimal("1500000")
        )

        result = calculator.calculate_multi_jurisdiction(
            total_budget=Decimal("10000000"),
            jurisdiction_spends=[quebec_spend, ireland_spend, uk_spend],
            monetization_preferences={
                "CA-QC-PSTC-2025": MonetizationMethod.DIRECT_CASH,
                "IE-S481-SCEAL-2025": MonetizationMethod.DIRECT_CASH,
                "UK-AVEC-2025": MonetizationMethod.DIRECT_CASH
            }
        )

        # Should have 3 results (one per jurisdiction)
        assert len(result.jurisdiction_results) == 3

        # Total qualified should match sum
        assert result.total_qualified_spend == Decimal("10000000")

        # Should have net benefits
        assert result.total_net_benefits > Decimal("0")

    def test_multi_jurisdiction_australia_stacking(self, calculator):
        """Test Australia Producer + PDV stacking with 60% cap"""
        australia_spend = JurisdictionSpend(
            jurisdiction="Australia",
            policy_ids=["AU-PRODUCER-OFFSET-2025", "AU-PDV-OFFSET-2025"],
            qualified_spend=Decimal("15000000"),
            total_spend=Decimal("15000000"),
            labor_spend=Decimal("8000000"),
            goods_services_spend=Decimal("3000000"),
            post_production_spend=Decimal("2500000"),
            vfx_animation_spend=Decimal("1500000")
        )

        result = calculator.calculate_multi_jurisdiction(
            total_budget=Decimal("15000000"),
            jurisdiction_spends=[australia_spend],
            monetization_preferences={
                "AU-PRODUCER-OFFSET-2025": MonetizationMethod.DIRECT_CASH,
                "AU-PDV-OFFSET-2025": MonetizationMethod.DIRECT_CASH
            }
        )

        # Should have 2 results
        assert len(result.jurisdiction_results) == 2

        # Should have Australia stacking info
        assert any("Australia" in s for s in result.stacking_applied)

        # Both policies should have credits
        producer_result = next(r for r in result.jurisdiction_results if "PRODUCER" in r.policy_id)
        pdv_result = next(r for r in result.jurisdiction_results if "PDV" in r.policy_id)

        assert producer_result.gross_credit > Decimal("0")
        assert pdv_result.gross_credit > Decimal("0")

    def test_multi_jurisdiction_budget_mismatch_warning(self, calculator):
        """Test warning when allocated spend doesn't match budget"""
        spend = JurisdictionSpend(
            jurisdiction="Canada",
            policy_ids=["CA-QC-PSTC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("5000000"),
            labor_spend=Decimal("4000000")
        )

        result = calculator.calculate_multi_jurisdiction(
            total_budget=Decimal("10000000"),  # Budget is $10M
            jurisdiction_spends=[spend],  # But only allocated $5M
            monetization_preferences={
                "CA-QC-PSTC-2025": MonetizationMethod.DIRECT_CASH
            }
        )

        # Should have warning about budget mismatch
        assert any("does not match budget" in w for w in result.warnings)


class TestIncentiveResultSerialization:
    """Test IncentiveResult to_dict() method"""

    def test_incentive_result_to_dict(self, calculator):
        """Test IncentiveResult serialization"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000"),
            labor_spend=Decimal("3000000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="UK-AVEC-2025",
            jurisdiction_spend=uk_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        result_dict = result.to_dict()

        # Verify all fields are present
        assert "policy_id" in result_dict
        assert "jurisdiction" in result_dict
        assert "gross_credit" in result_dict
        assert "net_cash_benefit" in result_dict
        assert "effective_rate" in result_dict
        assert "monetization_method" in result_dict

        # Verify Decimal fields are converted to strings
        assert isinstance(result_dict["gross_credit"], str)
        assert isinstance(result_dict["net_cash_benefit"], str)


class TestMultiJurisdictionResultSerialization:
    """Test MultiJurisdictionResult to_dict() method"""

    def test_multi_jurisdiction_result_to_dict(self, calculator):
        """Test MultiJurisdictionResult serialization"""
        spend = JurisdictionSpend(
            jurisdiction="Canada-Quebec",
            policy_ids=["CA-QC-PSTC-2025"],
            qualified_spend=Decimal("10000000"),
            total_spend=Decimal("10000000"),
            labor_spend=Decimal("8000000")
        )

        result = calculator.calculate_multi_jurisdiction(
            total_budget=Decimal("10000000"),
            jurisdiction_spends=[spend],
            monetization_preferences={
                "CA-QC-PSTC-2025": MonetizationMethod.DIRECT_CASH
            }
        )

        result_dict = result.to_dict()

        # Verify all fields are present
        assert "total_budget" in result_dict
        assert "total_qualified_spend" in result_dict
        assert "jurisdiction_results" in result_dict
        assert "total_net_benefits" in result_dict
        assert "blended_effective_rate" in result_dict

        # Verify nested results are serialized
        assert isinstance(result_dict["jurisdiction_results"], list)
        assert len(result_dict["jurisdiction_results"]) > 0


class TestDifferentPolicyTypes:
    """Test calculations for different policy types"""

    def test_refundable_tax_credit(self, calculator):
        """Test refundable tax credit (UK AVEC)"""
        uk_spend = JurisdictionSpend(
            jurisdiction="United Kingdom",
            policy_ids=["UK-AVEC-2025"],
            qualified_spend=Decimal("5000000"),
            total_spend=Decimal("6000000"),
            labor_spend=Decimal("3000000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="UK-AVEC-2025",
            jurisdiction_spend=uk_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Refundable credit should have full value with direct cash
        assert result.net_cash_benefit == result.gross_credit

    def test_transferable_tax_credit(self, calculator):
        """Test transferable tax credit (Georgia)"""
        georgia_spend = JurisdictionSpend(
            jurisdiction="United States",
            policy_ids=["US-GA-GEFA-2025"],
            qualified_spend=Decimal("8000000"),
            total_spend=Decimal("8000000"),
            labor_spend=Decimal("6000000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="US-GA-GEFA-2025",
            jurisdiction_spend=georgia_spend,
            monetization_method=MonetizationMethod.TRANSFER_TO_INVESTOR,
            transfer_discount=Decimal("20.0")
        )

        # Transferable credit should have discount applied
        assert result.discount_amount > Decimal("0")
        assert result.net_cash_benefit < result.gross_credit

    def test_cash_rebate(self, calculator):
        """Test cash rebate program (New Zealand)"""
        nz_spend = JurisdictionSpend(
            jurisdiction="New Zealand",
            policy_ids=["NZ-NZSPR-INTL-2025"],
            qualified_spend=Decimal("20000000"),
            total_spend=Decimal("20000000"),
            labor_spend=Decimal("15000000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="NZ-NZSPR-INTL-2025",
            jurisdiction_spend=nz_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Rebate provides direct cash (may have audit costs deducted)
        assert result.gross_credit > Decimal("0")
        assert result.net_cash_benefit > Decimal("0")
        assert result.monetization_method == MonetizationMethod.DIRECT_CASH

        # Net may be less than gross due to audit/admin costs
        assert result.net_cash_benefit <= result.gross_credit
