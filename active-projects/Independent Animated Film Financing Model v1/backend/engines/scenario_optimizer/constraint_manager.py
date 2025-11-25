"""
Constraint Manager

Manages and validates hard and soft constraints for capital stack scenarios.
Hard constraints must be satisfied; soft constraints are preferences.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from decimal import Decimal
from enum import Enum

from models.capital_stack import CapitalStack
from models.financial_instruments import Equity, Debt

logger = logging.getLogger(__name__)


class ConstraintType(Enum):
    """Type of constraint."""
    HARD = "hard"  # Must be satisfied
    SOFT = "soft"  # Preference, not required


class ConstraintCategory(Enum):
    """Category of constraint."""
    FINANCIAL = "financial"
    OWNERSHIP = "ownership"
    RISK = "risk"
    TIMING = "timing"
    STRATEGIC = "strategic"


@dataclass
class Constraint:
    """
    Base constraint definition.

    Attributes:
        constraint_id: Unique identifier
        constraint_type: Hard or soft
        category: Constraint category
        description: Human-readable description
        validator: Function that validates the constraint
        penalty_weight: Weight for soft constraint violations (0-1)
        metadata: Additional constraint data
    """
    constraint_id: str
    constraint_type: ConstraintType
    category: ConstraintCategory
    description: str
    validator: Callable[[CapitalStack], bool]
    penalty_weight: Decimal = Decimal("1.0")  # For soft constraints
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self, capital_stack: CapitalStack) -> bool:
        """
        Validate constraint against capital stack.

        Args:
            capital_stack: CapitalStack to validate

        Returns:
            True if constraint satisfied
        """
        try:
            return self.validator(capital_stack)
        except Exception as e:
            logger.error(f"Error validating constraint '{self.constraint_id}': {e}")
            return False


@dataclass
class HardConstraint(Constraint):
    """
    Hard constraint that MUST be satisfied.

    Scenarios violating hard constraints are invalid.
    """

    def __post_init__(self):
        """Ensure constraint type is HARD."""
        self.constraint_type = ConstraintType.HARD


@dataclass
class SoftConstraint(Constraint):
    """
    Soft constraint representing a preference.

    Violations incur penalties in optimization scoring.
    """

    def __post_init__(self):
        """Ensure constraint type is SOFT."""
        self.constraint_type = ConstraintType.SOFT


@dataclass
class ConstraintViolation:
    """
    Record of a constraint violation.

    Attributes:
        constraint: Violated constraint
        severity: How badly violated (for soft constraints)
        details: Additional violation details
    """
    constraint: Constraint
    severity: Decimal = Decimal("1.0")  # 0-1 scale
    details: str = ""


@dataclass
class ConstraintValidationResult:
    """
    Result of constraint validation.

    Attributes:
        is_valid: True if all hard constraints satisfied
        hard_violations: List of hard constraint violations
        soft_violations: List of soft constraint violations
        total_penalty: Sum of soft constraint penalties
        summary: Human-readable summary
    """
    is_valid: bool
    hard_violations: List[ConstraintViolation] = field(default_factory=list)
    soft_violations: List[ConstraintViolation] = field(default_factory=list)
    total_penalty: Decimal = Decimal("0")
    summary: str = ""

    def __post_init__(self):
        """Generate summary."""
        if not self.summary:
            if self.is_valid:
                self.summary = f"Valid scenario. {len(self.soft_violations)} soft constraint violations."
            else:
                self.summary = f"Invalid scenario. {len(self.hard_violations)} hard constraint violations."


class ConstraintManager:
    """
    Manage and validate constraints for capital stack scenarios.

    Supports hard constraints (must satisfy) and soft constraints (preferences).
    """

    def __init__(self):
        """Initialize constraint manager."""
        self.constraints: Dict[str, Constraint] = {}
        self._hard_constraints: List[str] = []
        self._soft_constraints: List[str] = []

        # Load default constraints
        self._load_default_constraints()

        logger.info(f"ConstraintManager initialized with {len(self.constraints)} default constraints")

    def add_constraint(self, constraint: Constraint):
        """
        Add constraint to manager.

        Args:
            constraint: Constraint to add
        """
        self.constraints[constraint.constraint_id] = constraint

        if constraint.constraint_type == ConstraintType.HARD:
            self._hard_constraints.append(constraint.constraint_id)
        else:
            self._soft_constraints.append(constraint.constraint_id)

        logger.info(f"Added {constraint.constraint_type.value} constraint '{constraint.constraint_id}'")

    def remove_constraint(self, constraint_id: str):
        """Remove constraint by ID."""
        if constraint_id in self.constraints:
            constraint = self.constraints[constraint_id]
            del self.constraints[constraint_id]

            if constraint_id in self._hard_constraints:
                self._hard_constraints.remove(constraint_id)
            if constraint_id in self._soft_constraints:
                self._soft_constraints.remove(constraint_id)

            logger.info(f"Removed constraint '{constraint_id}'")

    def validate(self, capital_stack: CapitalStack) -> ConstraintValidationResult:
        """
        Validate capital stack against all constraints.

        Args:
            capital_stack: CapitalStack to validate

        Returns:
            ConstraintValidationResult with violations
        """
        hard_violations = []
        soft_violations = []
        total_penalty = Decimal("0")

        # Check hard constraints
        for constraint_id in self._hard_constraints:
            constraint = self.constraints[constraint_id]
            if not constraint.validate(capital_stack):
                violation = ConstraintViolation(
                    constraint=constraint,
                    severity=Decimal("1.0"),
                    details=f"Hard constraint '{constraint.description}' violated"
                )
                hard_violations.append(violation)

        # Check soft constraints
        for constraint_id in self._soft_constraints:
            constraint = self.constraints[constraint_id]
            if not constraint.validate(capital_stack):
                # Calculate severity based on how badly violated
                severity = self._calculate_soft_violation_severity(capital_stack, constraint)

                violation = ConstraintViolation(
                    constraint=constraint,
                    severity=severity,
                    details=f"Soft constraint '{constraint.description}' violated"
                )
                soft_violations.append(violation)

                # Add penalty
                total_penalty += constraint.penalty_weight * severity

        # Valid if no hard violations
        is_valid = len(hard_violations) == 0

        result = ConstraintValidationResult(
            is_valid=is_valid,
            hard_violations=hard_violations,
            soft_violations=soft_violations,
            total_penalty=total_penalty
        )

        logger.info(f"Validation: {'Valid' if is_valid else 'Invalid'}. "
                   f"Hard violations: {len(hard_violations)}, Soft violations: {len(soft_violations)}")

        return result

    def validate_hard_only(self, capital_stack: CapitalStack) -> bool:
        """
        Quick validation of hard constraints only.

        Args:
            capital_stack: CapitalStack to validate

        Returns:
            True if all hard constraints satisfied
        """
        for constraint_id in self._hard_constraints:
            constraint = self.constraints[constraint_id]
            if not constraint.validate(capital_stack):
                return False
        return True

    def get_constraints_by_category(self, category: ConstraintCategory) -> List[Constraint]:
        """Get all constraints in a category."""
        return [c for c in self.constraints.values() if c.category == category]

    def get_hard_constraints(self) -> List[Constraint]:
        """Get all hard constraints."""
        return [self.constraints[cid] for cid in self._hard_constraints]

    def get_soft_constraints(self) -> List[Constraint]:
        """Get all soft constraints."""
        return [self.constraints[cid] for cid in self._soft_constraints]

    def _calculate_soft_violation_severity(
        self,
        capital_stack: CapitalStack,
        constraint: Constraint
    ) -> Decimal:
        """
        Calculate how badly a soft constraint is violated.

        Args:
            capital_stack: CapitalStack being validated
            constraint: Soft constraint that was violated

        Returns:
            Severity from 0 (barely violated) to 1 (severely violated)
        """
        # Default severity
        severity = Decimal("0.5")

        # Use metadata to calculate more precise severity
        if "target_value" in constraint.metadata and "tolerance" in constraint.metadata:
            # Calculate how far from target
            # This would need actual value extraction logic based on constraint type
            pass

        return severity

    def _load_default_constraints(self):
        """Load standard default constraints."""

        # Hard Constraint 1: Minimum Equity Percentage
        def min_equity_validator(stack: CapitalStack) -> bool:
            equity_total = sum(
                c.instrument.amount for c in stack.components
                if isinstance(c.instrument, Equity)
            )
            equity_pct = (equity_total / stack.project_budget) * Decimal("100")
            return equity_pct >= Decimal("15.0")  # Min 15% equity

        self.add_constraint(HardConstraint(
            constraint_id="min_equity_15pct",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Minimum 15% equity financing",
            validator=min_equity_validator,
            metadata={"min_percentage": Decimal("15.0")}
        ))

        # Hard Constraint 2: Maximum Debt Ratio
        def max_debt_ratio_validator(stack: CapitalStack) -> bool:
            debt_total = sum(
                c.instrument.amount for c in stack.components
                if isinstance(c.instrument, Debt)
            )
            debt_ratio = debt_total / stack.project_budget
            return debt_ratio <= Decimal("0.75")  # Max 75% debt

        self.add_constraint(HardConstraint(
            constraint_id="max_debt_ratio_75pct",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Maximum 75% debt ratio",
            validator=max_debt_ratio_validator,
            metadata={"max_ratio": Decimal("0.75")}
        ))

        # Hard Constraint 3: Budget Must Sum to Total
        def budget_sum_validator(stack: CapitalStack) -> bool:
            component_sum = sum(c.instrument.amount for c in stack.components)
            # Allow 1% tolerance for rounding
            tolerance = stack.project_budget * Decimal("0.01")
            return abs(component_sum - stack.project_budget) <= tolerance

        self.add_constraint(HardConstraint(
            constraint_id="budget_sum_matches",
            constraint_type=ConstraintType.HARD,
            category=ConstraintCategory.FINANCIAL,
            description="Component amounts must sum to project budget",
            validator=budget_sum_validator
        ))

        # Soft Constraint 1: Target IRR
        def target_irr_validator(stack: CapitalStack) -> bool:
            # This would require running waterfall simulation
            # For now, simple heuristic based on debt/equity mix
            equity_total = sum(
                c.instrument.amount for c in stack.components
                if isinstance(c.instrument, Equity)
            )
            equity_pct = (equity_total / stack.project_budget) * Decimal("100")

            # More equity → likely higher returns needed
            # Soft constraint: prefer structures likely to hit 20% IRR
            return equity_pct <= Decimal("50.0")

        self.add_constraint(SoftConstraint(
            constraint_id="target_irr_20pct",
            constraint_type=ConstraintType.SOFT,
            category=ConstraintCategory.FINANCIAL,
            description="Target 20% IRR for equity investors",
            validator=target_irr_validator,
            penalty_weight=Decimal("0.8"),
            metadata={"target_irr": Decimal("20.0")}
        ))

        # Soft Constraint 2: Minimize Dilution
        def minimize_dilution_validator(stack: CapitalStack) -> bool:
            # Prefer structures where producer retains >50% ownership
            equity_components = [
                c.instrument for c in stack.components
                if isinstance(c.instrument, Equity)
            ]

            if equity_components:
                # Assuming first equity component is producer's
                total_ownership_given = sum(e.ownership_percentage for e in equity_components)
                producer_ownership = Decimal("100.0") - total_ownership_given
                return producer_ownership >= Decimal("50.0")

            return True  # No equity = no dilution issue

        self.add_constraint(SoftConstraint(
            constraint_id="minimize_dilution",
            constraint_type=ConstraintType.SOFT,
            category=ConstraintCategory.OWNERSHIP,
            description="Producer retains majority ownership (>50%)",
            validator=minimize_dilution_validator,
            penalty_weight=Decimal("0.7"),
            metadata={"min_producer_ownership": Decimal("50.0")}
        ))

        # Soft Constraint 3: Maximize Tax Incentives
        def maximize_incentives_validator(stack: CapitalStack) -> bool:
            from models.financial_instruments import TaxIncentive

            incentive_total = sum(
                c.instrument.amount for c in stack.components
                if isinstance(c.instrument, TaxIncentive)
            )
            incentive_pct = (incentive_total / stack.project_budget) * Decimal("100")

            # Prefer >15% from incentives
            return incentive_pct >= Decimal("15.0")

        self.add_constraint(SoftConstraint(
            constraint_id="maximize_incentives",
            constraint_type=ConstraintType.SOFT,
            category=ConstraintCategory.FINANCIAL,
            description="Maximize tax incentives (target >15% of budget)",
            validator=maximize_incentives_validator,
            penalty_weight=Decimal("0.6"),
            metadata={"target_percentage": Decimal("15.0")}
        ))

        # Soft Constraint 4: Balanced Risk
        def balanced_risk_validator(stack: CapitalStack) -> bool:
            # Prefer not too much debt (>60%) or too much equity (>70%)
            debt_total = sum(
                c.instrument.amount for c in stack.components
                if isinstance(c.instrument, Debt)
            )
            equity_total = sum(
                c.instrument.amount for c in stack.components
                if isinstance(c.instrument, Equity)
            )

            debt_pct = (debt_total / stack.project_budget) * Decimal("100")
            equity_pct = (equity_total / stack.project_budget) * Decimal("100")

            return debt_pct <= Decimal("60.0") and equity_pct <= Decimal("70.0")

        self.add_constraint(SoftConstraint(
            constraint_id="balanced_risk",
            constraint_type=ConstraintType.SOFT,
            category=ConstraintCategory.RISK,
            description="Balanced debt/equity split (not too extreme)",
            validator=balanced_risk_validator,
            penalty_weight=Decimal("0.5")
        ))

        logger.info("Loaded default constraints")
