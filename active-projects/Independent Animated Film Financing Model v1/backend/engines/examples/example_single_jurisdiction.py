"""
Example: Single Jurisdiction Calculation

Demonstrates basic workflow for calculating tax incentives for a single jurisdiction.
This example uses the UK Audio-Visual Expenditure Credit (AVEC) for a £5M production.
"""

from pathlib import Path
from decimal import Decimal

from backend.engines.incentive_calculator import (
    PolicyLoader,
    PolicyRegistry,
    IncentiveCalculator,
    JurisdictionSpend,
)
from backend.models.incentive_policy import MonetizationMethod


def main():
    """Run single jurisdiction example"""

    print("=" * 80)
    print("Single Jurisdiction Example: UK AVEC")
    print("=" * 80)
    print()

    # 1. Initialize
    print("1. Initializing Engine 1...")
    base_path = Path(__file__).parent.parent.parent
    policies_dir = base_path / "data" / "policies"

    loader = PolicyLoader(policies_dir)
    registry = PolicyRegistry(loader)
    calculator = IncentiveCalculator(registry)

    print(f"   ✓ Loaded {len(registry.get_all())} policies")
    print()

    # 2. Get policy details
    print("2. Policy Details:")
    uk_policy = registry.get_by_id("UK-AVEC-2025")

    print(f"   Program: {uk_policy.program_name}")
    print(f"   Jurisdiction: {uk_policy.jurisdiction}")
    print(f"   Type: {uk_policy.incentive_type.value}")
    print(f"   Headline Rate: {uk_policy.headline_rate}%")
    print(f"   Enhanced Rate: {uk_policy.enhanced_rate}% (animation)")
    print(f"   Minimum Spend: £{uk_policy.minimum_local_spend:,.0f}")
    print(f"   Cultural Test Required: {uk_policy.cultural_test.requires_cultural_test}")
    print(f"   Refundable: {uk_policy.incentive_type.value == 'refundable_tax_credit'}")
    print()

    # 3. Define project spend
    print("3. Project Spend Allocation:")
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

    print(f"   Total Budget: £{uk_spend.total_spend:,.0f}")
    print(f"   Qualified Spend: £{uk_spend.qualified_spend:,.0f}")
    print(f"   Breakdown:")
    print(f"      Labor: £{uk_spend.labor_spend:,.0f}")
    print(f"      Goods & Services: £{uk_spend.goods_services_spend:,.0f}")
    print(f"      Post-Production: £{uk_spend.post_production_spend:,.0f}")
    print(f"      VFX/Animation: £{uk_spend.vfx_animation_spend:,.0f}")
    print()

    # 4. Calculate incentive
    print("4. Calculating Incentive...")
    result = calculator.calculate_single_jurisdiction(
        policy_id="UK-AVEC-2025",
        jurisdiction_spend=uk_spend,
        monetization_method=MonetizationMethod.DIRECT_CASH
    )

    print(f"   ✓ Calculation complete")
    print()

    # 5. Display results
    print("5. Incentive Results:")
    print()
    print(f"   Qualified Spend: £{result.qualified_spend:,.0f}")
    print(f"   Gross Credit (39%): £{result.gross_credit:,.0f}")
    print()
    print(f"   Less: Transfer Discount: £{result.discount_amount:,.0f}")
    print(f"   Less: Tax Costs: £{result.tax_cost:,.0f}")
    print(f"   Less: Audit Cost: £{result.audit_cost:,.0f}")
    print(f"   Less: Application Fee: £{result.application_fee:,.0f}")
    print()
    print(f"   = Net Cash Benefit: £{result.net_cash_benefit:,.0f}")
    print(f"   = Effective Rate: {result.effective_rate}%")
    print()
    print(f"   Monetization Method: {result.monetization_method.value}")
    print(f"   Timing to Receipt: {result.timing_months} months from completion")
    print()

    # 6. Warnings
    if result.warnings:
        print("6. Important Notes:")
        for warning in result.warnings:
            print(f"   ⚠ {warning}")
        print()

    # 7. Calculate breakdown
    print("7. Financial Summary:")
    print()
    print(f"   Total Production Budget: £{uk_spend.total_spend:,.0f}")
    print(f"   Less: Net Incentive: £{result.net_cash_benefit:,.0f}")
    print(f"   ────────────────────────────────")
    print(f"   Net Cost to Producer: £{uk_spend.total_spend - result.net_cash_benefit:,.0f}")
    print()
    print(f"   Incentive reduces net cost by {(result.net_cash_benefit / uk_spend.total_spend * 100):.1f}%")
    print()

    # 8. Timing information
    print("8. Timeline:")
    print()
    print(f"   Month 0-18: Production")
    print(f"   Month 18-24: Audit & Documentation ({uk_policy.timing_months_audit_to_certification} months)")
    print(f"   Month 24-27: Certification to Cash ({uk_policy.timing_months_certification_to_cash} months)")
    print(f"   Month 27: Incentive Receipt (£{result.net_cash_benefit:,.0f})")
    print()

    # 9. Cultural test reminder
    print("9. Next Steps:")
    print()
    print("   ✓ Ensure production qualifies for BFI Cultural Test")
    print(f"      Minimum {uk_policy.cultural_test.minimum_points_required} points required")
    print(f"      out of {uk_policy.cultural_test.total_points_available} total points")
    print(f"      Details: {uk_policy.cultural_test.test_details_url}")
    print()
    print("   ✓ Engage UK-based production services company")
    print("   ✓ Maintain detailed expenditure records")
    print("   ✓ Budget for audit costs (£35,000-50,000)")
    print("   ✓ Plan cash flow for 27-month receipt timeline")
    print()

    print("=" * 80)


if __name__ == "__main__":
    main()
