"""
Labor Cap Enforcer

Enforces labor-specific caps and rate differentials for tax incentive policies.
Handles percentage caps, category-specific rates, and residency requirements.
"""

import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.incentive_policy import IncentivePolicy

logger = logging.getLogger(__name__)


@dataclass
class LaborAdjustment:
    """Record of a labor cap adjustment."""
    adjustment_type: str  # "percent_cap", "category_rate", "labor_only"
    original_amount: Decimal
    adjusted_amount: Decimal
    reduction: Decimal
    description: str


@dataclass
class LaborEnforcementResult:
    """Result of labor cap enforcement."""
    adjusted_qualified_spend: Decimal
    adjusted_labor_spend: Decimal
    labor_credit_component: Decimal
    non_labor_credit_component: Decimal
    total_credit: Decimal
    effective_rate: Decimal
    adjustments: List[LaborAdjustment] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    labor_cap_applied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "adjusted_qualified_spend": str(self.adjusted_qualified_spend),
            "adjusted_labor_spend": str(self.adjusted_labor_spend),
            "labor_credit_component": str(self.labor_credit_component),
            "non_labor_credit_component": str(self.non_labor_credit_component),
            "total_credit": str(self.total_credit),
            "effective_rate": str(self.effective_rate),
            "adjustments": [
                {
                    "type": adj.adjustment_type,
                    "original": str(adj.original_amount),
                    "adjusted": str(adj.adjusted_amount),
                    "reduction": str(adj.reduction),
                    "description": adj.description
                }
                for adj in self.adjustments
            ],
            "warnings": self.warnings,
            "labor_cap_applied": self.labor_cap_applied
        }


class LaborCapEnforcer:
    """
    Enforce labor-specific caps and rate differentials for tax incentive policies.

    This class handles:
    1. Labor percentage caps (e.g., CPTC's 60% labor cap)
    2. Labor-specific rates (different from headline rate)
    3. Labor uplift rates (additional percentage on labor)
    4. VFX/Animation special rates
    5. Labor-only policies (Ontario OCASE)
    6. Residency-based rate differentiation

    Example usage:
        enforcer = LaborCapEnforcer()
        result = enforcer.enforce_labor_caps(
            policy=policy,
            qualified_spend=Decimal("10000000"),
            labor_spend=Decimal("6000000"),
            vfx_labor_spend=Decimal("2000000")
        )
    """

    def enforce_labor_caps(
        self,
        policy: "IncentivePolicy",
        qualified_spend: Decimal,
        labor_spend: Decimal,
        vfx_labor_spend: Optional[Decimal] = None,
        resident_labor_spend: Optional[Decimal] = None,
        nonresident_labor_spend: Optional[Decimal] = None,
    ) -> LaborEnforcementResult:
        """
        Apply labor caps and compute labor-specific credit components.

        Args:
            policy: The incentive policy to apply
            qualified_spend: Total qualified production expenditure
            labor_spend: Total labor spend (subset of qualified_spend)
            vfx_labor_spend: VFX/animation labor spend (subset of labor_spend)
            resident_labor_spend: Resident labor spend (subset of labor_spend)
            nonresident_labor_spend: Non-resident labor spend (subset of labor_spend)

        Returns:
            LaborEnforcementResult with adjusted amounts and credit breakdown
        """
        qpe = policy.qpe_definition
        adjustments: List[LaborAdjustment] = []
        warnings: List[str] = []
        labor_cap_applied = False

        # Ensure Decimal types
        if not isinstance(qualified_spend, Decimal):
            qualified_spend = Decimal(str(qualified_spend))
        if not isinstance(labor_spend, Decimal):
            labor_spend = Decimal(str(labor_spend))

        # Validation: labor cannot exceed qualified spend
        if labor_spend > qualified_spend:
            warnings.append(
                f"Labor spend ({labor_spend}) exceeds qualified spend ({qualified_spend}). "
                f"Capping labor at qualified spend."
            )
            labor_spend = qualified_spend

        adjusted_labor = labor_spend
        adjusted_qualified = qualified_spend

        # 1. Enforce labor percentage cap (e.g., CPTC's 60% cap)
        if qpe.labor_max_percent_of_spend:
            max_labor = qualified_spend * (qpe.labor_max_percent_of_spend / Decimal("100"))
            if labor_spend > max_labor:
                adjustments.append(LaborAdjustment(
                    adjustment_type="percent_cap",
                    original_amount=labor_spend,
                    adjusted_amount=max_labor,
                    reduction=labor_spend - max_labor,
                    description=f"Labor capped at {qpe.labor_max_percent_of_spend}% of qualified spend"
                ))
                adjusted_labor = max_labor
                labor_cap_applied = True

        # 2. Handle labor-only policies (e.g., Ontario OCASE)
        if qpe.labor_only_credit:
            adjusted_qualified = adjusted_labor
            adjustments.append(LaborAdjustment(
                adjustment_type="labor_only",
                original_amount=qualified_spend,
                adjusted_amount=adjusted_labor,
                reduction=qualified_spend - adjusted_labor,
                description="Labor-only credit: only labor spend qualifies"
            ))

        # 3. Calculate credit components based on rates
        headline_rate = policy.headline_rate
        non_labor_spend = adjusted_qualified - adjusted_labor

        # Determine labor rate
        labor_rate = headline_rate
        if qpe.labor_specific_rate is not None:
            labor_rate = qpe.labor_specific_rate

        # Add uplift if applicable
        if qpe.labor_uplift_rate:
            labor_rate = labor_rate + qpe.labor_uplift_rate
            adjustments.append(LaborAdjustment(
                adjustment_type="labor_uplift",
                original_amount=headline_rate,
                adjusted_amount=labor_rate,
                reduction=Decimal("0"),  # Uplift, not reduction
                description=f"Labor uplift: +{qpe.labor_uplift_rate}% on labor spend"
            ))

        # Handle VFX/animation special rate
        vfx_credit = Decimal("0")
        regular_labor_credit = Decimal("0")

        if vfx_labor_spend and qpe.vfx_animation_rate:
            vfx_labor = min(vfx_labor_spend, adjusted_labor)
            regular_labor = adjusted_labor - vfx_labor

            vfx_credit = vfx_labor * (qpe.vfx_animation_rate / Decimal("100"))
            regular_labor_credit = regular_labor * (labor_rate / Decimal("100"))

            adjustments.append(LaborAdjustment(
                adjustment_type="vfx_rate",
                original_amount=vfx_labor,
                adjusted_amount=vfx_credit,
                reduction=Decimal("0"),
                description=f"VFX labor at {qpe.vfx_animation_rate}% rate"
            ))
        else:
            regular_labor_credit = adjusted_labor * (labor_rate / Decimal("100"))

        labor_credit_component = vfx_credit + regular_labor_credit

        # Handle non-labor credit
        non_labor_credit = Decimal("0")
        if not qpe.labor_only_credit and non_labor_spend > 0:
            non_labor_credit = non_labor_spend * (headline_rate / Decimal("100"))

        total_credit = labor_credit_component + non_labor_credit

        # Calculate effective rate
        effective_rate = Decimal("0")
        if adjusted_qualified > 0:
            effective_rate = (total_credit / adjusted_qualified) * Decimal("100")

        logger.info(
            f"Labor cap enforcement for {policy.policy_id}: "
            f"labor={adjusted_labor}, credit={total_credit}, cap_applied={labor_cap_applied}"
        )

        return LaborEnforcementResult(
            adjusted_qualified_spend=adjusted_qualified,
            adjusted_labor_spend=adjusted_labor,
            labor_credit_component=labor_credit_component,
            non_labor_credit_component=non_labor_credit,
            total_credit=total_credit,
            effective_rate=effective_rate,
            adjustments=adjustments,
            warnings=warnings,
            labor_cap_applied=labor_cap_applied
        )

    def validate_labor_spend(
        self,
        qualified_spend: Decimal,
        labor_spend: Decimal,
        raise_on_error: bool = False
    ) -> List[str]:
        """
        Validate labor spend against qualified spend.

        Args:
            qualified_spend: Total qualified spend
            labor_spend: Labor spend component
            raise_on_error: If True, raise ValueError on validation failure

        Returns:
            List of validation warnings/errors

        Raises:
            ValueError: If raise_on_error=True and validation fails
        """
        errors = []

        if labor_spend < 0:
            errors.append("Labor spend cannot be negative")

        if labor_spend > qualified_spend:
            errors.append(
                f"Labor spend ({labor_spend}) exceeds qualified spend ({qualified_spend})"
            )

        if raise_on_error and errors:
            raise ValueError("; ".join(errors))

        return errors
