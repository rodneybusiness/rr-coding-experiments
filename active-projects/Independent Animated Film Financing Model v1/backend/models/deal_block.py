"""
DealBlock Model

A composable abstraction representing a discrete financing deal with terms
affecting both financial flows and ownership/control.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field, field_validator, ConfigDict


class DealType(str, Enum):
    """Types of financing deals"""
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

    # Fallback
    OTHER = "other"


class DealStatus(str, Enum):
    """Status of the deal in the pipeline"""
    PROSPECTIVE = "prospective"
    IN_NEGOTIATION = "in_negotiation"
    TERM_SHEET = "term_sheet"
    COMMITTED = "committed"
    CLOSED = "closed"
    LAPSED = "lapsed"


class ApprovalRight(str, Enum):
    """Types of approval rights that can be granted to counterparty"""
    SCRIPT = "script"
    DIRECTOR = "director"
    CAST = "cast"
    BUDGET = "budget"
    FINAL_CUT = "final_cut"
    MARKETING = "marketing"
    RELEASE_DATE = "release_date"
    TERRITORY_SALES = "territory_sales"


class RightsWindow(str, Enum):
    """Distribution windows for rights"""
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

    This is the core abstraction for modeling deal structures
    beyond pure financial instruments.
    """

    # === IDENTIFICATION ===
    deal_id: str = Field(..., description="Unique identifier for this deal")
    deal_name: str = Field(..., min_length=1, max_length=200, description="Human-readable name")
    deal_type: DealType = Field(..., description="Type of deal")
    status: DealStatus = Field(default=DealStatus.PROSPECTIVE, description="Current status")

    # === COUNTERPARTY ===
    counterparty_name: str = Field(..., min_length=1, description="Name of other party")
    counterparty_type: str = Field(
        default="investor",
        description="Type: investor, distributor, streamer, studio, co-producer, bank"
    )

    # === FINANCIAL TERMS ===
    amount: Decimal = Field(..., gt=0, description="Deal value in USD")
    currency: str = Field(default="USD", description="Currency code")

    # Payment structure
    payment_schedule: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Milestone -> percentage mapping (e.g., {'signing': 10, 'delivery': 90})"
    )

    # Recoupment
    recoupment_priority: int = Field(
        default=8,
        ge=1,
        le=15,
        description="Priority in waterfall (1=first, higher=later)"
    )
    is_recoupable: bool = Field(default=True, description="Can this amount be recouped?")

    # Returns
    interest_rate: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=50,
        description="Annual interest rate % (for debt instruments)"
    )
    premium_percentage: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
        description="Return premium % (for equity)"
    )
    backend_participation_pct: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
        description="Backend profit participation %"
    )

    # Fees
    origination_fee_pct: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=10,
        description="Origination/closing fee %"
    )
    distribution_fee_pct: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=50,
        description="Distribution fee %"
    )
    sales_commission_pct: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=30,
        description="Sales agent commission %"
    )

    # === TERRITORY & RIGHTS ===
    territories: List[str] = Field(
        default_factory=list,
        description="Territories covered (e.g., ['North America', 'UK/Ireland'])"
    )
    is_worldwide: bool = Field(default=False, description="Covers all territories?")

    rights_windows: List[RightsWindow] = Field(
        default_factory=list,
        description="Distribution windows included"
    )

    term_years: Optional[int] = Field(
        default=None,
        ge=1,
        le=50,
        description="License term duration in years"
    )

    exclusivity: bool = Field(default=True, description="Exclusive rights?")
    holdback_days: Optional[int] = Field(
        default=None,
        ge=0,
        description="Days before rights can be exercised"
    )

    # === OWNERSHIP & CONTROL ===
    ownership_percentage: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
        description="Equity ownership % (for equity deals)"
    )

    # Approval rights granted to counterparty
    approval_rights_granted: List[ApprovalRight] = Field(
        default_factory=list,
        description="What approvals counterparty has"
    )

    # Control provisions
    has_board_seat: bool = Field(default=False, description="Counterparty gets board seat?")
    has_veto_rights: bool = Field(default=False, description="Counterparty has veto rights?")
    veto_scope: Optional[str] = Field(
        default=None,
        max_length=500,
        description="What can be vetoed"
    )

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
    mfn_scope: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Scope of MFN clause"
    )

    reversion_trigger_years: Optional[int] = Field(
        default=None,
        ge=1,
        le=50,
        description="Years until rights revert"
    )
    reversion_trigger_condition: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Condition for reversion (e.g., 'if_not_distributed')"
    )

    sequel_rights_holder: Optional[str] = Field(
        default=None,
        description="Who holds sequel/derivative rights: 'producer', 'counterparty', 'shared'"
    )
    sequel_participation_pct: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
        description="Passive payment % if not involved in sequel"
    )

    cross_collateralized: bool = Field(
        default=False,
        description="Cross-collateralized with other properties?"
    )
    cross_collateral_scope: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Scope of cross-collateralization"
    )

    # === EXECUTION ===
    probability_of_closing: Decimal = Field(
        default=Decimal("75"),
        ge=0,
        le=100,
        description="Probability this deal closes %"
    )

    complexity_score: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Deal complexity (1=simple, 10=very complex)"
    )

    # === DATES ===
    created_date: date = Field(default_factory=date.today)
    expected_close_date: Optional[date] = Field(default=None)

    # === NOTES ===
    notes: Optional[str] = Field(default=None, max_length=2000)

    # === VALIDATORS ===
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Ensure amount is positive"""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator('ip_ownership')
    @classmethod
    def validate_ip_ownership(cls, v: str) -> str:
        """Validate IP ownership value"""
        valid_values = ['producer', 'counterparty', 'shared']
        if v.lower() not in valid_values:
            raise ValueError(f"IP ownership must be one of: {valid_values}")
        return v.lower()

    @field_validator('payment_schedule')
    @classmethod
    def validate_payment_schedule(cls, v: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """Validate payment schedule percentages"""
        if v:
            total = sum(v.values())
            if total > Decimal("100"):
                raise ValueError("Payment schedule percentages cannot exceed 100%")
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
        Higher = more control lost to counterparty.
        """
        score = 0

        # Approval rights (10 points each)
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

    def ownership_impact_score(self) -> int:
        """
        Score representing ownership retained (0-100).
        Higher = more ownership retained by producer.
        """
        score = 100

        # IP ownership
        if self.ip_ownership == "counterparty":
            score -= 50
        elif self.ip_ownership == "shared":
            score -= 25

        # Worldwide rights
        if self.is_worldwide and self.deal_type not in [
            DealType.EQUITY_INVESTMENT,
            DealType.GRANT,
            DealType.TAX_INCENTIVE
        ]:
            score -= 20

        # Territory coverage
        if self.territories and not self.is_worldwide:
            score -= min(len(self.territories) * 3, 15)

        # Long term licenses
        if self.term_years and self.term_years > 10:
            score -= min((self.term_years - 10) * 2, 20)

        # All rights vs specific windows
        if RightsWindow.ALL_RIGHTS in self.rights_windows:
            score -= 15

        return max(score, 0)

    def optionality_score(self) -> int:
        """
        Score representing future flexibility (0-100).
        Higher = more optionality retained.
        """
        score = 100

        # Sequel rights
        if self.sequel_rights_holder and self.sequel_rights_holder != "producer":
            score -= 25

        # MFN clause
        if self.mfn_clause:
            score -= 15

        # Cross-collateralization
        if self.cross_collateralized:
            score -= 10

        # No reversion trigger (bad for long-term)
        if self.term_years and self.term_years > 10 and not self.reversion_trigger_years:
            score -= 10

        # Reversion trigger (good!)
        if self.reversion_trigger_years and self.reversion_trigger_years <= 15:
            score += min(15, 25 - self.reversion_trigger_years)

        return max(0, min(score, 100))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            "deal_id": self.deal_id,
            "deal_name": self.deal_name,
            "deal_type": self.deal_type.value,
            "status": self.status.value,
            "counterparty_name": self.counterparty_name,
            "counterparty_type": self.counterparty_type,
            "amount": str(self.amount),
            "currency": self.currency,
            "payment_schedule": {k: str(v) for k, v in self.payment_schedule.items()},
            "recoupment_priority": self.recoupment_priority,
            "is_recoupable": self.is_recoupable,
            "interest_rate": str(self.interest_rate) if self.interest_rate else None,
            "premium_percentage": str(self.premium_percentage) if self.premium_percentage else None,
            "backend_participation_pct": str(self.backend_participation_pct) if self.backend_participation_pct else None,
            "territories": self.territories,
            "is_worldwide": self.is_worldwide,
            "rights_windows": [w.value for w in self.rights_windows],
            "term_years": self.term_years,
            "exclusivity": self.exclusivity,
            "ownership_percentage": str(self.ownership_percentage) if self.ownership_percentage else None,
            "approval_rights_granted": [a.value for a in self.approval_rights_granted],
            "has_board_seat": self.has_board_seat,
            "has_veto_rights": self.has_veto_rights,
            "ip_ownership": self.ip_ownership,
            "mfn_clause": self.mfn_clause,
            "reversion_trigger_years": self.reversion_trigger_years,
            "sequel_rights_holder": self.sequel_rights_holder,
            "cross_collateralized": self.cross_collateralized,
            "probability_of_closing": str(self.probability_of_closing),
            "complexity_score": self.complexity_score,
            # Computed scores
            "net_amount": str(self.net_amount_after_fees()),
            "expected_value": str(self.expected_value()),
            "control_impact": self.control_impact_score(),
            "ownership_impact": self.ownership_impact_score(),
            "optionality": self.optionality_score(),
            "created_date": self.created_date.isoformat(),
            "expected_close_date": self.expected_close_date.isoformat() if self.expected_close_date else None,
        }

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "deal_id": "DEAL-001",
                "deal_name": "North America Theatrical Distribution",
                "deal_type": "theatrical_distribution",
                "status": "committed",
                "counterparty_name": "Major Studios Inc.",
                "counterparty_type": "distributor",
                "amount": "8500000",
                "territories": ["United States", "Canada"],
                "rights_windows": ["theatrical", "pvod"],
                "distribution_fee_pct": "30",
                "term_years": 15,
                "probability_of_closing": "90",
                "ip_ownership": "producer"
            }
        }
    )


# === DEAL BLOCK TEMPLATES ===

def create_equity_investment_template(
    deal_id: str,
    counterparty_name: str,
    amount: Decimal,
    ownership_percentage: Decimal,
    premium_percentage: Decimal = Decimal("20"),
    backend_participation_pct: Optional[Decimal] = None,
    has_board_seat: bool = True,
) -> DealBlock:
    """Create a standard equity investment deal"""
    return DealBlock(
        deal_id=deal_id,
        deal_name=f"Equity Investment - {counterparty_name}",
        deal_type=DealType.EQUITY_INVESTMENT,
        status=DealStatus.PROSPECTIVE,
        counterparty_name=counterparty_name,
        counterparty_type="investor",
        amount=amount,
        ownership_percentage=ownership_percentage,
        premium_percentage=premium_percentage,
        backend_participation_pct=backend_participation_pct,
        recoupment_priority=8,
        has_board_seat=has_board_seat,
        approval_rights_granted=[ApprovalRight.BUDGET] if has_board_seat else [],
        ip_ownership="producer",
    )


def create_presale_template(
    deal_id: str,
    counterparty_name: str,
    amount: Decimal,
    territories: List[str],
    sales_commission_pct: Decimal = Decimal("15"),
    term_years: int = 15,
) -> DealBlock:
    """Create a standard pre-sale/MG deal"""
    return DealBlock(
        deal_id=deal_id,
        deal_name=f"Pre-Sale - {', '.join(territories[:2])}",
        deal_type=DealType.PRESALE_MG,
        status=DealStatus.PROSPECTIVE,
        counterparty_name=counterparty_name,
        counterparty_type="distributor",
        amount=amount,
        territories=territories,
        rights_windows=[RightsWindow.ALL_RIGHTS],
        term_years=term_years,
        sales_commission_pct=sales_commission_pct,
        payment_schedule={"delivery": Decimal("100")},
        backend_participation_pct=Decimal("50"),
        recoupment_priority=6,
        ip_ownership="producer",
    )


def create_streamer_license_template(
    deal_id: str,
    counterparty_name: str,
    amount: Decimal,
    territories: List[str],
    term_years: int = 7,
    is_worldwide: bool = False,
) -> DealBlock:
    """Create a standard streamer license deal"""
    return DealBlock(
        deal_id=deal_id,
        deal_name=f"Streamer License - {counterparty_name}",
        deal_type=DealType.STREAMER_LICENSE,
        status=DealStatus.PROSPECTIVE,
        counterparty_name=counterparty_name,
        counterparty_type="streamer",
        amount=amount,
        territories=territories,
        is_worldwide=is_worldwide,
        rights_windows=[RightsWindow.SVOD],
        term_years=term_years,
        holdback_days=120,
        recoupment_priority=1,
        is_recoupable=False,
        ip_ownership="producer",
        approval_rights_granted=[],
    )


def create_streamer_original_template(
    deal_id: str,
    counterparty_name: str,
    budget: Decimal,
    premium_percentage: Decimal = Decimal("15"),
) -> DealBlock:
    """Create a streamer original (cost-plus buyout) deal"""
    return DealBlock(
        deal_id=deal_id,
        deal_name=f"Streamer Original - {counterparty_name}",
        deal_type=DealType.STREAMER_ORIGINAL,
        status=DealStatus.PROSPECTIVE,
        counterparty_name=counterparty_name,
        counterparty_type="streamer",
        amount=budget,
        premium_percentage=premium_percentage,
        is_worldwide=True,
        rights_windows=[RightsWindow.ALL_RIGHTS],
        term_years=25,
        recoupment_priority=1,
        is_recoupable=False,
        ip_ownership="counterparty",
        approval_rights_granted=[
            ApprovalRight.SCRIPT,
            ApprovalRight.DIRECTOR,
            ApprovalRight.CAST,
            ApprovalRight.FINAL_CUT,
        ],
        sequel_rights_holder="counterparty",
        complexity_score=7,
    )


def create_gap_financing_template(
    deal_id: str,
    counterparty_name: str,
    amount: Decimal,
    interest_rate: Decimal = Decimal("12"),
    origination_fee_pct: Decimal = Decimal("3"),
) -> DealBlock:
    """Create a gap financing deal"""
    return DealBlock(
        deal_id=deal_id,
        deal_name=f"Gap Financing - {counterparty_name}",
        deal_type=DealType.GAP_FINANCING,
        status=DealStatus.PROSPECTIVE,
        counterparty_name=counterparty_name,
        counterparty_type="bank",
        amount=amount,
        interest_rate=interest_rate,
        origination_fee_pct=origination_fee_pct,
        recoupment_priority=5,
        is_recoupable=True,
        ip_ownership="producer",
        complexity_score=6,
    )
