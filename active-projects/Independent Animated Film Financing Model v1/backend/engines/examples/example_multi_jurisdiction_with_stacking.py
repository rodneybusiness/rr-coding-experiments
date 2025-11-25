"""
Example: Multi-Jurisdiction Calculation with Stacking

Demonstrates complete workflow for "The Dragon's Quest" - a $30M animated feature
using Quebec (Federal + Provincial stacking), Ireland, and California incentives.

This example shows:
1. Policy loading and registry initialization
2. Multi-jurisdiction spend allocation
3. Policy stacking (Canada Federal + Quebec)
4. Comprehensive incentive calculation
5. Cash flow projection
6. Monetization comparison
"""

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


def main():
    """Run complete multi-jurisdiction example"""

    print("=" * 80)
    print("THE DRAGON'S QUEST - Multi-Jurisdiction Incentive Analysis")
    print("=" * 80)
    print()

    # 1. Initialize Engine 1 components
    print("1. Initializing Engine 1 components...")
    base_path = Path(__file__).parent.parent.parent
    policies_dir = base_path / "data" / "policies"

    loader = PolicyLoader(policies_dir)
    registry = PolicyRegistry(loader)
    calculator = IncentiveCalculator(registry)
    projector = CashFlowProjector()
    comparator = MonetizationComparator(calculator)

    print(f"   ✓ Loaded {len(registry.get_all())} policies from {len(registry.get_jurisdictions())} jurisdictions")
    print()

    # 2. Define project parameters
    print("2. Project Parameters:")
    print(f"   Title: The Dragon's Quest")
    print(f"   Format: Theatrical animated feature")
    print(f"   Total Budget: $30,000,000")
    print(f"   Production Schedule: 18 months")
    print()

    # 3. Define jurisdiction allocations
    print("3. Jurisdiction Spend Allocation:")
    print()

    # Quebec: 55% of budget ($16.5M)
    quebec_spend = JurisdictionSpend(
        jurisdiction="Canada-Quebec",
        policy_ids=["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],  # Stacking
        qualified_spend=Decimal("16500000"),
        total_spend=Decimal("16500000"),
        labor_spend=Decimal("12000000"),
        goods_services_spend=Decimal("3000000"),
        post_production_spend=Decimal("1000000"),
        vfx_animation_spend=Decimal("500000")
    )
    print(f"   Quebec (55%): ${quebec_spend.total_spend:,.0f}")
    print(f"      Labor: ${quebec_spend.labor_spend:,.0f}")
    print(f"      Policies: Federal CPTC + Quebec PSTC (stacked)")
    print()

    # Ireland: 25% of budget ($7.5M)
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
    print(f"   Ireland (25%): ${ireland_spend.total_spend:,.0f}")
    print(f"      Labor: ${ireland_spend.labor_spend:,.0f}")
    print(f"      Policies: Section 481 Scéal Uplift (40%)")
    print()

    # California: 20% of budget ($6M)
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
    print(f"   California (20%): ${california_spend.total_spend:,.0f}")
    print(f"      Labor: ${california_spend.labor_spend:,.0f}")
    print(f"      Policies: California Film Tax Credit 4.0 (35%)")
    print()

    # 4. Calculate incentives
    print("4. Calculating Multi-Jurisdiction Incentives...")
    print()

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

    # 5. Display results by jurisdiction
    print("5. Incentive Results:")
    print()

    for jr in result.jurisdiction_results:
        print(f"   {jr.jurisdiction} - {jr.policy_name}")
        print(f"      Policy ID: {jr.policy_id}")
        print(f"      Qualified Spend: ${jr.qualified_spend:,.0f}")
        print(f"      Gross Credit: ${jr.gross_credit:,.0f}")
        print(f"      Net Cash Benefit: ${jr.net_cash_benefit:,.0f}")
        print(f"      Effective Rate: {jr.effective_rate}%")
        print(f"      Timing: {jr.timing_months} months from completion")
        if jr.warnings:
            print(f"      ⚠ Warnings: {', '.join(jr.warnings[:2])}")
        print()

    # 6. Display aggregate results
    print("6. Aggregate Results:")
    print(f"   Total Budget: ${result.total_budget:,.0f}")
    print(f"   Total Qualified Spend: ${result.total_qualified_spend:,.0f}")
    print(f"   Total Gross Credits: ${result.total_gross_credits:,.0f}")
    print(f"   Total Net Benefits: ${result.total_net_benefits:,.0f}")
    print(f"   Blended Effective Rate: {result.blended_effective_rate:.2f}%")
    print()

    if result.stacking_applied:
        print(f"   ✓ Stacking Applied:")
        for stack in result.stacking_applied:
            print(f"      - {stack}")
        print()

    # 7. Project cash flow
    print("7. Cash Flow Projection:")
    print()

    projection = projector.project(
        production_budget=Decimal("30000000"),
        production_schedule_months=18,
        jurisdiction_spends=[quebec_spend, ireland_spend, california_spend],
        incentive_results=result.jurisdiction_results
    )

    print(f"   Production Period: {projection.production_period_months} months")
    print(f"   Peak Funding Required: ${projection.peak_funding_required:,.0f}")
    print(f"   Total Incentive Receipts: ${projection.total_incentive_receipts:,.0f}")
    print(f"   Final Balance: ${projection.final_balance:,.0f}")
    print()

    # Show key events
    print("   Key Cash Flow Events:")
    print()
    print(f"      {'Month':<8} {'Type':<20} {'Amount':<20} {'Cumulative':<20}")
    print("      " + "-" * 68)

    # Show first 3 months of production
    for event in projection.events[:3]:
        print(f"      {event.month:<8} {event.event_type:<20} "
              f"${event.amount:>15,.0f}   ${event.cumulative_balance:>15,.0f}")

    print("      ...")

    # Show incentive receipt events
    incentive_events = [e for e in projection.events if e.event_type == "incentive_receipt"]
    for event in incentive_events:
        print(f"      {event.month:<8} {event.event_type:<20} "
              f"${event.amount:>15,.0f}   ${event.cumulative_balance:>15,.0f}")
    print()

    # 8. Monthly view summary
    print("8. Monthly Cash Flow Summary (Selected Months):")
    print()
    monthly_view = projector.monthly_view_dict(projection)

    print(f"      {'Month':<8} {'Spend':<18} {'Receipts':<18} {'Net Flow':<18} {'Cumulative':<18}")
    print("      " + "-" * 80)

    # Show months 0, 5, 10, 17 (production), then months with incentive receipts
    sample_months = [0, 5, 10, 17]
    for month in sample_months:
        if month in monthly_view:
            view = monthly_view[month]
            print(f"      {month:<8} "
                  f"${view['spend']:>14,.0f}   "
                  f"${view['incentive_receipts']:>14,.0f}   "
                  f"${view['net_cash_flow']:>14,.0f}   "
                  f"${view['cumulative_balance']:>14,.0f}")

    print("      ...")

    # Show months with incentive receipts
    incentive_months = sorted([e.month for e in incentive_events])
    for month in incentive_months:
        if month in monthly_view:
            view = monthly_view[month]
            print(f"      {month:<8} "
                  f"${view['spend']:>14,.0f}   "
                  f"${view['incentive_receipts']:>14,.0f}   "
                  f"${view['net_cash_flow']:>14,.0f}   "
                  f"${view['cumulative_balance']:>14,.0f}")
    print()

    # 9. Monetization comparison for Quebec
    print("9. Monetization Strategy Analysis (Quebec PSTC):")
    print()

    quebec_comparison = comparator.compare_strategies(
        policy_id="CA-QC-PSTC-2025",
        qualified_spend=quebec_spend.qualified_spend,
        jurisdiction_spend=quebec_spend,
        strategies=[
            MonetizationMethod.DIRECT_CASH,
            MonetizationMethod.TAX_CREDIT_LOAN
        ],
        loan_fee=Decimal("10.0")
    )

    for scenario in quebec_comparison.scenarios:
        print(f"   {scenario.strategy_name}:")
        print(f"      Gross Credit: ${scenario.gross_credit:,.0f}")
        print(f"      Discount/Fee: {scenario.discount_rate}% (${scenario.discount_amount:,.0f})")
        print(f"      Net Proceeds: ${scenario.net_proceeds:,.0f}")
        print(f"      Effective Rate: {scenario.effective_rate}%")
        print(f"      Timing: Month {scenario.timing_months}")
        print(f"      Notes: {scenario.notes[:100]}...")
        print()

    print(f"   ✓ Recommended: {quebec_comparison.recommended_strategy}")
    print(f"      {quebec_comparison.recommendation_reason}")
    print()

    # 10. Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"✓ Total Production Budget: ${result.total_budget:,.0f}")
    print(f"✓ Total Incentive Benefit: ${result.total_net_benefits:,.0f} "
          f"({result.blended_effective_rate:.2f}% effective)")
    print(f"✓ Net Production Cost: ${result.total_budget - result.total_net_benefits:,.0f}")
    print()
    print(f"✓ Incentive Breakdown:")
    for jr in result.jurisdiction_results:
        pct = (jr.net_cash_benefit / result.total_net_benefits * 100)
        print(f"    - {jr.jurisdiction}: ${jr.net_cash_benefit:,.0f} ({pct:.1f}%)")
    print()
    print(f"✓ Peak Funding Requirement: ${projection.peak_funding_required:,.0f}")
    print(f"✓ Incentive Receipt Timeline: {int(result.total_timing_weighted_months)} months avg")
    print()
    print("✓ Stacking strategies successfully applied:")
    for stack in result.stacking_applied:
        print(f"    - {stack}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
