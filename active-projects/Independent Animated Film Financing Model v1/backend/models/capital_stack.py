"""
Capital Stack Models - The complete financing structure

This module defines how the various financial instruments combine
to form the complete capital stack for a project.
"""

from decimal import Decimal
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .financial_instruments import FinancialInstrument, InstrumentType


class CapitalComponent(BaseModel):
    """A component of the capital stack"""

    component_id: str = Field(default_factory=lambda: f"COMP-{id(object())}", description="Auto-generated component ID")
    instrument: FinancialInstrument
    position: int = Field(..., description="Position in stack (1=senior)")

    # Status
    is_committed: bool = Field(default=False)
    is_closed: bool = Field(default=False)

    # Conditions
    conditions_precedent: Optional[List[str]] = Field(default=None, description="CPs for funding")

    notes: Optional[str] = None


class CapitalStack(BaseModel):
    """Complete capital stack for a project"""

    stack_id: str = Field(default_factory=lambda: f"STACK-{id(object())}", description="Unique identifier for this capital structure")
    project_id: str = Field(default="", description="Reference to ProjectProfile")

    # Engine 3 compatibility fields
    stack_name: str = Field(default="Unnamed Stack", description="Human-readable name")
    project_budget: Decimal = Field(default=Decimal("0"), gt=0, description="Total project budget")

    # Components
    components: List[CapitalComponent] = Field(..., min_length=1)

    # Ancillary costs
    completion_bond_fee_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=10)
    completion_bond_fee_amount: Optional[Decimal] = None

    legal_fees: Decimal = Field(default=Decimal("0"), ge=0)
    audit_fees: Decimal = Field(default=Decimal("0"), ge=0)
    cama_fees: Decimal = Field(default=Decimal("0"), ge=0)

    # Status
    is_fully_financed: bool = Field(default=False)
    financing_gap: Decimal = Field(default=Decimal("0"), ge=0, description="Remaining amount to close")

    notes: Optional[str] = None

    @field_validator('components')
    @classmethod
    def validate_unique_positions(cls, components: List[CapitalComponent]) -> List[CapitalComponent]:
        """Ensure no duplicate positions"""
        positions = [c.position for c in components]
        if len(positions) != len(set(positions)):
            raise ValueError("Duplicate position numbers in capital stack")
        return components

    def total_capital_raised(self) -> Decimal:
        """Calculate total capital from all components"""
        return sum(component.instrument.amount for component in self.components)

    def total_debt(self) -> Decimal:
        """Calculate total debt capital"""
        debt_types = {
            InstrumentType.SENIOR_DEBT,
            InstrumentType.GAP_DEBT,
            InstrumentType.MEZZANINE_DEBT,
            InstrumentType.TAX_CREDIT_LOAN,
            InstrumentType.BRIDGE_FINANCING
        }
        return sum(
            component.instrument.amount
            for component in self.components
            if component.instrument.instrument_type in debt_types
        )

    def total_equity(self) -> Decimal:
        """Calculate total equity capital"""
        return sum(
            component.instrument.amount
            for component in self.components
            if component.instrument.instrument_type == InstrumentType.EQUITY
        )

    def total_soft_money(self) -> Decimal:
        """Calculate total soft money (grants, subsidies)"""
        soft_money_types = {InstrumentType.GRANT, InstrumentType.SUBSIDY}
        return sum(
            component.instrument.amount
            for component in self.components
            if component.instrument.instrument_type in soft_money_types
        )

    def total_pre_sales(self) -> Decimal:
        """Calculate total pre-sales / MGs"""
        pre_sale_types = {InstrumentType.PRE_SALE, InstrumentType.NEGATIVE_PICKUP}
        return sum(
            component.instrument.amount
            for component in self.components
            if component.instrument.instrument_type in pre_sale_types
        )

    def debt_to_equity_ratio(self) -> Optional[Decimal]:
        """Calculate debt-to-equity ratio"""
        equity = self.total_equity()
        if equity == 0:
            return None
        return self.total_debt() / equity

    def get_component_by_type(self, instrument_type: InstrumentType) -> List[CapitalComponent]:
        """Get all components of a specific type"""
        return [c for c in self.components if c.instrument.instrument_type == instrument_type]

    def get_senior_components(self) -> List[CapitalComponent]:
        """Get components in senior positions (typically position 1-3)"""
        return [c for c in self.components if c.position <= 3]

    def stack_summary(self) -> Dict[str, Decimal]:
        """Get a summary of the capital stack composition"""
        return {
            "total_capital": self.total_capital_raised(),
            "total_debt": self.total_debt(),
            "total_equity": self.total_equity(),
            "total_soft_money": self.total_soft_money(),
            "total_pre_sales": self.total_pre_sales(),
            "debt_to_equity_ratio": self.debt_to_equity_ratio() or Decimal("0"),
            "financing_gap": self.financing_gap,
            "debt_percentage": (self.total_debt() / self.total_capital_raised() * 100) if self.total_capital_raised() > 0 else Decimal("0"),
            "equity_percentage": (self.total_equity() / self.total_capital_raised() * 100) if self.total_capital_raised() > 0 else Decimal("0"),
        }

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stack_id": "STACK-001",
                "project_id": "PROJ-001",
                "components": [
                    {
                        "component_id": "COMP-001",
                        "position": 1,
                        "is_committed": True,
                        "instrument": {
                            "instrument_id": "INS-001",
                            "instrument_type": "equity",
                            "amount": "5000000"
                        }
                    }
                ],
                "completion_bond_fee_percentage": "3.5",
                "is_fully_financed": False,
                "financing_gap": "2000000"
            }
        }
    )
