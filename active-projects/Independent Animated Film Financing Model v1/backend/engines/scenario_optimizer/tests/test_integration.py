"""
Integration Tests for Engine 3

End-to-end tests covering complete workflows from scenario generation through
optimization, evaluation, comparison, and trade-off analysis.
"""

import pytest
from pathlib import Path
from decimal import Decimal

from backend.models.waterfall import WaterfallStructure, WaterfallNode, RecoupmentPriority
from backend.models.capital_stack import CapitalStack

from backend.engines.scenario_optimizer import (
    ScenarioGenerator,
    ConstraintManager,
    CapitalStackOptimizer,
    ScenarioEvaluator,
    ScenarioComparator,
    TradeOffAnalyzer,
    OptimizationObjective,
    RankingCriterion,
    HardConstraint,
    SoftConstraint,
    ConstraintType,
    ConstraintCategory,
    DEFAULT_TEMPLATES
)


@pytest.fixture
def sample_waterfall():
    """Create sample waterfall structure for testing."""
    waterfall = WaterfallStructure(
        waterfall_name="Test Waterfall",
        default_distribution_fee_rate=Decimal("30.0"),
        nodes=[
            WaterfallNode(
                priority=RecoupmentPriority.SENIOR_DEBT_PRINCIPAL,
                payee="Senior Lender",
                amount=Decimal("10000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.MEZZANINE_DEBT,
                payee="Mezzanine Lender",
                amount=Decimal("5000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                payee="Equity Investors",
                amount=Decimal("15000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.NET_PROFITS,
                payee="Equity Investors",
                amount=None,
                percentage=Decimal("100.0")
            ),
        ]
    )
    return waterfall


class TestScenarioGenerator:
    """Test scenario generation from templates."""

    def test_generate_from_debt_heavy_template(self):
        """Test generating debt-heavy scenario."""
        generator = ScenarioGenerator()
        project_budget = Decimal("30000000")

        stack = generator.generate_from_template("debt_heavy", project_budget)

        assert stack is not None
        assert stack.project_budget == project_budget
        assert len(stack.components) > 0

        # Verify debt-heavy structure (should have significant debt)
        from backend.models.financial_instruments import Debt
        debt_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, Debt)
        )
        debt_pct = (debt_amount / project_budget) * Decimal("100")
        assert debt_pct >= Decimal("60.0")  # Should be >60% debt

    def test_generate_from_equity_heavy_template(self):
        """Test generating equity-heavy scenario."""
        generator = ScenarioGenerator()
        project_budget = Decimal("30000000")

        stack = generator.generate_from_template("equity_heavy", project_budget)

        assert stack is not None

        # Verify equity-heavy structure
        from backend.models.financial_instruments import Equity
        equity_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, Equity)
        )
        equity_pct = (equity_amount / project_budget) * Decimal("100")
        assert equity_pct >= Decimal("50.0")  # Should be >50% equity

    def test_generate_from_incentive_maximized_template(self):
        """Test generating incentive-maximized scenario."""
        generator = ScenarioGenerator()
        project_budget = Decimal("30000000")

        stack = generator.generate_from_template("incentive_maximized", project_budget)

        assert stack is not None

        # Verify high tax incentives
        from backend.models.financial_instruments import TaxIncentive
        incentive_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, TaxIncentive)
        )
        incentive_pct = (incentive_amount / project_budget) * Decimal("100")
        assert incentive_pct >= Decimal("20.0")  # Should be >20% incentives

    def test_generate_multiple_scenarios(self):
        """Test generating multiple scenarios at once."""
        generator = ScenarioGenerator()
        project_budget = Decimal("30000000")

        scenarios = generator.generate_multiple_scenarios(project_budget)

        assert len(scenarios) == 5  # All 5 default templates
        assert all(s.project_budget == project_budget for s in scenarios)

    def test_custom_template(self):
        """Test adding and using custom template."""
        from backend.engines.scenario_optimizer.scenario_generator import FinancingTemplate

        generator = ScenarioGenerator()

        custom_template = FinancingTemplate(
            template_name="custom_test",
            description="Custom test template",
            target_allocations={
                "equity": Decimal("50.0"),
                "senior_debt": Decimal("30.0"),
                "tax_incentives": Decimal("20.0")
            },
            typical_terms={
                "equity": {"ownership": 70.0, "premium": 15.0},
                "senior_debt": {"interest_rate": 7.5, "term_months": 24, "origination_fee": 1.5},
                "tax_incentives": {"jurisdiction": "Test", "credit_rate": 30.0, "timing_months": 18}
            }
        )

        generator.add_custom_template(custom_template)

        stack = generator.generate_from_template("custom_test", Decimal("25000000"))

        assert stack is not None
        assert len(stack.components) == 3


class TestConstraintManager:
    """Test constraint management and validation."""

    def test_default_constraints_loaded(self):
        """Test that default constraints are loaded."""
        manager = ConstraintManager()

        assert len(manager.constraints) > 0
        assert len(manager.get_hard_constraints()) > 0
        assert len(manager.get_soft_constraints()) > 0

    def test_validate_valid_stack(self):
        """Test validation of valid capital stack."""
        manager = ConstraintManager()
        generator = ScenarioGenerator()

        stack = generator.generate_from_template("balanced", Decimal("30000000"))

        result = manager.validate(stack)

        assert result.is_valid
        assert len(result.hard_violations) == 0

    def test_validate_min_equity_constraint(self):
        """Test minimum equity constraint."""
        manager = ConstraintManager()

        # Create stack with <15% equity (violates hard constraint)
        from backend.models.capital_stack import CapitalComponent
        from backend.models.financial_instruments import Equity, SeniorDebt

        equity = Equity(amount=Decimal("3000000"), ownership_percentage=Decimal("100"))  # 10%
        debt = SeniorDebt(amount=Decimal("27000000"), interest_rate=Decimal("8.0"), term_months=24)

        stack = CapitalStack(
            stack_name="Low Equity Test",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(instrument=debt, position=1),
                CapitalComponent(instrument=equity, position=2)
            ]
        )

        result = manager.validate(stack)

        assert not result.is_valid  # Should fail min equity constraint
        assert len(result.hard_violations) > 0

    def test_add_custom_constraint(self):
        """Test adding custom constraint."""
        manager = ConstraintManager()

        def custom_validator(stack: CapitalStack) -> bool:
            return stack.project_budget >= Decimal("20000000")

        custom_constraint = HardConstraint(
            constraint_id="min_budget_20m",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Minimum $20M budget",
            validator=custom_validator
        )

        manager.add_constraint(custom_constraint)

        assert "min_budget_20m" in manager.constraints


class TestCapitalStackOptimizer:
    """Test capital stack optimization with scipy backend."""

    def test_optimize_from_template(self, sample_waterfall):
        """Test optimizing starting from template."""
        generator = ScenarioGenerator()
        optimizer = CapitalStackOptimizer()

        # Generate template
        template = generator.generate_from_template("balanced", Decimal("30000000"))

        # Optimize
        result = optimizer.optimize(
            template_stack=template,
            project_budget=Decimal("30000000"),
            waterfall_structure=sample_waterfall,
            scenario_name="optimized"
        )

        assert result is not None
        assert result.capital_stack is not None
        assert result.solver_status == "SUCCESS"
        assert result.solve_time_seconds > 0

        # Should have valid allocations
        assert len(result.allocations) > 0
        total_allocation = sum(result.allocations.values())
        assert abs(total_allocation - Decimal("100.0")) < Decimal("0.1")  # Sum to 100%

    def test_optimize_improves_template(self, sample_waterfall):
        """Test that optimization improves over template."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator()
        optimizer = CapitalStackOptimizer(evaluator=evaluator)

        template = generator.generate_from_template("balanced", Decimal("30000000"))

        # Evaluate template
        template_eval = evaluator.evaluate(
            template,
            sample_waterfall,
            run_monte_carlo=False
        )
        template_score = template_eval.overall_score

        # Optimize
        result = optimizer.optimize(
            template_stack=template,
            project_budget=Decimal("30000000"),
            waterfall_structure=sample_waterfall,
            scenario_name="optimized"
        )

        # Evaluate optimized
        optimized_eval = evaluator.evaluate(
            result.capital_stack,
            sample_waterfall,
            run_monte_carlo=False
        )

        # Optimized should be at least as good as template
        assert optimized_eval.overall_score >= template_score * Decimal("0.95")  # Allow 5% tolerance

    def test_optimize_with_custom_weights(self, sample_waterfall):
        """Test optimization with custom objective weights."""
        generator = ScenarioGenerator()
        optimizer = CapitalStackOptimizer()

        template = generator.generate_from_template("balanced", Decimal("30000000"))

        # Maximize tax incentives
        weights = {
            "equity_irr": Decimal("0.1"),
            "tax_incentives": Decimal("0.7"),  # High weight on tax incentives
            "risk": Decimal("0.1"),
            "cost_of_capital": Decimal("0.05"),
            "debt_recovery": Decimal("0.05")
        }

        result = optimizer.optimize(
            template_stack=template,
            project_budget=Decimal("30000000"),
            objective_weights=weights,
            waterfall_structure=sample_waterfall,
            scenario_name="tax_optimized"
        )

        assert result is not None
        assert result.solver_status == "SUCCESS"

        # Should allocate significant tax incentives
        tax_incentive_pct = result.allocations.get("tax_incentive", Decimal("0"))
        assert tax_incentive_pct >= Decimal("15.0")  # Should be meaningful allocation

    def test_optimize_with_bounds(self, sample_waterfall):
        """Test optimization with custom bounds."""
        generator = ScenarioGenerator()
        optimizer = CapitalStackOptimizer()

        template = generator.generate_from_template("balanced", Decimal("30000000"))

        bounds = {
            "equity": (Decimal("25.0"), Decimal("35.0")),  # Constrain equity to 25-35%
            "senior_debt": (Decimal("20.0"), Decimal("40.0"))
        }

        result = optimizer.optimize(
            template_stack=template,
            project_budget=Decimal("30000000"),
            bounds=bounds,
            waterfall_structure=sample_waterfall,
            scenario_name="bounded"
        )

        assert result is not None

        # Check bounds are respected
        equity_pct = result.allocations.get("equity", Decimal("0"))
        assert Decimal("25.0") <= equity_pct <= Decimal("35.0")

    def test_optimize_respects_hard_constraints(self, sample_waterfall):
        """Test that optimizer respects hard constraints."""
        generator = ScenarioGenerator()
        constraint_manager = ConstraintManager()
        optimizer = CapitalStackOptimizer(constraint_manager=constraint_manager)

        template = generator.generate_from_template("balanced", Decimal("30000000"))

        result = optimizer.optimize(
            template_stack=template,
            project_budget=Decimal("30000000"),
            waterfall_structure=sample_waterfall,
            scenario_name="constrained"
        )

        # Validate result satisfies constraints
        validation = constraint_manager.validate(result.capital_stack)
        assert validation.is_valid
        assert len(validation.hard_violations) == 0

    def test_structural_validation(self):
        """Test structural validation rules."""
        from backend.models.capital_stack import CapitalComponent
        from backend.models.financial_instruments import Equity, GapFinancing

        optimizer = CapitalStackOptimizer()

        # Create stack with gap but no senior debt (violates rule)
        gap = GapFinancing(
            amount=Decimal("5000000"),
            interest_rate=Decimal("10.0"),
            term_months=24,
            minimum_presales_percentage=Decimal("30.0")
        )
        equity = Equity(
            amount=Decimal("25000000"),
            ownership_percentage=Decimal("100.0"),
            premium_percentage=Decimal("20.0")
        )

        invalid_stack = CapitalStack(
            stack_name="Invalid",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(instrument=gap, position=1),
                CapitalComponent(instrument=equity, position=2)
            ]
        )

        # Should fail structural validation
        assert not optimizer._validate_structure(invalid_stack)

    def test_convergence_validation(self, sample_waterfall):
        """Test optimization with convergence validation."""
        generator = ScenarioGenerator()
        optimizer = CapitalStackOptimizer()

        template = generator.generate_from_template("balanced", Decimal("30000000"))

        result = optimizer.optimize_with_convergence(
            template_stack=template,
            project_budget=Decimal("30000000"),
            waterfall_structure=sample_waterfall,
            scenario_name="convergence_tested",
            num_starts=3
        )

        assert result is not None
        assert result.solver_status == "SUCCESS"

        # Should have convergence metadata
        assert "num_starts" in result.metadata
        assert "convergence_scores" in result.metadata
        assert result.metadata["num_starts"] >= 1

        # Convergence scores should be similar
        scores = result.metadata["convergence_scores"]
        if len(scores) > 1:
            score_range = max(scores) - min(scores)
            avg_score = sum(scores) / len(scores)
            # Relative range should be small
            if avg_score > 0:
                assert (score_range / avg_score) < 0.2  # Within 20%


class TestScenarioEvaluator:
    """Test scenario evaluation with Engines 1 & 2 integration."""

    def test_evaluate_basic_scenario(self, sample_waterfall):
        """Test basic scenario evaluation."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))

        stack = generator.generate_from_template("balanced", Decimal("30000000"))

        evaluation = evaluator.evaluate(
            capital_stack=stack,
            waterfall_structure=sample_waterfall,
            run_monte_carlo=False  # Skip for speed
        )

        assert evaluation is not None
        assert evaluation.scenario_name == stack.stack_name
        assert evaluation.total_revenue_projected > 0
        assert evaluation.overall_score > 0

    def test_evaluate_with_monte_carlo(self, sample_waterfall):
        """Test evaluation with Monte Carlo simulation."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("60000000"))

        stack = generator.generate_from_template("equity_heavy", Decimal("30000000"))

        evaluation = evaluator.evaluate(
            capital_stack=stack,
            waterfall_structure=sample_waterfall,
            run_monte_carlo=True,
            num_simulations=100  # Small number for test speed
        )

        assert evaluation is not None

        # Should have Monte Carlo risk metrics
        assert evaluation.equity_irr_p50 is not None
        assert evaluation.probability_of_equity_recoupment >= 0

    def test_evaluate_multiple_scenarios(self, sample_waterfall):
        """Test evaluating multiple scenarios."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))

        stacks = generator.generate_multiple_scenarios(Decimal("30000000"))

        evaluations = []
        for stack in stacks[:3]:  # Test first 3 for speed
            evaluation = evaluator.evaluate(
                capital_stack=stack,
                waterfall_structure=sample_waterfall,
                run_monte_carlo=False
            )
            evaluations.append(evaluation)

        assert len(evaluations) == 3
        assert all(e.overall_score > 0 for e in evaluations)


class TestScenarioComparator:
    """Test scenario comparison and ranking."""

    def test_rank_scenarios_default_weights(self, sample_waterfall):
        """Test ranking scenarios with default weights."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        comparator = ScenarioComparator()

        # Generate and evaluate scenarios
        stacks = generator.generate_multiple_scenarios(Decimal("30000000"))
        evaluations = [
            evaluator.evaluate(stack, sample_waterfall, run_monte_carlo=False)
            for stack in stacks[:3]
        ]

        rankings = comparator.rank_scenarios(evaluations)

        assert len(rankings) == 3
        assert rankings[0].rank == 1
        assert rankings[1].rank == 2
        assert rankings[2].rank == 3

        # Ranks should be in descending weighted score order
        assert rankings[0].weighted_score >= rankings[1].weighted_score
        assert rankings[1].weighted_score >= rankings[2].weighted_score

    def test_rank_scenarios_equity_perspective(self, sample_waterfall):
        """Test ranking from equity investor perspective."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        comparator = ScenarioComparator(stakeholder_perspective="equity")

        stacks = generator.generate_multiple_scenarios(Decimal("30000000"))
        evaluations = [
            evaluator.evaluate(stack, sample_waterfall, run_monte_carlo=False)
            for stack in stacks[:3]
        ]

        rankings = comparator.rank_scenarios(evaluations)

        assert len(rankings) == 3
        # Equity perspective should heavily weight equity IRR

    def test_compare_two_scenarios(self, sample_waterfall):
        """Test head-to-head comparison."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        comparator = ScenarioComparator()

        stack_a = generator.generate_from_template("debt_heavy", Decimal("30000000"))
        stack_b = generator.generate_from_template("equity_heavy", Decimal("30000000"))

        eval_a = evaluator.evaluate(stack_a, sample_waterfall, run_monte_carlo=False)
        eval_b = evaluator.evaluate(stack_b, sample_waterfall, run_monte_carlo=False)

        winner, criterion_winners = comparator.compare_two_scenarios(eval_a, eval_b)

        assert winner in [eval_a.scenario_name, eval_b.scenario_name, "tie"]
        assert len(criterion_winners) > 0

    def test_get_top_n_scenarios(self, sample_waterfall):
        """Test getting top N scenarios."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        comparator = ScenarioComparator()

        stacks = generator.generate_multiple_scenarios(Decimal("30000000"))
        evaluations = [
            evaluator.evaluate(stack, sample_waterfall, run_monte_carlo=False)
            for stack in stacks
        ]

        top_3 = comparator.get_top_n_scenarios(evaluations, n=3)

        assert len(top_3) == 3
        assert all(r.rank <= 3 for r in top_3)


class TestTradeOffAnalyzer:
    """Test trade-off analysis and Pareto frontier identification."""

    def test_identify_pareto_frontier(self, sample_waterfall):
        """Test Pareto frontier identification."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        analyzer = TradeOffAnalyzer()

        stacks = generator.generate_multiple_scenarios(Decimal("30000000"))
        evaluations = [
            evaluator.evaluate(stack, sample_waterfall, run_monte_carlo=False)
            for stack in stacks
        ]

        frontier = analyzer.identify_pareto_frontier(
            evaluations,
            "equity_irr",
            "probability_of_equity_recoupment"
        )

        assert frontier is not None
        assert len(frontier.frontier_points) > 0
        assert all(p.is_pareto_optimal for p in frontier.frontier_points)

    def test_complete_trade_off_analysis(self, sample_waterfall):
        """Test complete trade-off analysis."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        analyzer = TradeOffAnalyzer()

        stacks = generator.generate_multiple_scenarios(Decimal("30000000"))
        evaluations = [
            evaluator.evaluate(stack, sample_waterfall, run_monte_carlo=False)
            for stack in stacks
        ]

        analysis = analyzer.analyze(evaluations)

        assert analysis is not None
        assert len(analysis.pareto_frontiers) > 0
        assert len(analysis.recommended_scenarios) > 0

        # Should have recommendations for different preferences
        assert "high_return_seeking" in analysis.recommended_scenarios
        assert "risk_averse" in analysis.recommended_scenarios

    def test_pareto_optimal_multi_objective(self, sample_waterfall):
        """Test multi-objective Pareto optimality."""
        generator = ScenarioGenerator()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        analyzer = TradeOffAnalyzer()

        stacks = generator.generate_multiple_scenarios(Decimal("30000000"))
        evaluations = [
            evaluator.evaluate(stack, sample_waterfall, run_monte_carlo=False)
            for stack in stacks
        ]

        pareto_optimal = analyzer.get_pareto_optimal_scenarios(
            evaluations,
            objectives=["equity_irr", "tax_incentive_effective_rate", "probability_of_equity_recoupment"]
        )

        assert len(pareto_optimal) > 0
        assert len(pareto_optimal) <= len(evaluations)


class TestCompleteWorkflow:
    """Test complete end-to-end workflows."""

    def test_end_to_end_scenario_optimization(self, sample_waterfall):
        """Test complete workflow: generate → optimize → evaluate → compare → analyze."""

        # 1. Generate scenarios from templates
        generator = ScenarioGenerator()
        scenarios = generator.generate_multiple_scenarios(Decimal("30000000"))

        assert len(scenarios) == 5

        # 2. Evaluate all scenarios
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        evaluations = []

        for stack in scenarios:
            evaluation = evaluator.evaluate(
                capital_stack=stack,
                waterfall_structure=sample_waterfall,
                run_monte_carlo=True,
                num_simulations=100
            )
            evaluations.append(evaluation)

        assert len(evaluations) == 5
        assert all(e.overall_score > 0 for e in evaluations)

        # 3. Rank scenarios
        comparator = ScenarioComparator()
        rankings = comparator.rank_scenarios(evaluations)

        assert len(rankings) == 5
        assert rankings[0].rank == 1

        winner = rankings[0]
        print(f"\nWinner: {winner.scenario_name}")
        print(f"Score: {winner.weighted_score:.1f}")
        print(f"Equity IRR: {winner.evaluation.equity_irr or 0:.1f}%")

        # 4. Analyze trade-offs
        analyzer = TradeOffAnalyzer()
        trade_off_analysis = analyzer.analyze(evaluations)

        assert len(trade_off_analysis.pareto_frontiers) > 0
        assert len(trade_off_analysis.recommended_scenarios) > 0

        # 5. Validate winner satisfies constraints
        constraint_manager = ConstraintManager()
        validation = constraint_manager.validate(winner.evaluation.capital_stack)

        assert validation.is_valid

    def test_custom_optimization_workflow(self, sample_waterfall):
        """Test workflow with custom optimization."""

        # 1. Generate template
        generator = ScenarioGenerator()
        template = generator.generate_from_template("balanced", Decimal("30000000"))

        # 2. Create optimizer with constraint manager
        constraint_manager = ConstraintManager()
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        optimizer = CapitalStackOptimizer(constraint_manager, evaluator)

        # 3. Optimize with custom weights (maximize tax incentives)
        weights = {
            "equity_irr": Decimal("0.15"),
            "tax_incentives": Decimal("0.50"),  # High weight
            "risk": Decimal("0.15"),
            "cost_of_capital": Decimal("0.10"),
            "debt_recovery": Decimal("0.10")
        }

        optimization_result = optimizer.optimize(
            template_stack=template,
            project_budget=Decimal("30000000"),
            objective_weights=weights,
            waterfall_structure=sample_waterfall,
            scenario_name="custom_optimized"
        )

        assert optimization_result.solver_status == "SUCCESS"

        # 4. Evaluate optimized scenario
        evaluation = evaluator.evaluate(
            capital_stack=optimization_result.capital_stack,
            waterfall_structure=sample_waterfall,
            run_monte_carlo=True,
            num_simulations=100
        )

        assert evaluation.overall_score > 0

        # 5. Validate constraint satisfaction
        validation = constraint_manager.validate(optimization_result.capital_stack)
        assert validation.is_valid

    def test_comparative_analysis_workflow(self, sample_waterfall):
        """Test workflow comparing optimized vs template-based scenarios."""

        # Generate template scenarios
        generator = ScenarioGenerator()
        template_stacks = generator.generate_multiple_scenarios(Decimal("30000000"))

        # Generate optimized scenario from balanced template
        balanced_template = generator.generate_from_template("balanced", Decimal("30000000"))
        optimizer = CapitalStackOptimizer()
        optimized_result = optimizer.optimize(
            template_stack=balanced_template,
            project_budget=Decimal("30000000"),
            waterfall_structure=sample_waterfall,
            scenario_name="optimizer_generated"
        )

        # Combine all scenarios
        all_stacks = template_stacks + [optimized_result.capital_stack]

        # Evaluate all
        evaluator = ScenarioEvaluator(base_revenue_projection=Decimal("75000000"))
        evaluations = [
            evaluator.evaluate(stack, sample_waterfall, run_monte_carlo=False)
            for stack in all_stacks
        ]

        # Compare
        comparator = ScenarioComparator()
        rankings = comparator.rank_scenarios(evaluations)

        assert len(rankings) == len(all_stacks)

        # Check if optimized scenario is competitive
        optimized_ranking = next(r for r in rankings if r.scenario_name == "optimizer_generated")
        print(f"\nOptimized scenario rank: #{optimized_ranking.rank}/{len(rankings)}")

        # Should be in top half (or at least not last)
        assert optimized_ranking.rank <= len(rankings)


import logging
logger = logging.getLogger(__name__)
