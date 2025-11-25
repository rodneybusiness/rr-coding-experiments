"""
Complete Scenario Optimization Workflow

Demonstrates the full capabilities of Engine 3: Scenario Generator & Optimizer.

This example shows:
1. Generating diverse financing scenarios from templates
2. Creating custom optimized scenarios
3. Evaluating scenarios with Engines 1 & 2 integration
4. Comparing and ranking scenarios
5. Analyzing trade-offs and identifying Pareto frontier
6. Making recommendations for different stakeholder perspectives
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from models.waterfall import WaterfallStructure, WaterfallNode, RecoupmentPriority
from models.capital_stack import CapitalStack

from engines.scenario_optimizer import (
    ScenarioGenerator,
    ConstraintManager,
    CapitalStackOptimizer,
    ScenarioEvaluator,
    ScenarioComparator,
    TradeOffAnalyzer,
    OptimizationObjective,
    DEFAULT_TEMPLATES
)


def create_sample_waterfall() -> WaterfallStructure:
    """Create sample 7-tier waterfall structure."""
    waterfall = WaterfallStructure(
        waterfall_name="Dragon's Quest Animated Feature - Waterfall",
        default_distribution_fee_rate=Decimal("30.0"),
        nodes=[
            # Tier 1: Distribution Fees (handled automatically)

            # Tier 2: Senior Debt
            WaterfallNode(
                priority=RecoupmentPriority.SENIOR_DEBT,
                payee="Senior Lender",
                amount=Decimal("10000000"),
                percentage=None
            ),

            # Tier 3: Mezzanine Debt
            WaterfallNode(
                priority=RecoupmentPriority.MEZZANINE_DEBT,
                payee="Mezzanine Lender",
                amount=Decimal("5000000"),
                percentage=None
            ),

            # Tier 4: Gap Financing
            WaterfallNode(
                priority=RecoupmentPriority.GAP_FINANCING,
                payee="Gap Lender",
                amount=Decimal("3000000"),
                percentage=None
            ),

            # Tier 5: Pre-Sales / Minimum Guarantees
            WaterfallNode(
                priority=RecoupmentPriority.MINIMUM_GUARANTEE,
                payee="SVOD Platform",
                amount=Decimal("8000000"),
                percentage=None
            ),

            # Tier 6: Equity Recoupment
            WaterfallNode(
                priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                payee="Equity Investors",
                amount=Decimal("12000000"),
                percentage=None
            ),

            # Tier 7: Equity Premium (20%)
            WaterfallNode(
                priority=RecoupmentPriority.EQUITY_PREMIUM,
                payee="Equity Investors",
                amount=Decimal("2400000"),  # 20% of $12M
                percentage=None
            ),

            # Tier 8: Net Profits Split
            WaterfallNode(
                priority=RecoupmentPriority.NET_PROFITS,
                payee="Equity Investors",
                amount=None,
                percentage=Decimal("100.0")
            ),
        ]
    )
    return waterfall


def main():
    """Run complete scenario optimization workflow."""

    print("=" * 100)
    print("COMPLETE SCENARIO OPTIMIZATION WORKFLOW")
    print("Project: Dragon's Quest - $30M Animated Feature")
    print("=" * 100)

    # Configuration
    PROJECT_BUDGET = Decimal("30000000")
    BASE_REVENUE = Decimal("75000000")
    MONTE_CARLO_SIMULATIONS = 1000

    # Create waterfall structure
    waterfall = create_sample_waterfall()

    # ============================================================================
    # STEP 1: Generate Diverse Scenarios from Templates
    # ============================================================================
    print("\n" + "-" * 100)
    print("STEP 1: GENERATING SCENARIOS FROM TEMPLATES")
    print("-" * 100)

    generator = ScenarioGenerator()
    print(f"\nAvailable templates: {', '.join(DEFAULT_TEMPLATES)}")

    template_scenarios = generator.generate_multiple_scenarios(PROJECT_BUDGET)

    print(f"\nGenerated {len(template_scenarios)} scenarios:")
    for stack in template_scenarios:
        print(f"  • {stack.stack_name}")
        print(f"      Components: {len(stack.components)}")
        print(f"      Budget: ${stack.project_budget:,.0f}")

    # ============================================================================
    # STEP 2: Create Optimized Scenarios
    # ============================================================================
    print("\n" + "-" * 100)
    print("STEP 2: CREATING OPTIMIZED SCENARIOS")
    print("-" * 100)

    optimizer = CapitalStackOptimizer()

    # Optimization 1: Maximize Tax Incentives
    print("\nOptimization 1: Maximize Tax Incentives")
    opt_result_1 = optimizer.optimize(
        project_budget=PROJECT_BUDGET,
        objective=OptimizationObjective.MAXIMIZE_TAX_INCENTIVES,
        available_instruments=["equity", "senior_debt", "gap_financing", "pre_sales", "tax_incentives"],
        scenario_name="optimizer_max_incentives"
    )
    print(f"  Status: {opt_result_1.solver_status}")
    print(f"  Solve time: {opt_result_1.solve_time_seconds:.2f}s")
    print(f"  Allocations:")
    for instrument, pct in opt_result_1.allocations.items():
        print(f"    {instrument}: {pct:.1f}%")

    # Optimization 2: Minimize Cost of Capital
    print("\nOptimization 2: Minimize Cost of Capital")
    opt_result_2 = optimizer.optimize(
        project_budget=PROJECT_BUDGET,
        objective=OptimizationObjective.MINIMIZE_COST_OF_CAPITAL,
        available_instruments=["equity", "senior_debt", "gap_financing", "pre_sales", "tax_incentives"],
        scenario_name="optimizer_low_cost"
    )
    print(f"  Status: {opt_result_2.solver_status}")
    print(f"  Allocations:")
    for instrument, pct in opt_result_2.allocations.items():
        print(f"    {instrument}: {pct:.1f}%")

    # Combine all scenarios
    all_scenarios = template_scenarios + [
        opt_result_1.capital_stack,
        opt_result_2.capital_stack
    ]

    # ============================================================================
    # STEP 3: Evaluate All Scenarios
    # ============================================================================
    print("\n" + "-" * 100)
    print("STEP 3: EVALUATING ALL SCENARIOS")
    print("-" * 100)

    evaluator = ScenarioEvaluator(base_revenue_projection=BASE_REVENUE)

    print(f"\nEvaluating {len(all_scenarios)} scenarios with:")
    print(f"  Base Revenue: ${BASE_REVENUE:,.0f}")
    print(f"  Monte Carlo Simulations: {MONTE_CARLO_SIMULATIONS}")
    print(f"  Discount Rate: {evaluator.discount_rate * 100:.0f}%")

    evaluations = []
    for i, stack in enumerate(all_scenarios):
        print(f"\n  Evaluating {i+1}/{len(all_scenarios)}: {stack.stack_name}...", end=" ")

        evaluation = evaluator.evaluate(
            capital_stack=stack,
            waterfall_structure=waterfall,
            revenue_projection=BASE_REVENUE,
            run_monte_carlo=True,
            num_simulations=MONTE_CARLO_SIMULATIONS
        )
        evaluations.append(evaluation)

        print(f"Score: {evaluation.overall_score:.1f}/100")

    # ============================================================================
    # STEP 4: Rank and Compare Scenarios
    # ============================================================================
    print("\n" + "-" * 100)
    print("STEP 4: RANKING SCENARIOS")
    print("-" * 100)

    # Default perspective
    print("\n--- DEFAULT PERSPECTIVE (Balanced) ---")
    comparator_default = ScenarioComparator()
    rankings_default = comparator_default.rank_scenarios(evaluations)

    print("\nTop 5 Scenarios (Balanced Perspective):")
    for i, ranking in enumerate(rankings_default[:5]):
        eval = ranking.evaluation
        print(f"\n#{i+1}: {ranking.scenario_name}")
        print(f"  Weighted Score: {ranking.weighted_score:.1f}/100")
        print(f"  Equity IRR: {eval.equity_irr or 0:.1f}%")
        print(f"  Tax Incentives: {eval.tax_incentive_effective_rate:.1f}% of budget")
        print(f"  P(Recoupment): {eval.probability_of_equity_recoupment * Decimal('100'):.0f}%")
        print(f"  Cost of Capital: {eval.weighted_cost_of_capital:.1f}%")

        if eval.strengths:
            print(f"  Strengths: {', '.join(eval.strengths[:2])}")

    # Equity investor perspective
    print("\n--- EQUITY INVESTOR PERSPECTIVE ---")
    comparator_equity = ScenarioComparator(stakeholder_perspective="equity")
    rankings_equity = comparator_equity.rank_scenarios(evaluations)

    print("\nTop 3 Scenarios (Equity Investor):")
    for i, ranking in enumerate(rankings_equity[:3]):
        print(f"  #{i+1}: {ranking.scenario_name} "
              f"(IRR: {ranking.evaluation.equity_irr or 0:.1f}%, "
              f"Score: {ranking.weighted_score:.1f})")

    # Producer perspective
    print("\n--- PRODUCER PERSPECTIVE ---")
    comparator_producer = ScenarioComparator(stakeholder_perspective="producer")
    rankings_producer = comparator_producer.rank_scenarios(evaluations)

    print("\nTop 3 Scenarios (Producer):")
    for i, ranking in enumerate(rankings_producer[:3]):
        print(f"  #{i+1}: {ranking.scenario_name} "
              f"(Incentives: {ranking.evaluation.tax_incentive_effective_rate:.1f}%, "
              f"Score: {ranking.weighted_score:.1f})")

    # ============================================================================
    # STEP 5: Trade-Off Analysis
    # ============================================================================
    print("\n" + "-" * 100)
    print("STEP 5: TRADE-OFF ANALYSIS & PARETO FRONTIER")
    print("-" * 100)

    analyzer = TradeOffAnalyzer()

    # Analyze trade-offs
    trade_off_analysis = analyzer.analyze(evaluations)

    print(f"\nIdentified {len(trade_off_analysis.pareto_frontiers)} trade-off frontiers:")

    # Show first frontier in detail
    frontier_1 = trade_off_analysis.pareto_frontiers[0]
    print(f"\n--- {frontier_1.objective_1_name} vs {frontier_1.objective_2_name} ---")
    print(f"Pareto-optimal scenarios: {len(frontier_1.frontier_points)}")
    print(f"Dominated scenarios: {len(frontier_1.dominated_points)}")

    if frontier_1.trade_off_slope:
        print(f"Average trade-off rate: {abs(frontier_1.trade_off_slope):.2f}")

    print("\nPareto-Optimal Points:")
    for point in frontier_1.frontier_points:
        print(f"  • {point.scenario_name}")
        print(f"      {frontier_1.objective_1_name}: {point.objective_1_value:.2f}")
        print(f"      {frontier_1.objective_2_name}: {point.objective_2_value:.2f}")

    # Show recommendations
    print("\n--- RECOMMENDATIONS BY PREFERENCE ---")
    for preference, scenario_name in trade_off_analysis.recommended_scenarios.items():
        recommended_eval = next(e for e in evaluations if e.scenario_name == scenario_name)
        print(f"\n{preference.replace('_', ' ').title()}:")
        print(f"  → {scenario_name}")
        print(f"     Equity IRR: {recommended_eval.equity_irr or 0:.1f}%")
        print(f"     Tax Incentives: {recommended_eval.tax_incentive_effective_rate:.1f}%")
        print(f"     P(Recoupment): {recommended_eval.probability_of_equity_recoupment * Decimal('100'):.0f}%")

    # ============================================================================
    # STEP 6: Detailed Winner Analysis
    # ============================================================================
    print("\n" + "-" * 100)
    print("STEP 6: DETAILED WINNER ANALYSIS")
    print("-" * 100)

    winner = rankings_default[0].evaluation

    print(f"\nWinning Scenario: {winner.scenario_name}")
    print(f"Overall Score: {winner.overall_score:.1f}/100")
    print(f"Rank: #1 of {len(all_scenarios)}")

    print("\n--- KEY METRICS ---")
    print(f"Equity IRR: {winner.equity_irr or 0:.1f}%")
    print(f"  P10: {winner.equity_irr_p10 or 0:.1f}%")
    print(f"  P50: {winner.equity_irr_p50 or 0:.1f}%")
    print(f"  P90: {winner.equity_irr_p90 or 0:.1f}%")

    print(f"\nTax Incentives: {winner.tax_incentive_effective_rate:.1f}% of budget")
    print(f"  Gross Credit: ${winner.tax_incentive_gross_credit:,.0f}")
    print(f"  Net Benefit: ${winner.tax_incentive_net_benefit:,.0f}")

    print(f"\nRisk Metrics:")
    print(f"  Probability of Recoupment: {winner.probability_of_equity_recoupment * Decimal('100'):.0f}%")
    print(f"  Senior Debt Recovery: {winner.senior_debt_recovery_rate:.0f}%")

    print(f"\nCost Metrics:")
    print(f"  Weighted Cost of Capital: {winner.weighted_cost_of_capital:.1f}%")
    print(f"  Total Interest Expense: ${winner.total_interest_expense:,.0f}")
    print(f"  Total Fees: ${winner.total_fees:,.0f}")

    print("\n--- STRENGTHS ---")
    for strength in winner.strengths:
        print(f"  ✓ {strength}")

    if winner.weaknesses:
        print("\n--- WEAKNESSES ---")
        for weakness in winner.weaknesses:
            print(f"  ✗ {weakness}")

    # Capital Stack Breakdown
    print("\n--- CAPITAL STACK BREAKDOWN ---")
    for component in winner.capital_stack.components:
        instrument = component.instrument
        pct = (instrument.amount / winner.capital_stack.project_budget) * Decimal("100")
        print(f"  {type(instrument).__name__}: ${instrument.amount:,.0f} ({pct:.1f}%)")

    # ============================================================================
    # STEP 7: Constraint Validation
    # ============================================================================
    print("\n" + "-" * 100)
    print("STEP 7: CONSTRAINT VALIDATION")
    print("-" * 100)

    constraint_manager = ConstraintManager()

    print("\nValidating all scenarios against constraints...")

    valid_count = 0
    for evaluation in evaluations:
        validation = constraint_manager.validate(evaluation.capital_stack)

        if validation.is_valid:
            valid_count += 1
            print(f"  ✓ {evaluation.scenario_name}: VALID")
        else:
            print(f"  ✗ {evaluation.scenario_name}: INVALID")
            print(f"      Hard violations: {len(validation.hard_violations)}")

    print(f"\n{valid_count}/{len(evaluations)} scenarios satisfy all hard constraints")

    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)

    print(f"\nProject: Dragon's Quest")
    print(f"Budget: ${PROJECT_BUDGET:,.0f}")
    print(f"Revenue Projection: ${BASE_REVENUE:,.0f}")

    print(f"\nScenarios Analyzed: {len(all_scenarios)}")
    print(f"  Template-based: {len(template_scenarios)}")
    print(f"  Optimizer-generated: {len(all_scenarios) - len(template_scenarios)}")

    print(f"\nRecommended Scenario: {winner.scenario_name}")
    print(f"  Overall Score: {winner.overall_score:.1f}/100")
    print(f"  Equity IRR: {winner.equity_irr or 0:.1f}%")
    print(f"  Tax Incentives: {winner.tax_incentive_effective_rate:.1f}% of budget")
    print(f"  Probability of Recoupment: {winner.probability_of_equity_recoupment * Decimal('100'):.0f}%")

    print("\n" + "=" * 100)
    print("WORKFLOW COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()
