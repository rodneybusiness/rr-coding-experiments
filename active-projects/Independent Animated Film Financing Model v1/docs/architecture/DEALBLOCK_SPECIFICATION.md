# DealBlock Specification

**Version:** 1.0
**Status:** Ready for Implementation
**Phase:** 1B

---

## Overview

DealBlock is a composable abstraction representing a discrete financing deal or market commitment. It captures both financial terms AND non-financial provisions (control, rights, constraints) that affect strategic scoring.

---

## Core Schema

```python
from enum import Enum
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field, field_validator

class DealType(str, Enum):
    """Types of deals that can be modeled"""
    # Equity
    EQUITY_INVESTMENT = "equity_investment"
    EQUITY_COPRO = "equity_copro"

    # Debt
    SENIOR_DEBT = "senior_debt"
    GAP_FINANCING = "gap_financing"
    MEZZANINE_DEBT = "mezzanine_debt"
    TAX_CREDIT_LOAN = "tax_credit_loan"

    # Pre-Sales & Distribution
    PRESALE_MG = "presale_mg"
    NEGATIVE_PICKUP = "negative_pickup"
    THEATRICAL_DISTRIBUTION = "theatrical_distribution"
    SALES_AGENT = "sales_agent"

    # Streamer
    STREAMER_LICENSE = "streamer_license"
    STREAMER_ORIGINAL = "streamer_original"
    OUTPUT_DEAL = "output_deal"

    # Soft Money
    GRANT = "grant"
    TAX_INCENTIVE = "tax_incentive"


class DealStatus(str, Enum):
    """Status of the deal"""
    PROSPECTIVE = "prospective"
    IN_NEGOTIATION = "in_negotiation"
    TERM_SHEET = "term_sheet"
    COMMITTED = "committed"
    CLOSED = "closed"
    LAPSED = "lapsed"


class ApprovalRight(str, Enum):
    """Types of approval rights"""
    SCRIPT = "script"
    DIRECTOR = "director"
    CAST = "cast"
    BUDGET = "budget"
    FINAL_CUT = "final_cut"
    MARKETING = "marketing"
    RELEASE_DATE = "release_date"
    TERRITORY_SALES = "territory_sales"


class RightsWindow(str, Enum):
    """Distribution windows"""
    THEATRICAL = "theatrical"
    PVOD = "pvod"
    SVOD = "svod"
    AVOD = "avod"
    EST = "est"
    FREE_TV = "free_tv"
    PAY_TV = "pay_tv"
    ANCILLARY = "ancillary"
    ALL_RIGHTS = "all_rights"


class DealBlock(BaseModel):
    """
    A discrete financing deal with terms affecting both
    financial flows and ownership/control.
    """

    # === IDENTIFICATION ===
    deal_id: str = Field(..., description="Unique identifier")
    deal_name: str = Field(..., description="Human-readable name")
    deal_type: DealType = Field(..., description="Type of deal")
    status: DealStatus = Field(default=DealStatus.PROSPECTIVE)

    # === COUNTERPARTY ===
    counterparty_name: str = Field(..., description="Name of other party")
    counterparty_type: str = Field(
        default="investor",
        description="Type: investor, distributor, streamer, studio, co-producer"
    )

    # === FINANCIAL TERMS ===
    amount: Decimal = Field(..., gt=0, description="Deal value in USD")
    currency: str = Field(default="USD")

    # Payment structure
    payment_schedule: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Milestone -> Amount mapping (e.g., {'signing': 0.10, 'delivery': 0.90})"
    )

    # Recoupment
    recoupment_priority: int = Field(
        default=8,
        ge=1,
        le=15,
        description="Priority in waterfall (1=first, higher=later)"
    )
    is_recoupable: bool = Field(default=True, description="Can this be recouped?")

    # Returns
    interest_rate: Optional[Decimal] = Field(
        default=None, ge=0, le=50,
        description="Annual interest rate % (for debt)"
    )
    premium_percentage: Optional[Decimal] = Field(
        default=None, ge=0, le=100,
        description="Return premium % (for equity)"
    )
    backend_participation_pct: Optional[Decimal] = Field(
        default=None, ge=0, le=100,
        description="Backend profit participation %"
    )

    # Fees
    origination_fee_pct: Optional[Decimal] = Field(default=None, ge=0, le=10)
    distribution_fee_pct: Optional[Decimal] = Field(default=None, ge=0, le=50)
    sales_commission_pct: Optional[Decimal] = Field(default=None, ge=0, le=30)

    # === TERRITORY & RIGHTS ===
    territories: List[str] = Field(
        default_factory=list,
        description="Territories covered (e.g., ['North America', 'UK/Ireland'])"
    )
    is_worldwide: bool = Field(default=False)

    rights_windows: List[RightsWindow] = Field(
        default_factory=list,
        description="Distribution windows included"
    )

    term_years: Optional[int] = Field(
        default=None, ge=1, le=50,
        description="License term duration in years"
    )

    exclusivity: bool = Field(default=True, description="Exclusive rights?")
    holdback_days: Optional[int] = Field(
        default=None,
        description="Days before rights can be exercised"
    )

    # === OWNERSHIP & CONTROL ===
    ownership_percentage: Optional[Decimal] = Field(
        default=None, ge=0, le=100,
        description="Equity ownership % (for equity deals)"
    )

    # Approval rights granted to counterparty
    approval_rights_granted: List[ApprovalRight] = Field(
        default_factory=list,
        description="What approvals counterparty has"
    )

    # Control provisions
    has_board_seat: bool = Field(default=False)
    has_veto_rights: bool = Field(default=False)
    veto_scope: Optional[str] = Field(default=None)

    # IP ownership
    ip_ownership: str = Field(
        default="producer",
        description="Who owns IP: 'producer', 'counterparty', 'shared'"
    )

    # === SPECIAL PROVISIONS ===
    mfn_clause: bool = Field(
        default=False,
        description="Most Favored Nations clause present?"
    )
    mfn_scope: Optional[str] = Field(default=None)

    reversion_trigger_years: Optional[int] = Field(
        default=None,
        description="Years until rights revert"
    )
    reversion_trigger_condition: Optional[str] = Field(
        default=None,
        description="Condition for reversion (e.g., 'if_not_distributed')"
    )

    sequel_rights_holder: Optional[str] = Field(
        default=None,
        description="Who holds sequel/derivative rights"
    )
    sequel_participation_pct: Optional[Decimal] = Field(
        default=None,
        description="Passive payment % if not involved in sequel"
    )

    cross_collateralized: bool = Field(
        default=False,
        description="Cross-collateralized with other properties?"
    )
    cross_collateral_scope: Optional[str] = Field(default=None)

    # === EXECUTION ===
    probability_of_closing: Decimal = Field(
        default=Decimal("75"),
        ge=0, le=100,
        description="Probability this deal closes %"
    )

    complexity_score: int = Field(
        default=5,
        ge=1, le=10,
        description="Deal complexity (1=simple, 10=very complex)"
    )

    # === DATES ===
    created_date: date = Field(default_factory=date.today)
    expected_close_date: Optional[date] = None

    # === NOTES ===
    notes: Optional[str] = Field(default=None, max_length=2000)

    # === VALIDATORS ===
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator('territories')
    @classmethod
    def validate_territories(cls, v: List[str], info) -> List[str]:
        # If worldwide, territories should be empty or ["Worldwide"]
        return v

    # === COMPUTED PROPERTIES ===
    def net_amount_after_fees(self) -> Decimal:
        """Calculate net amount after commissions/fees"""
        total_fee_pct = Decimal("0")
        if self.sales_commission_pct:
            total_fee_pct += self.sales_commission_pct
        if self.origination_fee_pct:
            total_fee_pct += self.origination_fee_pct
        return self.amount * (Decimal("100") - total_fee_pct) / Decimal("100")

    def expected_value(self) -> Decimal:
        """Probability-weighted expected value"""
        return self.net_amount_after_fees() * self.probability_of_closing / Decimal("100")

    def control_impact_score(self) -> int:
        """
        Score representing how much control is ceded (0-100).
        Higher = more control lost.
        """
        score = 0

        # Approval rights
        score += len(self.approval_rights_granted) * 10

        # Board/veto
        if self.has_board_seat:
            score += 15
        if self.has_veto_rights:
            score += 20

        # IP ownership
        if self.ip_ownership == "counterparty":
            score += 40
        elif self.ip_ownership == "shared":
            score += 20

        # Sequel rights
        if self.sequel_rights_holder and self.sequel_rights_holder != "producer":
            score += 15

        return min(score, 100)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            "deal_id": self.deal_id,
            "deal_name": self.deal_name,
            "deal_type": self.deal_type.value,
            "status": self.status.value,
            "counterparty_name": self.counterparty_name,
            "amount": str(self.amount),
            "net_amount": str(self.net_amount_after_fees()),
            "expected_value": str(self.expected_value()),
            "control_impact": self.control_impact_score(),
            "territories": self.territories,
            "rights_windows": [w.value for w in self.rights_windows],
            "probability_of_closing": str(self.probability_of_closing),
            # ... other fields
        }

    class Config:
        json_schema_extra = {
            "example": {
                "deal_id": "DEAL-001",
                "deal_name": "North America Theatrical Distribution",
                "deal_type": "theatrical_distribution",
                "status": "committed",
                "counterparty_name": "Major Studios Inc.",
                "amount": "8500000",
                "territories": ["United States", "Canada"],
                "rights_windows": ["theatrical", "pvod"],
                "distribution_fee_pct": "30",
                "probability_of_closing": "90"
            }
        }
```

---

## Deal Type Templates

### Equity Investment
```python
{
    "deal_type": "equity_investment",
    "ownership_percentage": Decimal("25"),
    "premium_percentage": Decimal("20"),
    "backend_participation_pct": Decimal("25"),
    "recoupment_priority": 8,
    "has_board_seat": True,
    "approval_rights_granted": [ApprovalRight.BUDGET],
    "ip_ownership": "producer"
}
```

### Streamer License
```python
{
    "deal_type": "streamer_license",
    "amount": Decimal("6000000"),
    "territories": ["North America"],
    "is_worldwide": False,
    "rights_windows": [RightsWindow.SVOD],
    "term_years": 7,
    "exclusivity": True,
    "holdback_days": 120,  # After theatrical
    "ip_ownership": "producer",
    "approval_rights_granted": [],
    "recoupment_priority": 1  # Upfront payment
}
```

### Streamer Original (Cost-Plus)
```python
{
    "deal_type": "streamer_original",
    "amount": Decimal("30000000"),  # Full budget
    "premium_percentage": Decimal("15"),
    "is_worldwide": True,
    "rights_windows": [RightsWindow.ALL_RIGHTS],
    "term_years": 25,  # Effectively perpetual
    "ip_ownership": "counterparty",  # Platform owns
    "approval_rights_granted": [
        ApprovalRight.SCRIPT,
        ApprovalRight.DIRECTOR,
        ApprovalRight.CAST,
        ApprovalRight.FINAL_CUT
    ],
    "sequel_rights_holder": "counterparty",
    "backend_participation_pct": None  # No backend
}
```

### Pre-Sale MG
```python
{
    "deal_type": "presale_mg",
    "amount": Decimal("3000000"),
    "territories": ["UK", "Ireland"],
    "rights_windows": [RightsWindow.ALL_RIGHTS],
    "term_years": 15,
    "sales_commission_pct": Decimal("15"),
    "payment_schedule": {
        "delivery": Decimal("100")
    },
    "backend_participation_pct": Decimal("50"),  # After MG recoup
    "recoupment_priority": 6,
    "ip_ownership": "producer"
}
```

### Gap Financing
```python
{
    "deal_type": "gap_financing",
    "amount": Decimal("4000000"),
    "interest_rate": Decimal("12"),
    "origination_fee_pct": Decimal("3"),
    "recoupment_priority": 5,
    "is_recoupable": True,
    "approval_rights_granted": [],
    "ip_ownership": "producer"
}
```

---

## Integration Points

### With WaterfallEngine
```python
def to_waterfall_node(self) -> WaterfallNode:
    """Convert DealBlock to waterfall node"""
    return WaterfallNode(
        node_id=f"deal_{self.deal_id}",
        priority=self.recoupment_priority,
        payee_name=self.counterparty_name,
        payee_type=self._map_to_payee_type(),
        amount=self.amount if self.is_recoupable else None,
        percentage=self.backend_participation_pct,
        is_recoupable=self.is_recoupable
    )
```

### With OwnershipControlScorer
```python
def get_control_inputs(self) -> Dict:
    """Extract control-relevant fields for scoring"""
    return {
        "approval_rights": self.approval_rights_granted,
        "has_board_seat": self.has_board_seat,
        "has_veto_rights": self.has_veto_rights,
        "ip_ownership": self.ip_ownership,
        "sequel_rights": self.sequel_rights_holder,
        "mfn_clause": self.mfn_clause,
        "reversion_years": self.reversion_trigger_years
    }
```

---

## API Endpoints

### POST /api/v1/deals/
Create a new DealBlock

### GET /api/v1/deals/{deal_id}
Get DealBlock by ID

### PUT /api/v1/deals/{deal_id}
Update DealBlock

### DELETE /api/v1/deals/{deal_id}
Delete DealBlock

### GET /api/v1/deals/templates
Get available deal templates

### POST /api/v1/deals/analyze
Analyze a DealBlock for waterfall and control impacts

---

## Test Cases Required

1. **Creation**: Valid deal with all required fields
2. **Validation**: Reject invalid amounts, percentages
3. **Calculation**: Net amount, expected value, control score
4. **Templates**: Each deal type template creates valid model
5. **Waterfall mapping**: Correct node generation
6. **Control scoring**: Score matches expected for each deal type

---

## Files to Create

```
backend/models/deal_block.py          # Core model
backend/models/__init__.py            # Export DealBlock
backend/api/app/schemas/deals.py      # API schemas
backend/api/app/api/v1/endpoints/deals.py  # API endpoints
backend/tests/test_deal_block.py      # Unit tests
frontend/lib/api/types.ts             # TypeScript types
frontend/app/dashboard/deals/page.tsx # UI (Phase 1B-IMPL)
```
