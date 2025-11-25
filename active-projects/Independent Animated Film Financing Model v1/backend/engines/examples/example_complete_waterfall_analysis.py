"""
Example: Complete Waterfall Analysis with IRR/NPV

Demonstrates the full power of Engine 2: Waterfall Execution Engine
- Revenue projection with 2025-accurate distribution windows
- Time-series waterfall execution
- Stakeholder return analysis (IRR, NPV, cash-on-cash, payback)
- Monte Carlo simulation for risk quantification

This example uses "The Dragon's Quest" - a $30M animated feature film.
"""

from pathlib import Path
from decimal import Decimal

from models.waterfall import WaterfallStructure, WaterfallNode, RecoupmentPriority
from models.capital_stack import CapitalStack, CapitalComponent
from models.financial_instruments import Equity, SeniorDebt, GapDebt, PreSale

from engines.waterfall_executor import (
    RevenueProjector,
    WaterfallExecutor,
    StakeholderAnalyzer,
    MonteCarloSimulator,
    RevenueDistribution,
)


def main():
    """Run complete waterfall analysis"""

    print("=" * 90)
    print("THE DRAGON'S QUEST - Complete Waterfall Analysis with IRR/NPV")
    print("Engine 2: Waterfall Execution Engine - Demonstration")
    print("=" * 90)
    print()

    # ====================
    # 1. PROJECT PARAMETERS
    # ====================

    print("1. PROJECT PARAMETERS")
    print("-" * 90)
    print(f"   Title: The Dragon's Quest")
    print(f"   Format: Theatrical animated feature (CGI)")
    print(f"   Production Budget: $30,000,000")
    print(f"   Production Schedule: 18 months")
    print(f"   Target Market: Family/All Ages")
    print()

    # ====================
    # 2. CAPITAL STACK
    # ====================

    print("2. CAPITAL STACK")
    print("-" * 90)

    # Define financial instruments
    equity = Equity(
        amount=Decimal("9000000"),
        ownership_percentage=Decimal("100.0"),
        premium_percentage=Decimal("20.0"),  # 120% recoupment (20% premium)
        backend_participation_percentage=Decimal("50.0")
    )

    svod_presale = PreSale(
        amount=Decimal("6000000"),
        buyer="Global Streamer",
        territory="Worldwide SVOD",
        delivery_quarter=6  # 6 quarters (1.5 years) from start
    )

    senior_debt = SeniorDebt(
        amount=Decimal("10000000"),
        interest_rate=Decimal("8.0"),
        term_months=24,
        origination_fee_percentage=Decimal("2.0")
    )

    gap_debt = GapDebt(
        amount=Decimal("5000000"),
        interest_rate=Decimal("12.0"),
        term_months=24,
        gap_percentage=Decimal("40.0")
    )

    # Create capital stack
    capital_stack = CapitalStack(
        stack_name="Dragon's Quest Capital Stack",
        project_budget=Decimal("30000000"),
        components=[
            CapitalComponent(instrument=senior_debt, position=1),
            CapitalComponent(instrument=gap_debt, position=2),
            CapitalComponent(instrument=svod_presale, position=3),
            CapitalComponent(instrument=equity, position=4)
        ]
    )

    print(f"   Total Capital Raised: ${capital_stack.total_capital_raised():,.0f}")
    print(f"   Total Debt: ${capital_stack.total_debt():,.0f}")
    print(f"   Total Equity: ${capital_stack.total_equity():,.0f}")
    print(f"   Debt-to-Equity Ratio: {capital_stack.debt_to_equity_ratio():.2f}:1")
    print()
    print("   Components:")
    for i, component in enumerate(capital_stack.components, 1):
        print(f"      {i}. {component.instrument.instrument_type.value}: "
              f"${component.instrument.amount:,.0f} (Position {component.position})")
    print()

    # ====================
    # 3. WATERFALL STRUCTURE
    # ====================

    print("3. WATERFALL STRUCTURE")
    print("-" * 90)

    waterfall = WaterfallStructure(
        waterfall_name="Dragon's Quest Waterfall",
        default_distribution_fee_rate=Decimal("30.0"),
        nodes=[
            # Tier 1: Distribution Fees (30%)
            WaterfallNode(
                priority=RecoupmentPriority.DISTRIBUTION_FEES,
                payee="Distributor",
                percentage=Decimal("30.0")
            ),

            # Tier 2: Senior Debt
            WaterfallNode(
                priority=RecoupmentPriority.SENIOR_DEBT,
                payee="Senior Lender",
                amount=Decimal("10000000")
            ),

            # Tier 3: Gap Debt
            WaterfallNode(
                priority=RecoupmentPriority.MEZZANINE_DEBT,
                payee="Gap Lender",
                amount=Decimal("5000000")
            ),

            # Tier 4: Pre-Sale (SVOD)
            WaterfallNode(
                priority=RecoupmentPriority.SALES_AGENT_EXPENSES,
                payee="SVOD Distributor",
                amount=Decimal("6000000")
            ),

            # Tier 5: Equity Recoupment (with 20% premium)
            WaterfallNode(
                priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                payee="Equity Investors",
                amount=Decimal("10800000")  # $9M × 1.20
            ),

            # Tier 6: Backend Participation
            WaterfallNode(
                priority=RecoupmentPriority.BACKEND_PARTICIPATION,
                payee="Equity Investors",
                percentage=Decimal("50.0")
            ),

            # Tier 7: Producer Net Profits
            WaterfallNode(
                priority=RecoupmentPriority.NET_PROFITS,
                payee="Producer",
                percentage=Decimal("50.0")
            ),
        ]
    )

    print("   Distribution Tiers:")
    for node in waterfall.nodes:
        if node.amount:
            print(f"      • {node.priority.value}: {node.payee} - ${node.amount:,.0f}")
        else:
            print(f"      • {node.priority.value}: {node.payee} - {node.percentage}%")
    print()

    # ====================
    # 4. REVENUE PROJECTION
    # ====================

    print("4. REVENUE PROJECTION (2025 Distribution Windows)")
    print("-" * 90)

    projector = RevenueProjector()

    projection = projector.project(
        total_ultimate_revenue=Decimal("75000000"),
        theatrical_box_office=Decimal("28000000"),
        svod_license_fee=Decimal("27000000"),
        release_strategy="wide_theatrical",
        project_name="The Dragon's Quest"
    )

    print(f"   Total Ultimate Revenue: ${Decimal('75000000'):,.0f}")
    print(f"   Projection Period: {projection.total_quarters} quarters (~{projection.total_quarters / 4:.1f} years)")
    print()
    print("   Revenue by Distribution Window:")
    for window, amount in sorted(projection.by_window.items(), key=lambda x: x[1], reverse=True):
        pct = (amount / Decimal("75000000")) * Decimal("100")
        print(f"      • {window.upper()}: ${amount:,.0f} ({pct:.1f}%)")
    print()

    # Show quarterly detail (first 8 quarters)
    print("   Quarterly Revenue (First 8 Quarters):")
    print(f"      {'Quarter':<10} {'Revenue':<18} {'Cumulative':<18} {'Active Windows'}")
    print("      " + "-" * 75)
    for detail in projection.quarterly_detail[:8]:
        q = detail['quarter']
        rev = Decimal(detail['revenue'])
        cum = Decimal(detail['cumulative'])
        windows = ', '.join(detail['windows_active'][:2])  # Show first 2
        print(f"      Q{q:<9} ${rev:>15,.0f}   ${cum:>15,.0f}   {windows}")
    print("      ...")
    print()

    # ====================
    # 5. WATERFALL EXECUTION
    # ====================

    print("5. WATERFALL EXECUTION (Time-Series)")
    print("-" * 90)

    executor = WaterfallExecutor(waterfall)
    waterfall_result = executor.execute_over_time(projection)

    print(f"   Quarters Executed: {len(waterfall_result.quarterly_executions)}")
    print(f"   Total Gross Receipts: ${waterfall_result.total_receipts:,.0f}")
    print(f"   Total Fees Deducted: ${waterfall_result.total_fees:,.0f}")
    print()
    print("   Total Payouts by Stakeholder:")
    for payee, amount in sorted(waterfall_result.total_paid_by_payee.items(), key=lambda x: x[1], reverse=True):
        print(f"      • {payee}: ${amount:,.0f}")
    print()

    # Unrecouped amounts
    if waterfall_result.final_unrecouped:
        print("   Unrecouped Amounts:")
        for node_id, amount in waterfall_result.final_unrecouped.items():
            print(f"      • {node_id}: ${amount:,.0f} remaining")
        print()

    # ====================
    # 6. STAKEHOLDER RETURN ANALYSIS
    # ====================

    print("6. STAKEHOLDER RETURN ANALYSIS (IRR, NPV, Cash-on-Cash)")
    print("-" * 90)

    analyzer = StakeholderAnalyzer(capital_stack, discount_rate=Decimal("0.15"))
    stakeholder_analysis = analyzer.analyze(waterfall_result)

    print(f"   Discount Rate: {analyzer.discount_rate * 100}% (for NPV calculations)")
    print()
    print("   Stakeholder Returns:")
    print()

    for stakeholder in stakeholder_analysis.stakeholders:
        print(f"   {stakeholder.stakeholder_name}")
        print(f"   {'─' * 60}")
        print(f"      Investment: ${stakeholder.initial_investment:,.0f}")
        print(f"      Total Receipts: ${stakeholder.total_receipts:,.0f}")
        print(f"      Cash-on-Cash Multiple: {stakeholder.cash_on_cash:.2f}x")

        if stakeholder.irr is not None:
            print(f"      IRR: {stakeholder.irr * 100:.2f}%")
        else:
            print(f"      IRR: N/A (no positive cash flows)")

        if stakeholder.npv is not None:
            print(f"      NPV @ 15%: ${stakeholder.npv:,.0f}")

        if stakeholder.payback_years is not None:
            print(f"      Payback Period: {stakeholder.payback_years:.1f} years")
        else:
            print(f"      Payback Period: Never (within projection)")

        print(f"      ROI: {stakeholder.roi_percentage:.1f}%")
        print()

    # Summary statistics
    print("   Summary Statistics:")
    print("   " + "─" * 60)
    summary = stakeholder_analysis.summary_statistics
    print(f"      Total Invested: ${summary['total_invested']}")
    print(f"      Total Recouped: ${summary['total_recouped']}")
    print(f"      Overall Recovery Rate: {summary['overall_recovery_rate']}%")

    if summary.get('median_irr'):
        print(f"      Median IRR: {Decimal(summary['median_irr']) * 100:.2f}%")

    if summary.get('equity_irr'):
        print(f"      Equity IRR: {Decimal(summary['equity_irr']) * 100:.2f}%")

    if summary.get('debt_recovery_rate'):
        print(f"      Debt Recovery Rate: {summary['debt_recovery_rate']}%")

    print()

    # ====================
    # 7. MONTE CARLO SIMULATION
    # ====================

    print("7. MONTE CARLO SIMULATION (Risk Quantification)")
    print("-" * 90)

    # Define revenue uncertainty
    revenue_dist = RevenueDistribution(
        variable_name="total_revenue",
        distribution_type="triangular",
        parameters={
            "min": Decimal("45000000"),    # Pessimistic: 40% lower
            "mode": Decimal("75000000"),   # Base case
            "max": Decimal("120000000")    # Optimistic: 60% higher
        }
    )

    print(f"   Revenue Distribution: Triangular")
    print(f"      Pessimistic (P10): ${revenue_dist.parameters['min']:,.0f}")
    print(f"      Base Case (P50): ${revenue_dist.parameters['mode']:,.0f}")
    print(f"      Optimistic (P90): ${revenue_dist.parameters['max']:,.0f}")
    print()

    # Run simulation (1,000 scenarios for demonstration)
    print("   Running 1,000 simulations...")
    simulator = MonteCarloSimulator(waterfall, capital_stack, projection)
    mc_result = simulator.simulate(revenue_dist, num_simulations=1000, seed=42)

    print(f"   ✓ Completed 1,000 scenarios")
    print()

    # Revenue percentiles
    print("   Revenue Percentiles:")
    print(f"      P10: ${mc_result.revenue_percentiles['p10']:,.0f}")
    print(f"      P50: ${mc_result.revenue_percentiles['p50']:,.0f}")
    print(f"      P90: ${mc_result.revenue_percentiles['p90']:,.0f}")
    print()

    # Stakeholder percentiles
    print("   Equity Investor Returns (Confidence Intervals):")
    print("   " + "─" * 60)
    equity_id = next(k for k in mc_result.stakeholder_percentiles.keys() if "equity" in k.lower())
    equity_percentiles = mc_result.stakeholder_percentiles[equity_id]

    print(f"      IRR:")
    print(f"         P10 (pessimistic): {equity_percentiles['irr_p10'] * 100:.2f}%")
    print(f"         P50 (median): {equity_percentiles['irr_p50'] * 100:.2f}%")
    print(f"         P90 (optimistic): {equity_percentiles['irr_p90'] * 100:.2f}%")
    print()

    print(f"      Cash-on-Cash Multiple:")
    print(f"         P10 (pessimistic): {equity_percentiles['coc_p10']:.2f}x")
    print(f"         P50 (median): {equity_percentiles['coc_p50']:.2f}x")
    print(f"         P90 (optimistic): {equity_percentiles['coc_p90']:.2f}x")
    print()

    # Probability of full recoupment
    print("   Probability of Full Recoupment:")
    for stakeholder_id, prob in mc_result.probability_of_recoupment.items():
        stakeholder_name = stakeholder_id.split('_', 1)[1] if '_' in stakeholder_id else stakeholder_id
        print(f"      • {stakeholder_name}: {prob * 100:.1f}%")
    print()

    # ====================
    # 8. EXECUTIVE SUMMARY
    # ====================

    print("=" * 90)
    print("EXECUTIVE SUMMARY")
    print("=" * 90)
    print()

    print("✓ PROJECT VIABILITY")
    print(f"   Capital Stack: ${capital_stack.total_capital_raised():,.0f} raised vs ${capital_stack.project_budget:,.0f} budget")
    print(f"   Financing Gap: ${capital_stack.financing_gap():,.0f}")
    print()

    print("✓ REVENUE OUTLOOK")
    print(f"   Base Case: $75.0M lifetime revenue")
    print(f"   Theatrical: $28.0M (37.3%)")
    print(f"   SVOD: $27.0M (36.0%)")
    print(f"   Other Windows: $20.0M (26.7%)")
    print()

    print("✓ INVESTOR RETURNS (Base Case)")
    for stakeholder in stakeholder_analysis.stakeholders:
        if stakeholder.irr:
            print(f"   {stakeholder.stakeholder_name}: {stakeholder.irr * 100:.1f}% IRR, {stakeholder.cash_on_cash:.2f}x cash-on-cash")

    print()

    print("✓ RISK ASSESSMENT (Monte Carlo)")
    print(f"   Revenue Range: $45M - $120M")
    print(f"   Equity IRR Range: {equity_percentiles['irr_p10'] * 100:.1f}% to {equity_percentiles['irr_p90'] * 100:.1f}%")
    print(f"   Probability of Equity Recoupment: {mc_result.probability_of_recoupment[equity_id] * 100:.1f}%")
    print()

    print("=" * 90)
    print()

    print("Analysis complete. Engine 2 successfully demonstrated:")
    print("  ✓ Revenue projection with 2025-accurate distribution windows")
    print("  ✓ Time-series waterfall execution")
    print("  ✓ IRR/NPV/cash-on-cash calculations for all stakeholders")
    print("  ✓ Monte Carlo simulation with 1,000 scenarios")
    print("  ✓ Risk quantification with confidence intervals")
    print()


if __name__ == "__main__":
    main()
