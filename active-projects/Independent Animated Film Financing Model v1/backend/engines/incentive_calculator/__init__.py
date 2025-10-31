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

from backend.engines.incentive_calculator.policy_loader import PolicyLoader
from backend.engines.incentive_calculator.policy_registry import PolicyRegistry
from backend.engines.incentive_calculator.calculator import (
    IncentiveCalculator,
    JurisdictionSpend,
    IncentiveResult,
    MultiJurisdictionResult,
)
from backend.engines.incentive_calculator.cash_flow_projector import (
    CashFlowProjector,
    CashFlowEvent,
    CashFlowProjection,
)
from backend.engines.incentive_calculator.monetization_comparator import (
    MonetizationComparator,
    MonetizationScenario,
    MonetizationComparison,
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
]

__version__ = "1.0.0"
