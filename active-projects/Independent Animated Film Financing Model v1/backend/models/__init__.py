"""
Animation Finance Model - Data Models

This package contains Pydantic models representing the core entities
in the animation financing ecosystem.
"""

from .financial_instruments import (
    FinancialInstrument,
    Equity,
    SeniorDebt,
    GapDebt,
    MezzanineDebt,
    TaxCreditLoan,
    BridgeFinancing,
    PreSale,
    NegativePickup,
)
from .incentive_policy import (
    IncentivePolicy,
    IncentiveType,
    QPEDefinition,
    MonetizationMethod,
)
from .project_profile import (
    ProjectProfile,
    ProjectType,
    ProductionJurisdiction,
)
from .capital_stack import (
    CapitalStack,
    CapitalComponent,
)
from .waterfall import (
    WaterfallStructure,
    WaterfallNode,
    RecoupmentPriority,
)

__all__ = [
    # Financial Instruments
    "FinancialInstrument",
    "Equity",
    "SeniorDebt",
    "GapDebt",
    "MezzanineDebt",
    "TaxCreditLoan",
    "BridgeFinancing",
    "PreSale",
    "NegativePickup",
    # Incentive Policy
    "IncentivePolicy",
    "IncentiveType",
    "QPEDefinition",
    "MonetizationMethod",
    # Project Profile
    "ProjectProfile",
    "ProjectType",
    "ProductionJurisdiction",
    # Capital Stack
    "CapitalStack",
    "CapitalComponent",
    # Waterfall
    "WaterfallStructure",
    "WaterfallNode",
    "RecoupmentPriority",
]
