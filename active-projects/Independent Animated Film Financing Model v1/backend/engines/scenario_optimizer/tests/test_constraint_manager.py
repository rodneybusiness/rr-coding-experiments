"""
Unit Tests for ConstraintManager

Tests constraint validation, violation detection, and constraint types
(budget, ownership, debt ratios).
"""

import pytest
from decimal import Decimal

from engines.scenario_optimizer import (
    ConstraintManager,
    Constraint,
    HardConstraint,
    SoftConstraint,
    ConstraintType,
    ConstraintCategory,
    ConstraintViolation,
    ConstraintValidationResult
)
from models.capital_stack import CapitalStack, CapitalComponent
from models.financial_instruments import (
    Equity, SeniorDebt, MezzanineDebt, GapFinancing, TaxIncentive
)


class TestConstraintManager:
    """Test ConstraintManager class."""

    @pytest.fixture
    def manager(self):
        """Create constraint manager instance."""
        return ConstraintManager()

    @pytest.fixture
    def simple_stack(self):
        """Create simple valid capital stack."""
        return CapitalStack(
            stack_name="test_stack",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("15000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("15000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

    @pytest.fixture
    def high_debt_stack(self):
        """Create capital stack with high debt ratio."""
        return CapitalStack(
            stack_name="high_debt_stack",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("5000000"),
                        ownership_percentage=Decimal("30.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("25000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

    @pytest.fixture
    def low_equity_stack(self):
        """Create capital stack with low equity."""
        return CapitalStack(
            stack_name="low_equity_stack",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("3000000"),  # Only 10%
                        ownership_percentage=Decimal("50.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("27000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

    # Initialization Tests

    def test_initialization_loads_default_constraints(self, manager):
        """Test that manager loads default constraints on init."""
        assert len(manager.constraints) > 0
        assert len(manager._hard_constraints) > 0
        assert len(manager._soft_constraints) > 0

    def test_has_min_equity_constraint(self, manager):
        """Test that min equity constraint is loaded."""
        assert "min_equity_15pct" in manager.constraints
        constraint = manager.constraints["min_equity_15pct"]
        assert constraint.constraint_type == ConstraintType.HARD

    def test_has_max_debt_ratio_constraint(self, manager):
        """Test that max debt ratio constraint is loaded."""
        assert "max_debt_ratio_75pct" in manager.constraints
        constraint = manager.constraints["max_debt_ratio_75pct"]
        assert constraint.constraint_type == ConstraintType.HARD

    def test_has_budget_sum_constraint(self, manager):
        """Test that budget sum constraint is loaded."""
        assert "budget_sum_matches" in manager.constraints
        constraint = manager.constraints["budget_sum_matches"]
        assert constraint.constraint_type == ConstraintType.HARD

    # Constraint Addition/Removal Tests

    def test_add_custom_hard_constraint(self, manager):
        """Test adding custom hard constraint."""
        def custom_validator(stack):
            return stack.project_budget >= Decimal("10000000")

        custom_constraint = HardConstraint(
            constraint_id="min_budget_10m",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Minimum $10M budget",
            validator=custom_validator
        )

        initial_count = len(manager.constraints)
        manager.add_constraint(custom_constraint)

        assert len(manager.constraints) == initial_count + 1
        assert "min_budget_10m" in manager.constraints
        assert "min_budget_10m" in manager._hard_constraints

    def test_add_custom_soft_constraint(self, manager):
        """Test adding custom soft constraint."""
        def custom_validator(stack):
            return stack.project_budget <= Decimal("50000000")

        custom_constraint = SoftConstraint(
            constraint_id="prefer_small_budget",
            constraint_type=ConstraintType.SOFT,
            category=ConstraintCategory.FINANCIAL,
            description="Prefer budgets under $50M",
            validator=custom_validator,
            penalty_weight=Decimal("0.3")
        )

        initial_count = len(manager.constraints)
        manager.add_constraint(custom_constraint)

        assert len(manager.constraints) == initial_count + 1
        assert "prefer_small_budget" in manager.constraints
        assert "prefer_small_budget" in manager._soft_constraints

    def test_remove_constraint(self, manager):
        """Test removing constraint."""
        initial_count = len(manager.constraints)

        # Add a constraint
        def dummy_validator(stack):
            return True

        constraint = HardConstraint(
            constraint_id="temp_constraint",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Temporary constraint",
            validator=dummy_validator
        )

        manager.add_constraint(constraint)
        assert len(manager.constraints) == initial_count + 1

        # Remove it
        manager.remove_constraint("temp_constraint")
        assert len(manager.constraints) == initial_count
        assert "temp_constraint" not in manager.constraints

    # Hard Constraint Validation Tests

    def test_validate_valid_stack(self, manager, simple_stack):
        """Test validating a valid capital stack."""
        result = manager.validate(simple_stack)

        assert result.is_valid
        assert len(result.hard_violations) == 0

    def test_validate_low_equity_stack_fails(self, manager, low_equity_stack):
        """Test that low equity stack fails min equity constraint."""
        result = manager.validate(low_equity_stack)

        assert not result.is_valid
        assert len(result.hard_violations) > 0

        # Should have min equity violation
        violation_ids = [v.constraint.constraint_id for v in result.hard_violations]
        assert "min_equity_15pct" in violation_ids

    def test_validate_high_debt_stack_fails(self, manager, high_debt_stack):
        """Test that high debt stack fails max debt constraint."""
        result = manager.validate(high_debt_stack)

        # High debt stack has 83% debt, which exceeds 75% limit
        assert not result.is_valid
        assert len(result.hard_violations) > 0

        violation_ids = [v.constraint.constraint_id for v in result.hard_violations]
        assert "max_debt_ratio_75pct" in violation_ids

    def test_validate_mismatched_budget_fails(self, manager):
        """Test that mismatched component sum fails budget constraint."""
        # Create stack where components don't sum to budget
        stack = CapitalStack(
            stack_name="mismatched_stack",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("10000000"),  # Components sum to 20M, not 30M
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
                )
            ]
        )

        result = manager.validate(stack)

        assert not result.is_valid
        violation_ids = [v.constraint.constraint_id for v in result.hard_violations]
        assert "budget_sum_matches" in violation_ids

    def test_validate_hard_only_fast_path(self, manager, simple_stack):
        """Test fast validation of hard constraints only."""
        is_valid = manager.validate_hard_only(simple_stack)

        assert is_valid

    def test_validate_hard_only_rejects_invalid(self, manager, low_equity_stack):
        """Test hard-only validation rejects invalid stack."""
        is_valid = manager.validate_hard_only(low_equity_stack)

        assert not is_valid

    # Soft Constraint Validation Tests

    def test_soft_constraints_generate_penalties(self, manager):
        """Test that soft constraint violations generate penalties."""
        # Create stack that violates soft constraints
        stack = CapitalStack(
            stack_name="soft_violation_stack",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("21000000"),  # 70% equity (violates balanced risk)
                        ownership_percentage=Decimal("20.0"),  # Low ownership (violates minimize dilution)
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("9000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

        result = manager.validate(stack)

        # Should be valid (no hard violations) but have soft violations
        assert result.is_valid
        assert len(result.soft_violations) > 0
        assert result.total_penalty > Decimal("0")

    def test_soft_constraint_penalty_weights(self, manager):
        """Test that penalty weights are applied correctly."""
        def always_fails(stack):
            return False

        constraint = SoftConstraint(
            constraint_id="test_penalty",
            constraint_type=ConstraintType.SOFT,
            category=ConstraintCategory.FINANCIAL,
            description="Test penalty weighting",
            validator=always_fails,
            penalty_weight=Decimal("0.5")
        )

        manager.add_constraint(constraint)

        result = manager.validate(CapitalStack(
            stack_name="test",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("30000000"),
                        ownership_percentage=Decimal("100.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                )
            ]
        ))

        # Should have penalty from test constraint
        assert result.total_penalty >= Decimal("0.5") * Decimal("0.5")  # weight * severity

    # Constraint Querying Tests

    def test_get_constraints_by_category(self, manager):
        """Test getting constraints by category."""
        financial_constraints = manager.get_constraints_by_category(ConstraintCategory.FINANCIAL)

        assert len(financial_constraints) > 0
        for constraint in financial_constraints:
            assert constraint.category == ConstraintCategory.FINANCIAL

    def test_get_hard_constraints(self, manager):
        """Test getting all hard constraints."""
        hard_constraints = manager.get_hard_constraints()

        assert len(hard_constraints) > 0
        for constraint in hard_constraints:
            assert constraint.constraint_type == ConstraintType.HARD

    def test_get_soft_constraints(self, manager):
        """Test getting all soft constraints."""
        soft_constraints = manager.get_soft_constraints()

        assert len(soft_constraints) > 0
        for constraint in soft_constraints:
            assert constraint.constraint_type == ConstraintType.SOFT

    # Constraint Type Tests

    def test_min_equity_constraint_validation(self, manager):
        """Test minimum equity constraint specifically."""
        constraint = manager.constraints["min_equity_15pct"]

        # Valid stack (50% equity)
        valid_stack = CapitalStack(
            stack_name="valid",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("15000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("15000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

        assert constraint.validate(valid_stack)

        # Invalid stack (10% equity)
        invalid_stack = CapitalStack(
            stack_name="invalid",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("3000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("27000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

        assert not constraint.validate(invalid_stack)

    def test_max_debt_ratio_constraint_validation(self, manager):
        """Test maximum debt ratio constraint specifically."""
        constraint = manager.constraints["max_debt_ratio_75pct"]

        # Valid stack (50% debt)
        valid_stack = CapitalStack(
            stack_name="valid",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("15000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("15000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

        assert constraint.validate(valid_stack)

        # Invalid stack (90% debt)
        invalid_stack = CapitalStack(
            stack_name="invalid",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("3000000"),
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("27000000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

        assert not constraint.validate(invalid_stack)

    def test_budget_sum_constraint_with_tolerance(self, manager):
        """Test that budget sum constraint allows small rounding errors."""
        constraint = manager.constraints["budget_sum_matches"]

        # Stack with 0.5% difference (within 1% tolerance)
        stack = CapitalStack(
            stack_name="slightly_off",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("15075000"),  # Sum = 30,150,000 (0.5% over)
                        ownership_percentage=Decimal("40.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                ),
                CapitalComponent(
                    instrument=SeniorDebt(
                        amount=Decimal("15075000"),
                        interest_rate=Decimal("8.0"),
                        term_months=24,
                        origination_fee_percentage=Decimal("2.0")
                    ),
                    position=2
                )
            ]
        )

        assert constraint.validate(stack)  # Should pass with tolerance

    # Violation Details Tests

    def test_constraint_violation_has_details(self, manager, low_equity_stack):
        """Test that violations include details."""
        result = manager.validate(low_equity_stack)

        assert len(result.hard_violations) > 0

        for violation in result.hard_violations:
            assert violation.constraint is not None
            assert violation.details != ""
            assert violation.severity > Decimal("0")

    def test_validation_result_summary(self, manager, simple_stack):
        """Test that validation result includes summary."""
        result = manager.validate(simple_stack)

        assert result.summary != ""
        assert "Valid" in result.summary or "Invalid" in result.summary

    # Edge Cases

    def test_validate_empty_stack(self, manager):
        """Test validating empty capital stack - Pydantic now rejects empty stacks."""
        from pydantic import ValidationError

        # CapitalStack now requires at least one component (Pydantic validation)
        with pytest.raises(ValidationError) as exc_info:
            CapitalStack(
                stack_name="empty",
                project_budget=Decimal("30000000"),
                components=[]
            )

        # Verify it's the right validation error
        assert "at least 1 item" in str(exc_info.value)

    def test_validate_single_instrument_stack(self, manager):
        """Test validating stack with single instrument."""
        single_stack = CapitalStack(
            stack_name="single",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("30000000"),
                        ownership_percentage=Decimal("100.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                )
            ]
        )

        result = manager.validate(single_stack)

        # 100% equity is valid (meets all hard constraints)
        assert result.is_valid

    def test_constraint_validator_exception_returns_false(self, manager):
        """Test that validator exceptions are caught and return False."""
        def bad_validator(stack):
            raise ValueError("Intentional error")

        bad_constraint = HardConstraint(
            constraint_id="bad_constraint",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Bad constraint",
            validator=bad_validator
        )

        manager.add_constraint(bad_constraint)

        result = manager.validate(CapitalStack(
            stack_name="test",
            project_budget=Decimal("30000000"),
            components=[
                CapitalComponent(
                    instrument=Equity(
                        amount=Decimal("30000000"),
                        ownership_percentage=Decimal("100.0"),
                        premium_percentage=Decimal("20.0")
                    ),
                    position=1
                )
            ]
        ))

        # Should catch exception and mark as invalid
        assert not result.is_valid


class TestConstraintDataClasses:
    """Test constraint data classes."""

    def test_hard_constraint_forces_type(self):
        """Test that HardConstraint forces HARD type."""
        constraint = HardConstraint(
            constraint_id="test",
            constraint_type=ConstraintType.SOFT,  # Try to set as SOFT
            category=ConstraintCategory.FINANCIAL,
            description="Test",
            validator=lambda s: True
        )

        # Should be forced to HARD
        assert constraint.constraint_type == ConstraintType.HARD

    def test_soft_constraint_forces_type(self):
        """Test that SoftConstraint forces SOFT type."""
        constraint = SoftConstraint(
            constraint_id="test",
            constraint_type=ConstraintType.HARD,  # Try to set as HARD
            category=ConstraintCategory.FINANCIAL,
            description="Test",
            validator=lambda s: True
        )

        # Should be forced to SOFT
        assert constraint.constraint_type == ConstraintType.SOFT

    def test_constraint_violation_creation(self):
        """Test creating constraint violation."""
        constraint = HardConstraint(
            constraint_id="test",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Test constraint",
            validator=lambda s: True
        )

        violation = ConstraintViolation(
            constraint=constraint,
            severity=Decimal("0.8"),
            details="Test violation details"
        )

        assert violation.constraint == constraint
        assert violation.severity == Decimal("0.8")
        assert violation.details == "Test violation details"

    def test_validation_result_auto_summary_valid(self):
        """Test that validation result auto-generates summary for valid result."""
        result = ConstraintValidationResult(
            is_valid=True,
            hard_violations=[],
            soft_violations=[]
        )

        assert "Valid" in result.summary

    def test_validation_result_auto_summary_invalid(self):
        """Test that validation result auto-generates summary for invalid result."""
        constraint = HardConstraint(
            constraint_id="test",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Test",
            validator=lambda s: True
        )

        violation = ConstraintViolation(constraint=constraint)

        result = ConstraintValidationResult(
            is_valid=False,
            hard_violations=[violation],
            soft_violations=[]
        )

        assert "Invalid" in result.summary
        assert "1" in result.summary  # Should mention 1 violation
