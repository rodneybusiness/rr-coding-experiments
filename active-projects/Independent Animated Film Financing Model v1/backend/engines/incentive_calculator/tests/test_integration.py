"""
Integration Tests for Engine 1

End-to-end tests covering complete workflows from policy loading through
calculation, cash flow projection, and monetization comparison.
"""

import pytest
from pathlib import Path
from decimal import Decimal

from engines.incentive_calculator import (
    PolicyLoader,
    PolicyRegistry,
    IncentiveCalculator,
    JurisdictionSpend,
    CashFlowProjector,
    MonetizationComparator,
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
def comparator(calculator):
    """Create MonetizationComparator"""
    return MonetizationComparator(calculator)


class TestCompleteWorkflows:
    """Test complete end-to-end workflows"""

    def test_uk_avec_single_jurisdiction(self, calculator):
        """Test complete UK AVEC calculation"""
        # £5M qualified spend
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

        # 39% of £5M = £1,950,000
        assert result.gross_credit == Decimal("5000000") * Decimal("0.39")
        assert result.net_cash_benefit == result.gross_credit  # No discount for direct cash
        assert result.effective_rate == Decimal("39.0")
        assert result.policy_name == "Audio-Visual Expenditure Credit (AVEC)"

        # Should have warning about cultural test
        assert any("cultural test" in w.lower() for w in result.warnings)

    def test_quebec_stacking_scenario(self, calculator):
        """Test Quebec Federal + Provincial stacking"""
        # $10M production, $8M labor in Quebec
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

        # Federal: 25% × $8M = $2M, capped at 15% of budget = $1.5M
        federal_result = next(r for r in result.jurisdiction_results if "FEDERAL" in r.policy_id)
        assert federal_result.gross_credit == Decimal("1500000")  # Capped

        # Quebec: Labor (36% × $8M = $2.88M) + Non-labor (20% × $2M = $0.40M) = $3.28M
        # Quebec PSTC: 20% base on all spend + 16% uplift on labor = 36% on labor, 20% on non-labor
        quebec_result = next(r for r in result.jurisdiction_results if "QC" in r.policy_id)
        expected_labor_credit = Decimal("8000000") * Decimal("0.36")  # $2.88M
        expected_nonlabor_credit = Decimal("2000000") * Decimal("0.20")  # $0.40M
        expected_quebec_credit = expected_labor_credit + expected_nonlabor_credit  # $3.28M
        assert quebec_result.gross_credit == expected_quebec_credit

        # Total net benefit should be sum of both
        expected_total = federal_result.net_cash_benefit + quebec_result.net_cash_benefit
        assert result.total_net_benefits == expected_total

        # Should indicate stacking was applied
        assert len(result.stacking_applied) > 0
        assert any("Quebec" in s for s in result.stacking_applied)

    def test_dragons_quest_multi_jurisdiction(self, calculator):
        """Test 'The Dragon's Quest' 3-jurisdiction scenario"""
        # Quebec: 55% of $30M budget
        quebec_spend = JurisdictionSpend(
            jurisdiction="Canada-Quebec",
            policy_ids=["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],
            qualified_spend=Decimal("16500000"),
            total_spend=Decimal("16500000"),
            labor_spend=Decimal("12000000"),
            goods_services_spend=Decimal("3000000"),
            post_production_spend=Decimal("1000000"),
            vfx_animation_spend=Decimal("500000")
        )

        # Ireland: 25% of budget
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

        # California: 20% of budget
        california_spend = JurisdictionSpend(
            jurisdiction="United States",
            policy_ids=["US-CA-FILMTAX-2025"],
            qualified_spend=Decimal("6000000"),
            total_spend=Decimal("6000000"),
            labor_spend=Decimal("4500000"),
            goods_services_spend=Decimal("1200000"),
            post_production_spend=Decimal("200000"),
            vfx_animation_spend=Decimal("100000")
        )

        result = calculator.calculate_multi_jurisdiction(
            total_budget=Decimal("30000000"),
            jurisdiction_spends=[quebec_spend, ireland_spend, california_spend],
            monetization_preferences={
                "CA-FEDERAL-CPTC-2025": MonetizationMethod.DIRECT_CASH,
                "CA-QC-PSTC-2025": MonetizationMethod.DIRECT_CASH,
                "IE-S481-SCEAL-2025": MonetizationMethod.DIRECT_CASH,
                "US-CA-FILMTAX-2025": MonetizationMethod.DIRECT_CASH
            }
        )

        # Should have 4 results (2 for Quebec, 1 for Ireland, 1 for California)
        assert len(result.jurisdiction_results) == 4

        # Verify each jurisdiction
        assert any("CA-FEDERAL" in r.policy_id for r in result.jurisdiction_results)
        assert any("CA-QC" in r.policy_id for r in result.jurisdiction_results)
        assert any("IE-S481-SCEAL" in r.policy_id for r in result.jurisdiction_results)
        assert any("US-CA" in r.policy_id for r in result.jurisdiction_results)

        # Total net benefits should be substantial (>$10M)
        assert result.total_net_benefits > Decimal("10000000")

        # Blended effective rate should be > 30%
        assert result.blended_effective_rate > Decimal("30.0")

    def test_australia_stacking_scenario(self, calculator):
        """Test Australia Producer Offset + PDV Offset stacking"""
        # $15M production with significant post/VFX
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

        # Producer Offset: 40% (theatrical)
        producer_result = next(r for r in result.jurisdiction_results if "PRODUCER" in r.policy_id)
        assert producer_result.gross_credit > Decimal("0")

        # PDV Offset: 30%
        pdv_result = next(r for r in result.jurisdiction_results if "PDV" in r.policy_id)
        assert pdv_result.gross_credit > Decimal("0")

        # Should indicate stacking was applied with 60% cap check
        assert any("Australia" in s for s in result.stacking_applied)

    def test_cash_flow_projection_single_jurisdiction(self, calculator, projector):
        """Test cash flow projection for single jurisdiction"""
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

        # Project cash flow
        projection = projector.project(
            production_budget=Decimal("6000000"),
            production_schedule_months=18,
            jurisdiction_spends=[uk_spend],
            incentive_results=[result]
        )

        # Should have events
        assert len(projection.events) > 0

        # Should have production spend events
        spend_events = [e for e in projection.events if e.event_type == "production_spend"]
        assert len(spend_events) == 18  # 18 months

        # Should have incentive receipt event
        incentive_events = [e for e in projection.events if e.event_type == "incentive_receipt"]
        assert len(incentive_events) == 1

        # Peak funding should be negative (need to fund production)
        assert projection.peak_funding_required > Decimal("0")

        # Total incentive receipts should match calculation
        assert projection.total_incentive_receipts == result.net_cash_benefit

    def test_cash_flow_projection_multi_jurisdiction(self, calculator, projector):
        """Test cash flow projection for multi-jurisdiction"""
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

        projection = projector.project(
            production_budget=Decimal("10000000"),
            production_schedule_months=18,
            jurisdiction_spends=[quebec_spend],
            incentive_results=[result]
        )

        # Get monthly view
        monthly_view = projector.monthly_view_dict(projection)

        # Should have entries for all months
        assert len(monthly_view) > 18  # Production + post-production period

        # First month should have spend
        assert monthly_view[0]["spend"] > Decimal("0")

        # Last months should have incentive receipts
        max_month = max(monthly_view.keys())
        total_receipts = sum(v["incentive_receipts"] for v in monthly_view.values())
        assert total_receipts == result.net_cash_benefit

    def test_monetization_comparison_georgia(self, calculator, comparator):
        """Test monetization comparison for Georgia transferable credit"""
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

        comparison = comparator.compare_strategies(
            policy_id="US-GA-GEFA-2025",
            qualified_spend=georgia_spend.qualified_spend,
            jurisdiction_spend=georgia_spend,
            strategies=[
                MonetizationMethod.DIRECT_CASH,
                MonetizationMethod.TRANSFER_TO_INVESTOR,
                MonetizationMethod.TAX_CREDIT_LOAN
            ]
        )

        # Should have scenarios
        assert len(comparison.scenarios) >= 2

        # Should have recommendation
        assert comparison.recommended_strategy
        assert comparison.recommendation_reason

        # Verify scenarios have different net proceeds
        net_proceeds = [s.net_proceeds for s in comparison.scenarios]
        assert len(set(net_proceeds)) > 1  # Should have different values

        # Direct cash should have highest net proceeds
        direct_scenario = next(
            s for s in comparison.scenarios
            if s.monetization_method == MonetizationMethod.DIRECT_CASH
        )
        assert direct_scenario.net_proceeds == max(net_proceeds)

    def test_loan_vs_direct_analysis(self, calculator, comparator):
        """Test detailed loan vs. direct analysis"""
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

        analysis = comparator.loan_vs_direct_analysis(
            policy_id="US-GA-GEFA-2025",
            qualified_spend=georgia_spend.qualified_spend,
            jurisdiction_spend=georgia_spend,
            loan_fee_rate=Decimal("10.0"),
            production_schedule_months=18
        )

        # Should have both scenarios
        assert "loan_scenario" in analysis
        assert "direct_scenario" in analysis
        assert "difference" in analysis

        # Loan should be earlier but lower proceeds
        loan_month = analysis["loan_scenario"]["month_received"]
        direct_month = analysis["direct_scenario"]["month_received"]
        assert loan_month < direct_month

        loan_benefit = Decimal(analysis["loan_scenario"]["net_benefit"])
        direct_benefit = Decimal(analysis["direct_scenario"]["net_benefit"])
        assert direct_benefit > loan_benefit

        # Should have loan cost
        loan_cost = Decimal(analysis["difference"]["loan_cost"])
        assert loan_cost > Decimal("0")

    def test_policy_registry_search(self, registry):
        """Test policy registry search functionality"""
        # Search for refundable credits
        refundable = registry.search(
            incentive_type="refundable_tax_credit"
        )
        assert len(refundable) > 0

        # Search for high-rate incentives (>35%)
        high_rate = registry.search(
            min_rate=Decimal("35.0")
        )
        assert len(high_rate) > 0
        assert all(p.headline_rate >= Decimal("35.0") for p in high_rate)

        # Search for policies without cultural test
        no_cultural_test = registry.search(
            requires_cultural_test=False
        )
        assert len(no_cultural_test) > 0
        assert all(not p.cultural_test.requires_cultural_test for p in no_cultural_test)

    def test_policy_registry_stackable(self, registry):
        """Test stackable policy identification"""
        stackable = registry.get_stackable_policies()

        # Should have Canada and Australia
        assert any("Canada" in k for k in stackable.keys())
        assert any("Australia" in k for k in stackable.keys())

        # Canada-Quebec should have 2 policies
        if "Canada-Quebec" in stackable:
            assert len(stackable["Canada-Quebec"]) == 2

        # Australia should have 2 policies
        if "Australia" in stackable:
            assert len(stackable["Australia"]) == 2

    def test_policy_registry_summary(self, registry):
        """Test registry summary statistics"""
        summary = registry.get_summary()

        assert summary["total_policies"] >= 15
        assert summary["jurisdictions"] >= 13
        assert len(summary["by_type"]) > 0
        assert len(summary["by_jurisdiction"]) > 0
        assert summary["average_rate"] > Decimal("0")
        assert summary["rate_range"][0] < summary["rate_range"][1]

    def test_calculator_validation_minimum_spend(self, calculator):
        """Test calculator validates minimum spend requirements"""
        # New Zealand has high minimum ($15M NZD)
        nz_spend = JurisdictionSpend(
            jurisdiction="New Zealand",
            policy_ids=["NZ-NZSPR-INTL-2025"],
            qualified_spend=Decimal("1000000"),  # Below minimum
            total_spend=Decimal("1000000"),
            labor_spend=Decimal("800000"),
            goods_services_spend=Decimal("150000"),
            post_production_spend=Decimal("40000"),
            vfx_animation_spend=Decimal("10000")
        )

        result = calculator.calculate_single_jurisdiction(
            policy_id="NZ-NZSPR-INTL-2025",
            jurisdiction_spend=nz_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Should have warning about minimum spend
        assert any("minimum" in w.lower() for w in result.warnings)

    def test_calculator_validation_unsupported_monetization(self, calculator):
        """Test calculator rejects unsupported monetization methods"""
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

        # UK AVEC doesn't support transfer (it's refundable, not transferable)
        # Actually, let's check what methods it supports
        policy = calculator.registry.get_by_id("UK-AVEC-2025")

        # Try an unsupported method (if transfer isn't supported)
        if MonetizationMethod.TRANSFER_TO_INVESTOR not in policy.monetization_methods:
            with pytest.raises(ValueError, match="not supported"):
                calculator.calculate_single_jurisdiction(
                    policy_id="UK-AVEC-2025",
                    jurisdiction_spend=uk_spend,
                    monetization_method=MonetizationMethod.TRANSFER_TO_INVESTOR
                )

    def test_end_to_end_complete_workflow(self, loader, projector):
        """Test complete end-to-end workflow from loading to cash flow"""
        # 1. Load policies
        registry = PolicyRegistry(loader)
        assert len(registry.get_all()) >= 15

        # 2. Initialize calculator
        calculator = IncentiveCalculator(registry)

        # 3. Define project
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

        # 4. Calculate incentives
        result = calculator.calculate_multi_jurisdiction(
            total_budget=Decimal("10000000"),
            jurisdiction_spends=[quebec_spend],
            monetization_preferences={
                "CA-FEDERAL-CPTC-2025": MonetizationMethod.DIRECT_CASH,
                "CA-QC-PSTC-2025": MonetizationMethod.DIRECT_CASH
            }
        )

        assert result.total_net_benefits > Decimal("0")

        # 5. Project cash flow
        projection = projector.project(
            production_budget=Decimal("10000000"),
            production_schedule_months=18,
            jurisdiction_spends=[quebec_spend],
            incentive_results=result.jurisdiction_results
        )

        assert projection.peak_funding_required > Decimal("0")
        assert projection.total_incentive_receipts == result.total_net_benefits

        # 6. Compare monetization
        comparator = MonetizationComparator(calculator)
        comparison = comparator.compare_strategies(
            policy_id="CA-QC-PSTC-2025",
            qualified_spend=quebec_spend.qualified_spend,
            jurisdiction_spend=quebec_spend
        )

        assert len(comparison.scenarios) > 0
        assert comparison.recommended_strategy

        # Success! Complete workflow executed
