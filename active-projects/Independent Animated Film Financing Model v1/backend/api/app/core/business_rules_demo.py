"""
Demonstration of Business Rules Configuration Module

This script demonstrates how the centralized business_rules module
is used throughout the API layer.
"""

from decimal import Decimal
from app.core import business_rules


def demo_monetization_options():
    """Demonstrate tax credit monetization option calculations."""
    print("=" * 70)
    print("TAX CREDIT MONETIZATION OPTIONS")
    print("=" * 70)

    gross_credit = Decimal("5000000")  # $5M tax credit
    options = business_rules.get_monetization_options(gross_credit)

    print(f"\nGross Tax Credit: ${gross_credit:,.2f}")
    print("\nMonetization Options:")
    print(f"  1. Direct Receipt ({business_rules.DIRECT_RECEIPT_RATE * 100:.0f}%): "
          f"${options['direct_receipt']:,.2f}")
    print(f"     - Full value, but wait 18-24 months")

    print(f"\n  2. Bank Loan ({business_rules.BANK_LOAN_ADVANCE_RATE * 100:.0f}%): "
          f"${options['bank_loan']:,.2f}")
    print(f"     - Cost: ${gross_credit - options['bank_loan']:,.2f} "
          f"({(1 - business_rules.BANK_LOAN_ADVANCE_RATE) * 100:.0f}% interest/fees)")
    print(f"     - Immediate liquidity")

    print(f"\n  3. Broker Sale ({business_rules.BROKER_SALE_RATE * 100:.0f}%): "
          f"${options['broker_sale']:,.2f}")
    print(f"     - Discount: ${gross_credit - options['broker_sale']:,.2f} "
          f"({(1 - business_rules.BROKER_SALE_RATE) * 100:.0f}%)")
    print(f"     - Immediate cash, no recourse")


def demo_scenario_templates():
    """Demonstrate scenario template selection."""
    print("\n" + "=" * 70)
    print("SCENARIO TEMPLATE SELECTION")
    print("=" * 70)

    print(f"\nDefault scenarios per project: {business_rules.SCENARIOS_PER_PROJECT}")
    print(f"\nAvailable templates ({len(business_rules.SCENARIO_TEMPLATES)}):")
    for i, template in enumerate(business_rules.SCENARIO_TEMPLATES, 1):
        print(f"  {i}. {template}")

    print("\nGenerating 3 scenarios:")
    selected = business_rules.get_scenario_templates(3)
    for i, template in enumerate(selected, 1):
        print(f"  {i}. {template}")


def demo_performance_thresholds():
    """Demonstrate performance evaluation thresholds."""
    print("\n" + "=" * 70)
    print("PERFORMANCE EVALUATION THRESHOLDS")
    print("=" * 70)

    print("\nEquity IRR Assessment:")
    print(f"  Excellent: >= {business_rules.EQUITY_IRR_EXCELLENT_THRESHOLD}%")
    print(f"  Low:       <  {business_rules.EQUITY_IRR_LOW_THRESHOLD}%")

    print("\nTax Incentive Capture:")
    print(f"  Exceptional: >= {business_rules.TAX_RATE_EXCEPTIONAL_THRESHOLD}%")
    print(f"  Good:        >= {business_rules.TAX_RATE_GOOD_THRESHOLD}%")
    print(f"  Limited:     <  {business_rules.TAX_RATE_GOOD_THRESHOLD}%")

    print("\nRisk Score (0-100 scale):")
    print(f"  Low Risk:  <  {business_rules.RISK_SCORE_LOW_THRESHOLD}")
    print(f"  High Risk: >  {business_rules.RISK_SCORE_HIGH_THRESHOLD}")

    print("\nDebt Coverage Ratio:")
    print(f"  Strong: >= {business_rules.DEBT_COVERAGE_STRONG_THRESHOLD}x")
    print(f"  Weak:   <  {business_rules.DEBT_COVERAGE_WEAK_THRESHOLD}x")

    print("\nCost of Capital:")
    print(f"  Low:  <  {business_rules.COST_OF_CAPITAL_LOW_THRESHOLD}%")
    print(f"  High: >  {business_rules.COST_OF_CAPITAL_HIGH_THRESHOLD}%")


def demo_project_estimates():
    """Demonstrate project-level estimates."""
    print("\n" + "=" * 70)
    print("PROJECT ESTIMATES")
    print("=" * 70)

    budget = Decimal("30000000")  # $30M

    print(f"\nProject Budget: ${budget:,.2f}")

    revenue = budget * business_rules.REVENUE_MULTIPLIER_DEFAULT
    print(f"\nRevenue Estimate ({business_rules.REVENUE_MULTIPLIER_DEFAULT}x): "
          f"${revenue:,.2f}")

    tax_incentives = business_rules.estimate_tax_incentives(budget)
    print(f"\nTax Incentive Estimate ({business_rules.TAX_CAPTURE_RATE_ESTIMATE}%): "
          f"${tax_incentives:,.2f}")

    committed = business_rules.estimate_committed_capital(budget)
    print(f"\nCommitted Capital Estimate ({business_rules.CAPITAL_COMMITMENT_RATE_ESTIMATE * 100:.0f}%): "
          f"${committed:,.2f}")


def demo_scurve_defaults():
    """Demonstrate S-curve investment drawdown defaults."""
    print("\n" + "=" * 70)
    print("S-CURVE INVESTMENT DRAWDOWN DEFAULTS")
    print("=" * 70)

    print(f"\nDefault Steepness: {business_rules.SCURVE_DEFAULT_STEEPNESS}")
    print(f"  - Controls how rapidly spending transitions through midpoint")
    print(f"  - Higher values = more rapid transition")
    print(f"  - {business_rules.SCURVE_DEFAULT_STEEPNESS} is standard for film production")

    print(f"\nDefault Midpoint: {business_rules.SCURVE_DEFAULT_MIDPOINT}")
    print(f"  - Point where peak spending occurs (0-1 scale)")
    print(f"  - {business_rules.SCURVE_DEFAULT_MIDPOINT} = peak spending at 40% through timeline")
    print(f"  - Typical for: pre-production (slow) → production (peak) → post (taper)")


def demo_cash_flow_distribution():
    """Demonstrate cash flow distribution assumptions."""
    print("\n" + "=" * 70)
    print("CASH FLOW DISTRIBUTION")
    print("=" * 70)

    total_benefit = Decimal("4000000")  # $4M

    print(f"\nTotal Tax Benefit: ${total_benefit:,.2f}")
    print(f"\nDistribution Pattern:")

    primary = total_benefit * business_rules.CASH_FLOW_PRIMARY_DISTRIBUTION_PCT
    secondary = total_benefit * business_rules.CASH_FLOW_SECONDARY_DISTRIBUTION_PCT

    print(f"  Primary Quarter ({business_rules.CASH_FLOW_PRIMARY_DISTRIBUTION_PCT * 100:.0f}%): "
          f"${primary:,.2f}")
    print(f"  Next Quarter ({business_rules.CASH_FLOW_SECONDARY_DISTRIBUTION_PCT * 100:.0f}%): "
          f"${secondary:,.2f}")
    print(f"\n  Total: ${primary + secondary:,.2f}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "BUSINESS RULES CONFIGURATION DEMO" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")

    demo_monetization_options()
    demo_scenario_templates()
    demo_performance_thresholds()
    demo_project_estimates()
    demo_scurve_defaults()
    demo_cash_flow_distribution()

    print("\n" + "=" * 70)
    print("BENEFITS OF CENTRALIZED CONFIGURATION")
    print("=" * 70)
    print("""
1. Single Source of Truth
   - All business assumptions in one location
   - Easy to find and understand current values
   - No hunting through codebase for magic numbers

2. Easy Updates
   - Change business logic without modifying code
   - Update one value to affect entire application
   - Reduces risk of inconsistent assumptions

3. Documentation
   - Comments explain rationale for each value
   - Business context preserved alongside technical code
   - Easier onboarding for new developers

4. Testability
   - Can mock/override for testing scenarios
   - Easy to test sensitivity to different assumptions
   - Clear separation of business logic from implementation

5. Future Extensibility
   - Ready to move to database configuration
   - Easy to add environment-specific overrides
   - Can support user-configurable business rules
""")

    print("=" * 70)
    print("\n")
