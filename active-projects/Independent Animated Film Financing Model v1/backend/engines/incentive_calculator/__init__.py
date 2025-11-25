"""
Engine 1: Enhanced Incentive Calculator

This module provides comprehensive tax incentive calculation capabilities for
multi-jurisdiction film productions, including:
- Policy loading and validation
- Single and multi-jurisdiction calculations
- Stacking logic for combinable incentives
- Cash flow timeline projections
- Monetization strategy comparisons
"""

from .policy_loader import PolicyLoader
from .policy_registry import PolicyRegistry
from .calculator import (
    IncentiveCalculator,
    JurisdictionSpend,
    IncentiveResult,
    MultiJurisdictionResult,
)
from .cash_flow_projector import (
    CashFlowProjector,
    CashFlowEvent,
    CashFlowProjection,
)
from .monetization_comparator import (
    MonetizationComparator,
    MonetizationScenario,
    MonetizationComparison,
)
from .labor_cap_enforcer import (
    LaborCapEnforcer,
    LaborAdjustment,
    LaborEnforcementResult,
)

__all__ = [
    # Core components
    "PolicyLoader",
    "PolicyRegistry",
    "IncentiveCalculator",
    # Data classes
    "JurisdictionSpend",
    "IncentiveResult",
    "MultiJurisdictionResult",
    # Cash flow
    "CashFlowProjector",
    "CashFlowEvent",
    "CashFlowProjection",
    # Monetization
    "MonetizationComparator",
    "MonetizationScenario",
    "MonetizationComparison",
    # Labor cap enforcement
    "LaborCapEnforcer",
    "LaborAdjustment",
    "LaborEnforcementResult",
]

__version__ = "1.0.0"
