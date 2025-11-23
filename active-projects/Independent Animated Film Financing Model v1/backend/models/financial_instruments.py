"""
Financial Instruments - Core data models for financing components

This module defines the various financial instruments used in animation
film financing, including equity, debt, pre-sales, and other structures.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator
from backend.models.waterfall import RecoupmentPriority


class InstrumentType(str, Enum):
    """Types of financial instruments"""
    EQUITY = "equity"
    SENIOR_DEBT = "senior_debt"
    GAP_DEBT = "gap_debt"
    MEZZANINE_DEBT = "mezzanine_debt"
    TAX_CREDIT_LOAN = "tax_credit_loan"
    BRIDGE_FINANCING = "bridge_financing"
    PRE_SALE = "pre_sale"
    NEGATIVE_PICKUP = "negative_pickup"
    GRANT = "grant"
    SUBSIDY = "subsidy"


class FinancialInstrument(BaseModel):
    """Base class for all financial instruments"""

    instrument_id: str = Field(default_factory=lambda: f"INS-{id(object())}", description="Unique identifier for this instrument")
    instrument_type: InstrumentType
    amount: Decimal = Field(..., gt=0, description="Principal amount in USD")
    currency: str = Field(default="USD", description="Currency code (ISO 4217)")

    # Timing
    commitment_date: Optional[date] = None
    funding_date: Optional[date] = None
    maturity_date: Optional[date] = None

    # S-curve: Investment drawdown schedule
    # Maps quarter number (int) to percentage of total amount (0-100)
    # Example: {0: 40, 1: 30, 2: 20, 3: 10} means 40% at quarter 0, 30% at quarter 1, etc.
    drawdown_schedule: Optional[Dict[int, Decimal]] = Field(
        default=None,
        description="S-curve drawdown schedule by quarter. If None, assumes 100% at quarter 0."
    )

    # Metadata
    provider_name: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator('drawdown_schedule')
    @classmethod
    def validate_drawdown_schedule(cls, v: Optional[Dict[int, Decimal]]) -> Optional[Dict[int, Decimal]]:
        if v is None:
            return v

        # Check that all quarters are non-negative
        for quarter, percentage in v.items():
            if quarter < 0:
                raise ValueError("Quarter numbers must be non-negative")
            if percentage < 0 or percentage > 100:
                raise ValueError("Drawdown percentages must be between 0 and 100")

        # Check that percentages sum to 100%
        total_percentage = sum(v.values())
        if abs(total_percentage - Decimal("100")) > Decimal("0.01"):  # Allow for rounding
            raise ValueError(f"Drawdown schedule must sum to 100%, got {total_percentage}%")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "instrument_id": "INS-001",
                "instrument_type": "equity",
                "amount": "5000000.00",
                "currency": "USD",
                "provider_name": "Film Investment Fund LP"
            }
        }


class Equity(FinancialInstrument):
    """Equity investment in the production"""

    instrument_type: InstrumentType = Field(default=InstrumentType.EQUITY, frozen=True)

    ownership_percentage: Decimal = Field(..., ge=0, le=100, description="Ownership % of the SPV")
    premium_percentage: Decimal = Field(default=Decimal("0"), ge=0, description="Expected return premium %")
    recoupment_priority: RecoupmentPriority = Field(default=RecoupmentPriority.EQUITY)

    # Backend participation
    backend_participation_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    backend_definition: Optional[str] = Field(default=None, description="e.g., 'Net Profits', 'Adjusted Gross'")

    # Investor type
    is_active_investor: bool = Field(default=False, description="Active vs. passive investor")

    @field_validator('ownership_percentage', 'backend_participation_percentage')
    @classmethod
    def validate_percentage(cls, v: Decimal) -> Decimal:
        if not (0 <= v <= 100):
            raise ValueError("Percentage must be between 0 and 100")
        return v


class Debt(FinancialInstrument):
    """Base class for debt instruments"""

    # Interest and fees
    interest_rate: Decimal = Field(..., ge=0, description="Annual interest rate %")
    term_months: int = Field(default=24, gt=0, description="Loan term in months")
    origination_fee_percentage: Decimal = Field(default=Decimal("0"), ge=0, description="Upfront fee %")
    commitment_fee_percentage: Decimal = Field(default=Decimal("0"), ge=0, description="Commitment fee %")

    # Security and collateral
    collateral_description: Optional[str] = None
    advance_rate: Decimal = Field(default=Decimal("100"), ge=0, le=100, description="% of collateral value advanced")

    # Amortization
    is_amortizing: bool = Field(default=False)
    balloon_payment: bool = Field(default=True)

    @property
    def total_fees_percentage(self) -> Decimal:
        """Calculate total upfront fees as percentage"""
        return self.origination_fee_percentage + self.commitment_fee_percentage

    @property
    def total_fees_amount(self) -> Decimal:
        """Calculate total upfront fees in dollars"""
        return self.amount * (self.total_fees_percentage / 100)


class SeniorDebt(Debt):
    """Senior secured production loan"""

    instrument_type: InstrumentType = Field(default=InstrumentType.SENIOR_DEBT, frozen=True)
    recoupment_priority: RecoupmentPriority = Field(default=RecoupmentPriority.SENIOR_DEBT)

    # Senior debt specifics
    requires_completion_bond: bool = Field(default=True)
    lender_approval_rights: bool = Field(default=True, description="Budget/script approval")


class GapDebt(Debt):
    """Gap financing against unsold territories"""

    instrument_type: InstrumentType = Field(default=InstrumentType.GAP_DEBT, frozen=True)
    recoupment_priority: RecoupmentPriority = Field(default=RecoupmentPriority.SENIOR_DEBT)

    # Gap-specific
    gap_percentage: Decimal = Field(..., ge=0, le=100, description="% of unsold territory value")
    sales_agent_estimates: Optional[Dict[str, Decimal]] = Field(default=None, description="Territory estimates")

    @field_validator('gap_percentage')
    @classmethod
    def validate_gap_percentage(cls, v: Decimal) -> Decimal:
        if v > 50:
            # Gap financing typically doesn't exceed 50% of estimated value
            raise ValueError("Gap percentage typically should not exceed 50%")
        return v


class MezzanineDebt(Debt):
    """Mezzanine/Supergap financing (higher risk debt)"""

    instrument_type: InstrumentType = Field(default=InstrumentType.MEZZANINE_DEBT, frozen=True)
    recoupment_priority: RecoupmentPriority = Field(default=RecoupmentPriority.MEZZANINE_DEBT)

    # Mezz-specific
    equity_kicker: bool = Field(default=False, description="Equity participation component")
    equity_kicker_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class TaxCreditLoan(Debt):
    """Loan secured by tax credit certification"""

    instrument_type: InstrumentType = Field(default=InstrumentType.TAX_CREDIT_LOAN, frozen=True)
    recoupment_priority: RecoupmentPriority = Field(default=RecoupmentPriority.SENIOR_DEBT)

    # Tax credit specifics
    tax_credit_jurisdiction: str = Field(..., description="e.g., 'UK', 'Ireland', 'Quebec'")
    certified_tax_credit_amount: Decimal = Field(..., gt=0)
    advance_rate: Decimal = Field(default=Decimal("85"), ge=0, le=100, description="% of certified credit advanced")

    # Timing
    expected_certification_date: Optional[date] = None
    expected_cash_receipt_date: Optional[date] = None


class BridgeFinancing(Debt):
    """Short-term bridge loan until main financing closes"""

    instrument_type: InstrumentType = Field(default=InstrumentType.BRIDGE_FINANCING, frozen=True)

    # Bridge-specific
    bridges_to: str = Field(..., description="What this bridges to, e.g., 'Production Loan', 'Tax Credit'")
    term_months: int = Field(..., gt=0, description="Loan term in months")


class PreSale(FinancialInstrument):
    """Pre-sale / Minimum Guarantee from distributor"""

    instrument_type: InstrumentType = Field(default=InstrumentType.PRE_SALE, frozen=True)

    # Pre-sale specifics
    territory: str = Field(..., description="e.g., 'North America', 'UK/Ireland', 'France'")
    rights_description: str = Field(..., description="e.g., 'All Rights', 'Theatrical Only', 'SVOD'")

    # Payment structure
    mg_amount: Decimal = Field(..., gt=0, description="Minimum Guarantee amount")
    payment_on_delivery: Decimal = Field(..., ge=0, description="Amount paid upon delivery")
    payment_schedule: Optional[Dict[str, Decimal]] = Field(default=None, description="Milestone payments")

    # Overage terms
    has_overage: bool = Field(default=True)
    overage_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100, description="% of revenues after MG recoupment")

    # Sales agent
    sales_agent_commission: Decimal = Field(default=Decimal("15"), ge=0, le=40, description="Sales commission %")


class NegativePickup(FinancialInstrument):
    """Negative Pickup deal - commitment to acquire completed film"""

    instrument_type: InstrumentType = Field(default=InstrumentType.NEGATIVE_PICKUP, frozen=True)

    # Negative pickup specifics
    acquiring_entity: str = Field(..., description="Studio/Distributor name")
    pickup_price: Decimal = Field(..., gt=0, description="Agreed purchase price")
    rights_acquired: str = Field(..., description="Rights description")

    # Conditions
    delivery_requirements: Optional[Dict[str, Any]] = Field(default=None, description="Technical delivery specs")
    creative_approvals: bool = Field(default=True, description="Studio approval rights")

    # Use as collateral
    used_as_loan_collateral: bool = Field(default=True)


class Grant(FinancialInstrument):
    """Government or foundation grant (non-dilutive, non-recoupable)"""

    instrument_type: InstrumentType = Field(default=InstrumentType.GRANT, frozen=True)

    # Grant specifics
    jurisdiction: str = Field(..., description="Granting jurisdiction")
    grant_program_name: str = Field(..., description="e.g., 'CNC AIDE', 'Eurimages'")

    # Requirements
    cultural_requirements: Optional[str] = None
    deliverable_requirements: Optional[str] = None

    # Timing
    application_date: Optional[date] = None
    approval_date: Optional[date] = None
    disbursement_schedule: Optional[Dict[str, Decimal]] = None


class GapFinancing(Debt):
    """Gap financing against expected sales (Engine 3 compatible)"""

    instrument_type: InstrumentType = Field(default=InstrumentType.GAP_DEBT, frozen=True)
    recoupment_priority: RecoupmentPriority = Field(default=RecoupmentPriority.SENIOR_DEBT)

    # Gap-specific (Engine 3 attributes)
    minimum_presales_percentage: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=100,
        description="Minimum pre-sales required as %"
    )


class TaxIncentive(FinancialInstrument):
    """Tax incentive/credit (Engine 3 compatible)"""

    instrument_type: InstrumentType = Field(default=InstrumentType.GRANT, frozen=True)  # Use GRANT as closest type

    # Tax incentive specifics
    jurisdiction: str = Field(..., description="Tax jurisdiction (e.g., 'Quebec', 'Ireland')")
    qualified_spend: Decimal = Field(..., gt=0, description="Qualified production spend")
    credit_rate: Decimal = Field(..., gt=0, le=100, description="Tax credit rate %")
    timing_months: int = Field(default=18, gt=0, description="Months until cash receipt")
