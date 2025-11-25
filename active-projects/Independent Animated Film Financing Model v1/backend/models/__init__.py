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
from .deal_block import (
    DealBlock,
    DealType,
    DealStatus,
    ApprovalRight,
    RightsWindow,
    create_equity_investment_template,
    create_presale_template,
    create_streamer_license_template,
    create_streamer_original_template,
    create_gap_financing_template,
)
from .capital_program import (
    CapitalProgram,
    CapitalSource,
    CapitalDeployment,
    CapitalProgramConstraints,
    ProgramType,
    ProgramStatus,
    AllocationStatus,
    create_internal_pool,
    create_external_fund,
    create_output_deal,
    create_spv,
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
    # Deal Blocks
    "DealBlock",
    "DealType",
    "DealStatus",
    "ApprovalRight",
    "RightsWindow",
    "create_equity_investment_template",
    "create_presale_template",
    "create_streamer_license_template",
    "create_streamer_original_template",
    "create_gap_financing_template",
    # Capital Programs
    "CapitalProgram",
    "CapitalSource",
    "CapitalDeployment",
    "CapitalProgramConstraints",
    "ProgramType",
    "ProgramStatus",
    "AllocationStatus",
    "create_internal_pool",
    "create_external_fund",
    "create_output_deal",
    "create_spv",
]
