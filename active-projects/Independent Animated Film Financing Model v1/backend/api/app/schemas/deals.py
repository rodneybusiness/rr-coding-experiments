"""
DealBlock API Schemas

Pydantic schemas for DealBlock API requests and responses.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field


class DealBlockInput(BaseModel):
    """Input schema for creating/updating a DealBlock"""

    deal_name: str = Field(..., min_length=1, max_length=200)
    deal_type: str = Field(..., description="Type of deal")
    status: str = Field(default="prospective")

    # Counterparty
    counterparty_name: str = Field(..., min_length=1)
    counterparty_type: str = Field(default="investor")

    # Financial
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD")
    payment_schedule: Optional[Dict[str, Decimal]] = None
    recoupment_priority: int = Field(default=8, ge=1, le=15)
    is_recoupable: bool = Field(default=True)

    # Returns
    interest_rate: Optional[Decimal] = Field(default=None, ge=0, le=50)
    premium_percentage: Optional[Decimal] = Field(default=None, ge=0, le=100)
    backend_participation_pct: Optional[Decimal] = Field(default=None, ge=0, le=100)

    # Fees
    origination_fee_pct: Optional[Decimal] = Field(default=None, ge=0, le=10)
    distribution_fee_pct: Optional[Decimal] = Field(default=None, ge=0, le=50)
    sales_commission_pct: Optional[Decimal] = Field(default=None, ge=0, le=30)

    # Territory & Rights
    territories: List[str] = Field(default_factory=list)
    is_worldwide: bool = Field(default=False)
    rights_windows: List[str] = Field(default_factory=list)
    term_years: Optional[int] = Field(default=None, ge=1, le=50)
    exclusivity: bool = Field(default=True)
    holdback_days: Optional[int] = Field(default=None, ge=0)

    # Ownership & Control
    ownership_percentage: Optional[Decimal] = Field(default=None, ge=0, le=100)
    approval_rights_granted: List[str] = Field(default_factory=list)
    has_board_seat: bool = Field(default=False)
    has_veto_rights: bool = Field(default=False)
    veto_scope: Optional[str] = None
    ip_ownership: str = Field(default="producer")

    # Special Provisions
    mfn_clause: bool = Field(default=False)
    mfn_scope: Optional[str] = None
    reversion_trigger_years: Optional[int] = Field(default=None, ge=1, le=50)
    reversion_trigger_condition: Optional[str] = None
    sequel_rights_holder: Optional[str] = None
    sequel_participation_pct: Optional[Decimal] = Field(default=None, ge=0, le=100)
    cross_collateralized: bool = Field(default=False)
    cross_collateral_scope: Optional[str] = None

    # Execution
    probability_of_closing: Decimal = Field(default=Decimal("75"), ge=0, le=100)
    complexity_score: int = Field(default=5, ge=1, le=10)

    # Dates
    expected_close_date: Optional[date] = None

    # Notes
    notes: Optional[str] = Field(default=None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "deal_name": "North America Theatrical Distribution",
                "deal_type": "theatrical_distribution",
                "counterparty_name": "Major Studios Inc.",
                "counterparty_type": "distributor",
                "amount": "8500000",
                "territories": ["United States", "Canada"],
                "rights_windows": ["theatrical", "pvod"],
                "distribution_fee_pct": "30",
                "term_years": 15,
                "probability_of_closing": "90",
            }
        }


class DealBlockResponse(BaseModel):
    """Response schema for a DealBlock"""

    deal_id: str
    deal_name: str
    deal_type: str
    status: str

    # Counterparty
    counterparty_name: str
    counterparty_type: str

    # Financial
    amount: Decimal
    currency: str
    payment_schedule: Dict[str, Decimal]
    recoupment_priority: int
    is_recoupable: bool

    # Returns
    interest_rate: Optional[Decimal]
    premium_percentage: Optional[Decimal]
    backend_participation_pct: Optional[Decimal]

    # Fees
    origination_fee_pct: Optional[Decimal]
    distribution_fee_pct: Optional[Decimal]
    sales_commission_pct: Optional[Decimal]

    # Territory & Rights
    territories: List[str]
    is_worldwide: bool
    rights_windows: List[str]
    term_years: Optional[int]
    exclusivity: bool
    holdback_days: Optional[int]

    # Ownership & Control
    ownership_percentage: Optional[Decimal]
    approval_rights_granted: List[str]
    has_board_seat: bool
    has_veto_rights: bool
    veto_scope: Optional[str]
    ip_ownership: str

    # Special Provisions
    mfn_clause: bool
    mfn_scope: Optional[str]
    reversion_trigger_years: Optional[int]
    reversion_trigger_condition: Optional[str]
    sequel_rights_holder: Optional[str]
    sequel_participation_pct: Optional[Decimal]
    cross_collateralized: bool
    cross_collateral_scope: Optional[str]

    # Execution
    probability_of_closing: Decimal
    complexity_score: int

    # Dates
    created_date: date
    expected_close_date: Optional[date]

    # Notes
    notes: Optional[str]

    # Computed values
    net_amount: Decimal
    expected_value: Decimal
    control_impact_score: int
    ownership_impact_score: int
    optionality_score: int


class DealBlockListResponse(BaseModel):
    """Response for listing multiple DealBlocks"""

    deals: List[DealBlockResponse]
    total_count: int


class DealBlockCreateRequest(BaseModel):
    """Request to create a new DealBlock"""

    project_id: str = Field(..., description="Project to associate with")
    deal: DealBlockInput


class DealBlockAnalysisRequest(BaseModel):
    """Request to analyze a set of DealBlocks"""

    project_id: str
    deal_blocks: List[DealBlockInput] = Field(..., min_length=1)


class DealBlockAnalysisResponse(BaseModel):
    """Analysis results for DealBlocks"""

    project_id: str
    total_deal_value: Decimal
    total_expected_value: Decimal
    deal_count: int

    # Aggregate scores
    average_control_impact: Decimal
    average_ownership_impact: Decimal
    average_optionality: Decimal
    total_complexity: int

    # Risk flags
    has_mfn_deals: bool
    has_worldwide_rights_deals: bool
    has_ip_transfer_deals: bool

    # Breakdown by type
    deals_by_type: Dict[str, int]
    value_by_type: Dict[str, Decimal]

    # Individual deal summaries
    deal_summaries: List[Dict[str, Any]]


class DealTemplateResponse(BaseModel):
    """Response for deal templates"""

    template_name: str
    deal_type: str
    description: str
    default_values: Dict[str, Any]


class DealTemplatesListResponse(BaseModel):
    """Response listing available templates"""

    templates: List[DealTemplateResponse]
