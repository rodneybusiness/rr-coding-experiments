"""
Demonstration of S-curve Investment Modeling Integration with WaterfallExecutor

Shows how to use the InvestmentDrawdown class with WaterfallExecutor to track
investment timing alongside revenue waterfalls.
"""

from decimal import Decimal
from models.waterfall import WaterfallStructure, WaterfallNode, RecoupmentPriority
from engines.waterfall_executor import RevenueProjector, WaterfallExecutor
from engines.waterfall_executor.revenue_projector import InvestmentDrawdown


def demo_basic_integration():
    """Demo: Basic S-curve investment tracking with waterfall execution"""
    print("=" * 80)
    print("DEMO: S-Curve Investment Modeling with WaterfallExecutor")
    print("=" * 80)

    # 1. Create investment drawdown profile
    print("\n1. Creating S-curve investment drawdown profile...")
    investment = InvestmentDrawdown.create(
        total_investment=Decimal("10000000"),  # $10M budget
        draw_periods=18,  # 18 months of production
        steepness=8.0,
        midpoint=0.4  # Peak draws at 40% through timeline (production-heavy)
    )

    print(f"   Total Investment: ${investment.total_investment:,.2f}")
    print(f"   Draw Periods: {investment.draw_periods}")
    print(f"   Profile: Steepness={investment.steepness}, Midpoint={investment.midpoint}")

    # Show first few draws
    print("\n   First 6 months investment draws:")
    for i in range(6):
        draw = investment.quarterly_draws[i]
        cumulative = investment.cumulative_draws[i]
        pct = (cumulative / investment.total_investment) * 100
        print(f"      Month {i+1}: ${draw:>12,.2f} (Cumulative: ${cumulative:>12,.2f}, {pct:>5.1f}%)")

    # 2. Create waterfall structure
    print("\n2. Creating waterfall structure...")
    waterfall = WaterfallStructure(
        waterfall_name="Film Production Waterfall",
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
                amount=Decimal("5000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.NET_PROFITS,
                payee="Producer",
                amount=None,
                percentage=Decimal("20.0")
            ),
            WaterfallNode(
                priority=RecoupmentPriority.NET_PROFITS,
                payee="Equity Investors",
                amount=None,
                percentage=Decimal("80.0")
            ),
        ]
    )
    print(f"   Waterfall: {waterfall.waterfall_name}")
    print(f"   Nodes: {len(waterfall.nodes)}")

    # 3. Create revenue projection
    print("\n3. Creating revenue projection...")
    projector = RevenueProjector()
    projection = projector.project(
        total_ultimate_revenue=Decimal("40000000"),
        theatrical_box_office=Decimal("18000000"),
        release_strategy="wide_theatrical",
        project_name="Animated Feature"
    )
    print(f"   Project: {projection.project_name}")
    print(f"   Total Revenue: ${Decimal(projection.metadata['total_ultimate_revenue']):,.2f}")
    print(f"   Projection Quarters: {projection.total_quarters}")

    # 4. Execute waterfall WITHOUT investment tracking (baseline)
    print("\n4. Executing waterfall WITHOUT investment tracking (baseline)...")
    executor = WaterfallExecutor(waterfall)
    result_without_investment = executor.execute_over_time(projection)

    print(f"   Total Receipts: ${result_without_investment.total_receipts:,.2f}")
    print(f"   Total Fees: ${result_without_investment.total_fees:,.2f}")
    print(f"   Quarters Executed: {len(result_without_investment.quarterly_executions)}")
    print(f"   Investment Tracking: {'Enabled' if result_without_investment.investment_drawdown else 'Disabled'}")

    # 5. Execute waterfall WITH investment tracking
    print("\n5. Executing waterfall WITH investment tracking (S-curve)...")
    result_with_investment = executor.execute_over_time(
        projection,
        investment_drawdown_profile=investment
    )

    print(f"   Total Receipts: ${result_with_investment.total_receipts:,.2f}")
    print(f"   Total Fees: ${result_with_investment.total_fees:,.2f}")
    print(f"   Total Investment Drawn: ${result_with_investment.total_investment_drawn:,.2f}")
    print(f"   Quarters Executed: {len(result_with_investment.quarterly_executions)}")
    print(f"   Investment Tracking: {'Enabled' if result_with_investment.investment_drawdown else 'Disabled'}")

    # 6. Show quarterly detail with investment tracking
    print("\n6. Sample quarterly detail (first 6 quarters with investment data):")
    print(f"   {'Q':>3} {'Revenue':>12} {'Fees':>12} {'Pool':>12} {'Inv Draw':>12} {'Cum Inv':>12}")
    print("   " + "-" * 72)

    for qe in result_with_investment.quarterly_executions[:6]:
        inv_draw = qe.investment_drawn if qe.investment_drawn else Decimal("0")
        cum_inv = qe.cumulative_investment_drawn if qe.cumulative_investment_drawn else Decimal("0")
        print(f"   {qe.quarter:>3} ${qe.gross_receipts:>11,.0f} "
              f"${qe.distribution_fees + qe.pa_expenses:>11,.0f} "
              f"${qe.remaining_pool:>11,.0f} "
              f"${inv_draw:>11,.0f} "
              f"${cum_inv:>11,.0f}")

    # 7. Verify backward compatibility
    print("\n7. Backward Compatibility Check:")
    print(f"   ✓ Waterfall execution works WITHOUT investment profile")
    print(f"   ✓ Waterfall execution works WITH investment profile")
    print(f"   ✓ Revenue totals match in both cases: {result_without_investment.total_receipts == result_with_investment.total_receipts}")
    print(f"   ✓ Stakeholder payouts match in both cases: {result_without_investment.total_paid_by_payee == result_with_investment.total_paid_by_payee}")

    # 8. Show serialization with investment data
    print("\n8. Serialization Test (to_dict):")
    result_dict = result_with_investment.to_dict()
    has_investment_data = "investment_drawdown" in result_dict
    has_total_drawn = "total_investment_drawn" in result_dict
    print(f"   ✓ Investment drawdown in output: {has_investment_data}")
    print(f"   ✓ Total investment drawn in output: {has_total_drawn}")

    if has_investment_data:
        inv_dict = result_dict["investment_drawdown"]
        print(f"   ✓ Investment profile serialized with {len(inv_dict['quarterly_draws'])} periods")

    print("\n" + "=" * 80)
    print("DEMO COMPLETE: S-Curve investment modeling successfully integrated!")
    print("=" * 80)

    return result_with_investment


def demo_s_curve_profiles():
    """Demo: Different S-curve profiles for different production patterns"""
    print("\n" + "=" * 80)
    print("DEMO: Different S-Curve Investment Profiles")
    print("=" * 80)

    profiles = [
        ("Standard Production", 8.0, 0.4),
        ("Front-loaded (Animation)", 10.0, 0.3),
        ("Back-loaded (VFX-heavy)", 10.0, 0.7),
        ("Even Distribution", 2.0, 0.5)
    ]

    for name, steepness, midpoint in profiles:
        print(f"\n{name}:")
        print(f"  Steepness: {steepness}, Midpoint: {midpoint}")

        drawdown = InvestmentDrawdown.create(
            total_investment=Decimal("10000000"),
            draw_periods=12,
            steepness=steepness,
            midpoint=midpoint
        )

        # Show distribution pattern
        first_half = sum(drawdown.quarterly_draws[:6])
        second_half = sum(drawdown.quarterly_draws[6:])
        first_half_pct = (first_half / drawdown.total_investment) * 100

        print(f"  First 6 months: ${first_half:>12,.2f} ({first_half_pct:>5.1f}%)")
        print(f"  Last 6 months:  ${second_half:>12,.2f} ({100-first_half_pct:>5.1f}%)")

        # Find peak draw month
        peak_idx = drawdown.quarterly_draws.index(max(drawdown.quarterly_draws))
        print(f"  Peak draw in month: {peak_idx + 1}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Run basic integration demo
    result = demo_basic_integration()

    # Run S-curve profiles demo
    demo_s_curve_profiles()

    print("\n✓ All demonstrations completed successfully!")
