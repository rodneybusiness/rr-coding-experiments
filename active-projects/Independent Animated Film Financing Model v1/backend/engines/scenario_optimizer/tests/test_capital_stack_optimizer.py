"""
Unit Tests for CapitalStackOptimizer

Tests multi-objective optimization, constraint satisfaction, and optimization weights.
"""

import pytest
from decimal import Decimal
import numpy as np

from engines.scenario_optimizer import (
    CapitalStackOptimizer,
    ConstraintManager,
    ScenarioEvaluator,
    ScenarioGenerator,
    OptimizationObjective,
    OptimizationResult
)
from models.capital_stack import CapitalStack, CapitalComponent
from models.financial_instruments import (
    Equity, SeniorDebt, MezzanineDebt, GapFinancing, TaxIncentive
)
from models.waterfall import (
    WaterfallStructure, WaterfallNode, RecoupmentPriority, PayeeType, RecoupmentBasis
)


def create_minimal_capital_stack(name: str = "test", budget: Decimal = Decimal("30000000")) -> CapitalStack:
    """Create a minimal valid capital stack with one equity component for testing."""
    equity = Equity(amount=budget, ownership_percentage=Decimal("100.0"))
    component = CapitalComponent(instrument=equity, position=1)
    return CapitalStack(stack_name=name, project_budget=budget, components=[component])


class TestCapitalStackOptimizer:
    """Test CapitalStackOptimizer class."""

    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return CapitalStackOptimizer()

    @pytest.fixture
    def constraint_manager(self):
        """Create constraint manager."""
        return ConstraintManager()

    @pytest.fixture
    def evaluator(self):
        """Create scenario evaluator."""
        return ScenarioEvaluator()

    @pytest.fixture
    def template_stack(self):
        """Create template capital stack for optimization."""
        return CapitalStack(
            stack_name="template",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("10000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("10000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                ),
                CapitalComponent(
                    instrument=TaxIncentive(
                        amount=Decimal("10000000"),
                        jurisdiction="Canada",
                        qualified_spend=Decimal("30000000"),
                        credit_rate=Decimal("33.3"),
                        timing_months=18
                    ),
                    position=3
                )
            ]
        )

    @pytest.fixture
    def sample_waterfall(self):
        """Create sample waterfall for evaluation."""
        return WaterfallStructure(
            waterfall_id="test_waterfall",
            project_id="test_project",
            waterfall_name="Test Waterfall",
            default_distribution_fee_rate=Decimal("30.0"),
            nodes=[
                WaterfallNode(
                    node_id="node_1",
                    priority=RecoupmentPriority.SENIOR_DEBT_PRINCIPAL,
                    description="Senior Debt",
                    payee_type=PayeeType.LENDER,
                    payee_name="Senior Lender",
                    recoupment_basis=RecoupmentBasis.GROSS_RECEIPTS,
                    fixed_amount=Decimal("10000000")
                ),
                WaterfallNode(
                    node_id="node_2",
                    priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                    description="Equity",
                    payee_type=PayeeType.INVESTOR,
                    payee_name="Equity Investors",
                    recoupment_basis=RecoupmentBasis.REMAINING_POOL,
                    fixed_amount=Decimal("10000000")
                )
            ]
        )

    # Initialization Tests

    def test_initialization(self, optimizer):
        """Test optimizer initialization."""
        assert optimizer.constraint_manager is not None
        assert optimizer.evaluator is not None
        assert isinstance(optimizer.evaluation_cache, dict)

    def test_initialization_with_custom_managers(self, constraint_manager, evaluator):
        """Test initialization with custom managers."""
        optimizer = CapitalStackOptimizer(
            constraint_manager=constraint_manager,
            evaluator=evaluator
        )

        assert optimizer.constraint_manager == constraint_manager
        assert optimizer.evaluator == evaluator

    # Basic Optimization Tests

    def test_optimize_basic(self, optimizer, template_stack):
        """Test basic optimization without waterfall."""
        project_budget = Decimal("30000000")

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget,
            scenario_name="optimized_basic"
        )

        assert isinstance(result, OptimizationResult)
        assert result.solver_status == "SUCCESS"
        assert result.capital_stack is not None
        assert result.capital_stack.project_budget == project_budget
        assert result.objective_value > Decimal("0")

    def test_optimization_respects_budget(self, optimizer, template_stack):
        """Test that optimized stack respects project budget."""
        project_budget = Decimal("30000000")

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget
        )

        # Components should sum to budget (within tolerance)
        component_sum = sum(c.instrument.amount for c in result.capital_stack.components)
        tolerance = project_budget * Decimal("0.01")
        assert abs(component_sum - project_budget) <= tolerance

    def test_optimization_satisfies_hard_constraints(self, optimizer, template_stack):
        """Test that optimized stack satisfies hard constraints."""
        project_budget = Decimal("30000000")

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget
        )

        # Verify hard constraints
        is_valid = optimizer.constraint_manager.validate_hard_only(result.capital_stack)
        assert is_valid

    def test_optimization_with_custom_bounds(self, optimizer, template_stack):
        """Test optimization with custom bounds."""
        project_budget = Decimal("30000000")

        bounds = {
            "equity": (Decimal("30.0"), Decimal("50.0")),  # 30-50% equity
            "senior_debt": (Decimal("20.0"), Decimal("40.0"))  # 20-40% debt
        }

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget,
            bounds=bounds
        )

        # Check that bounds were respected
        equity_pct = result.allocations.get("equity", Decimal("0"))
        assert Decimal("30.0") <= equity_pct <= Decimal("50.0")

        senior_debt_pct = result.allocations.get("senior_debt", Decimal("0"))
        assert Decimal("20.0") <= senior_debt_pct <= Decimal("40.0")

    # Multi-Objective Optimization Tests

    def test_optimization_with_custom_weights(self, optimizer, template_stack):
        """Test optimization with custom objective weights."""
        project_budget = Decimal("30000000")

        # Prioritize tax incentives heavily
        weights = {
            "tax_incentives": Decimal("0.70"),
            "equity_irr": Decimal("0.10"),
            "risk": Decimal("0.10"),
            "cost_of_capital": Decimal("0.05"),
            "debt_recovery": Decimal("0.05")
        }

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget,
            objective_weights=weights
        )

        # Should have higher tax incentive allocation
        tax_pct = result.allocations.get("tax_incentive", Decimal("0")) + result.allocations.get("tax_incentives", Decimal("0"))
        assert tax_pct > Decimal("15.0")  # Should be significant

    def test_optimization_default_weights(self, optimizer):
        """Test that default weights are reasonable."""
        weights = optimizer._get_default_weights()

        assert "equity_irr" in weights
        assert "tax_incentives" in weights
        assert "risk" in weights
        assert "cost_of_capital" in weights
        assert "debt_recovery" in weights

        # Weights should sum to approximately 1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - Decimal("1.0")) < Decimal("0.01")

    def test_weighted_score_calculation(self, optimizer, evaluator, template_stack, sample_waterfall):
        """Test weighted score calculation."""
        # Evaluate template stack
        evaluation = evaluator.evaluate(
            template_stack,
            sample_waterfall,
            run_monte_carlo=False
        )

        weights = optimizer._get_default_weights()
        score = optimizer._calculate_weighted_score(evaluation, weights)

        assert score >= Decimal("0")
        assert score <= Decimal("100")

    # Convergence Tests

    def test_optimization_with_convergence(self, optimizer, template_stack):
        """Test optimization with convergence validation."""
        project_budget = Decimal("30000000")

        result = optimizer.optimize_with_convergence(
            template_stack=template_stack,
            project_budget=project_budget,
            num_starts=3
        )

        assert result.solver_status == "SUCCESS"
        assert "num_starts" in result.metadata
        assert "convergence_scores" in result.metadata
        assert len(result.metadata["convergence_scores"]) <= 3

    def test_convergence_metadata(self, optimizer, template_stack):
        """Test that convergence run includes metadata."""
        project_budget = Decimal("30000000")

        result = optimizer.optimize_with_convergence(
            template_stack=template_stack,
            project_budget=project_budget,
            num_starts=2
        )

        assert "convergence_std" in result.metadata
        assert "convergence_range" in result.metadata
        assert result.metadata["num_starts"] >= 1

    # Structural Validation Tests

    def test_structural_validation_gap_requires_senior(self, optimizer):
        """Test that gap financing requires senior debt."""
        # Stack with gap but no senior debt
        stack = CapitalStack(
            stack_name="invalid_structure",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=GapFinancing(
                        amount=Decimal("15000000"),
                        interest_rate=Decimal("10.0"),
                        term_months=24,
                        minimum_presales_percentage=Decimal("30.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("15000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=2
                )
            ]
        )

        is_valid = optimizer._validate_structure(stack)
        assert not is_valid  # Should fail structural validation

    def test_structural_validation_mezzanine_limit(self, optimizer):
        """Test that mezzanine shouldn't exceed senior debt."""
        # Stack with mezzanine > senior
        stack = CapitalStack(
            stack_name="invalid_mezz",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("5000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=MezzanineDebt(
                        amount=Decimal("10000000"),  # More than senior
                        interest_rate=Decimal("12.0"),
                        term_months=36,
                        equity_kicker_percentage=Decimal("5.0")
                    ),
                    position=2
                ),
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("15000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=3
                )
            ]
        )

        is_valid = optimizer._validate_structure(stack)
        assert not is_valid

    def test_structural_validation_debt_to_equity_limit(self, optimizer):
        """Test that extreme debt/equity ratios are rejected."""
        # Stack with 10:1 debt to equity ratio
        stack = CapitalStack(
            stack_name="extreme_leverage",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("27000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("3000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=2
                )
            ]
        )

        is_valid = optimizer._validate_structure(stack)
        # 9:1 ratio exceeds 5:1 limit
        assert not is_valid

    # Bounds Tests

    def test_get_bounds_default(self, optimizer):
        """Test getting default bounds for instruments."""
        equity_bounds = optimizer._get_bounds("equity", None)
        assert equity_bounds[0] >= Decimal("0")  # Min
        assert equity_bounds[1] <= Decimal("100")  # Max
        assert equity_bounds[0] < equity_bounds[1]

    def test_get_bounds_custom(self, optimizer):
        """Test getting custom bounds."""
        custom_bounds = {
            "equity": (Decimal("25.0"), Decimal("60.0"))
        }

        equity_bounds = optimizer._get_bounds("equity", custom_bounds)
        assert equity_bounds == (Decimal("25.0"), Decimal("60.0"))

    def test_bounds_applied_in_optimization(self, optimizer, template_stack):
        """Test that bounds are actually applied in optimization."""
        project_budget = Decimal("30000000")

        # Tight bounds
        bounds = {
            "equity": (Decimal("45.0"), Decimal("55.0"))
        }

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget,
            bounds=bounds
        )

        equity_pct = result.allocations.get("equity", Decimal("0"))
        assert Decimal("45.0") <= equity_pct <= Decimal("55.0")

    # Optimization Result Tests

    def test_optimization_result_structure(self, optimizer, template_stack):
        """Test that optimization result has correct structure."""
        project_budget = Decimal("30000000")

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget
        )

        assert hasattr(result, 'objective_value')
        assert hasattr(result, 'capital_stack')
        assert hasattr(result, 'solver_status')
        assert hasattr(result, 'solve_time_seconds')
        assert hasattr(result, 'allocations')
        assert hasattr(result, 'metadata')

    def test_optimization_result_metadata(self, optimizer, template_stack):
        """Test that optimization result includes metadata."""
        project_budget = Decimal("30000000")

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget
        )

        assert "num_iterations" in result.metadata
        assert "num_evaluations" in result.metadata
        assert "method" in result.metadata
        assert result.metadata["method"] == "SLSQP"

    def test_solve_time_recorded(self, optimizer, template_stack):
        """Test that solve time is recorded."""
        project_budget = Decimal("30000000")

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget
        )

        assert result.solve_time_seconds > 0
        assert result.solve_time_seconds < 60  # Should be reasonably fast

    # Cache Tests

    def test_evaluation_cache_used(self, optimizer, template_stack):
        """Test that evaluation cache is used to avoid redundant evaluations."""
        project_budget = Decimal("30000000")

        # Clear cache
        optimizer.evaluation_cache = {}

        result = optimizer.optimize(
            template_stack=template_stack,
            project_budget=project_budget
        )

        # Cache should have entries
        assert len(optimizer.evaluation_cache) > 0

    def test_cache_key_generation(self, optimizer):
        """Test cache key generation."""
        amounts = np.array([10000000.0, 15000000.0, 5000000.0])

        key = optimizer._get_cache_key(amounts)

        assert isinstance(key, str)
        assert len(key) > 0

        # Same amounts should produce same key
        key2 = optimizer._get_cache_key(amounts)
        assert key == key2

    # Instrument Type Normalization Tests

    def test_normalize_instrument_type(self, optimizer):
        """Test instrument type normalization."""
        assert optimizer._normalize_instrument_type("SeniorDebt") == "senior_debt"
        assert optimizer._normalize_instrument_type("MezzanineDebt") == "mezzanine_debt"
        assert optimizer._normalize_instrument_type("TaxIncentive") == "tax_incentive"
        assert optimizer._normalize_instrument_type("Equity") == "equity"

    # Stack Building Tests

    def test_build_stack_from_amounts(self, optimizer, template_stack):
        """Test building capital stack from optimized amounts."""
        template_instruments = [c.instrument for c in template_stack.components]
        amounts = np.array([12000000.0, 10000000.0, 8000000.0])
        project_budget = Decimal("30000000")

        stack = optimizer._build_stack_from_amounts(
            template_instruments,
            amounts,
            project_budget,
            "test_scenario"
        )

        assert stack.stack_name == "test_scenario"
        assert stack.project_budget == project_budget
        assert len(stack.components) == 3

    def test_build_stack_excludes_zero_amounts(self, optimizer, template_stack):
        """Test that zero amounts are excluded from built stack."""
        template_instruments = [c.instrument for c in template_stack.components]
        amounts = np.array([20000000.0, 0.0, 10000000.0])  # Middle instrument is zero
        project_budget = Decimal("30000000")

        stack = optimizer._build_stack_from_amounts(
            template_instruments,
            amounts,
            project_budget,
            "test_scenario"
        )

        # Should only have 2 components (zero excluded)
        assert len(stack.components) == 2

    # Perturbation Tests

    def test_perturb_stack(self, optimizer, template_stack):
        """Test stack perturbation for convergence testing."""
        perturbed = optimizer._perturb_stack(template_stack, perturbation=0.1)

        assert perturbed.project_budget == template_stack.project_budget
        assert len(perturbed.components) == len(template_stack.components)

        # Components should be different but close
        original_amounts = [c.instrument.amount for c in template_stack.components]
        perturbed_amounts = [c.instrument.amount for c in perturbed.components]

        for orig, pert in zip(original_amounts, perturbed_amounts):
            # Should be within 20% (10% perturbation + renormalization)
            assert abs(pert - orig) / orig < Decimal("0.25")

    def test_perturbed_stack_sums_to_budget(self, optimizer, template_stack):
        """Test that perturbed stack still sums to budget."""
        perturbed = optimizer._perturb_stack(template_stack, perturbation=0.15)

        component_sum = sum(c.instrument.amount for c in perturbed.components)
        tolerance = template_stack.project_budget * Decimal("0.01")

        assert abs(component_sum - template_stack.project_budget) <= tolerance

    # Simple Evaluation Tests

    def test_simple_evaluation_fallback(self, optimizer, template_stack):
        """Test simple evaluation when waterfall not provided."""
        evaluation = optimizer._simple_evaluation(template_stack)

        assert evaluation.scenario_name == template_stack.stack_name
        assert evaluation.tax_incentive_gross_credit >= Decimal("0")
        assert evaluation.weighted_cost_of_capital >= Decimal("0")

    def test_simple_evaluation_calculates_tax_incentives(self, optimizer, template_stack):
        """Test that simple evaluation calculates tax incentives."""
        evaluation = optimizer._simple_evaluation(template_stack)

        # Template has $10M in tax incentives
        assert evaluation.tax_incentive_gross_credit > Decimal("0")
        assert evaluation.tax_incentive_effective_rate > Decimal("0")


class TestOptimizationResult:
    """Test OptimizationResult dataclass."""

    def test_optimization_result_creation(self):
        """Test creating optimization result."""
        stack = create_minimal_capital_stack()

        result = OptimizationResult(
            objective_value=Decimal("75.5"),
            capital_stack=stack,
            solver_status="SUCCESS",
            solve_time_seconds=1.5,
            allocations={"equity": Decimal("50.0"), "senior_debt": Decimal("50.0")}
        )

        assert result.objective_value == Decimal("75.5")
        assert result.capital_stack == stack
        assert result.solver_status == "SUCCESS"
        assert result.solve_time_seconds == 1.5
        assert len(result.allocations) == 2

    def test_optimization_result_with_metadata(self):
        """Test optimization result with metadata."""
        stack = create_minimal_capital_stack()

        result = OptimizationResult(
            objective_value=Decimal("80.0"),
            capital_stack=stack,
            solver_status="SUCCESS",
            solve_time_seconds=2.0,
            allocations={},
            metadata={
                "num_iterations": 25,
                "convergence_std": 0.5
            }
        )

        assert result.metadata["num_iterations"] == 25
        assert result.metadata["convergence_std"] == 0.5
