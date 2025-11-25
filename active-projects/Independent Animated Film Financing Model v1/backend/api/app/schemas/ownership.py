"""
Ownership & Control Scorer API Schemas

Pydantic schemas for ownership/control scoring API requests and responses.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field


class ScoreWeights(BaseModel):
    """Custom weights for scoring dimensions"""
    ownership: Decimal = Field(default=Decimal("0.35"), ge=0, le=1)
    control: Decimal = Field(default=Decimal("0.30"), ge=0, le=1)
    optionality: Decimal = Field(default=Decimal("0.20"), ge=0, le=1)
    friction: Decimal = Field(default=Decimal("0.15"), ge=0, le=1)


class ControlImpactResponse(BaseModel):
    """Response schema for a single control impact"""
    source: str
    dimension: str
    impact: int
    explanation: str


class ScoringFlagsResponse(BaseModel):
    """Response schema for scoring flags"""
    has_mfn_risk: bool
    has_control_concentration: bool
    has_reversion_opportunity: bool


class OwnershipScoreResponse(BaseModel):
    """Response schema for ownership/control scoring"""

    # Dimension scores (0-100)
    ownership_score: Decimal
    control_score: Decimal
    optionality_score: Decimal
    friction_score: Decimal

    # Weighted composite
    composite_score: Decimal

    # Detailed impacts for explainability
    impacts: List[ControlImpactResponse]

    # Per-deal breakdown
    deal_impacts: Dict[str, Dict[str, int]]

    # Actionable recommendations
    recommendations: List[str]

    # Quick flags
    flags: ScoringFlagsResponse

    class Config:
        json_schema_extra = {
            "example": {
                "ownership_score": "72.0",
                "control_score": "65.0",
                "optionality_score": "80.0",
                "friction_score": "35.0",
                "composite_score": "71.25",
                "impacts": [
                    {
                        "source": "NA Distribution Deal",
                        "dimension": "control",
                        "impact": -15,
                        "explanation": "Counterparty has final_cut approval (-15)"
                    }
                ],
                "deal_impacts": {
                    "DEAL-001": {"ownership": -20, "control": -15, "optionality": 0, "friction": 15}
                },
                "recommendations": [
                    "Control score is low. Consider limiting approval rights."
                ],
                "flags": {
                    "has_mfn_risk": False,
                    "has_control_concentration": False,
                    "has_reversion_opportunity": True
                }
            }
        }


class ScoreDealBlockInput(BaseModel):
    """Input schema for a deal block in scoring request"""

    deal_id: str = Field(..., description="Unique identifier for this deal")
    deal_name: str = Field(..., min_length=1, max_length=200)
    deal_type: str = Field(..., description="Type of deal")
    counterparty_name: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=0)

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
    sequel_rights_holder: Optional[str] = None
    cross_collateralized: bool = Field(default=False)
    cross_collateral_scope: Optional[str] = None

    # Execution
    complexity_score: int = Field(default=5, ge=1, le=10)


class OwnershipScoreRequest(BaseModel):
    """Request schema for scoring deals"""

    deal_blocks: List[ScoreDealBlockInput] = Field(..., min_length=1)
    weights: Optional[ScoreWeights] = None

    class Config:
        json_schema_extra = {
            "example": {
                "deal_blocks": [
                    {
                        "deal_id": "DEAL-001",
                        "deal_name": "North America Theatrical",
                        "deal_type": "theatrical_distribution",
                        "counterparty_name": "Major Studios",
                        "amount": "8500000",
                        "territories": ["United States", "Canada"],
                        "approval_rights_granted": ["marketing"],
                        "term_years": 15
                    }
                ],
                "weights": {
                    "ownership": "0.35",
                    "control": "0.30",
                    "optionality": "0.20",
                    "friction": "0.15"
                }
            }
        }


class ScenarioComparisonRequest(BaseModel):
    """Request to compare multiple scenarios"""

    scenarios: Dict[str, List[ScoreDealBlockInput]] = Field(
        ...,
        description="Dict of scenario_name → list of deal blocks"
    )
    weights: Optional[ScoreWeights] = None


class ScenarioComparisonResponse(BaseModel):
    """Response comparing multiple scenarios"""

    results: Dict[str, OwnershipScoreResponse]
    best_composite: str = Field(..., description="Name of scenario with best composite score")
    best_ownership: str = Field(..., description="Name of scenario with best ownership score")
    best_control: str = Field(..., description="Name of scenario with best control score")
    best_optionality: str = Field(..., description="Name of scenario with best optionality score")
    lowest_friction: str = Field(..., description="Name of scenario with lowest friction")
