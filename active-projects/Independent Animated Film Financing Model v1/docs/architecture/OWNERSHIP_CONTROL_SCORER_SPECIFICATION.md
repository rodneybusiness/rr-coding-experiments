# OwnershipControlScorer Specification

**Version:** 1.0
**Status:** Ready for Implementation
**Phase:** 1C

---

## Overview

The OwnershipControlScorer is a new engine that evaluates scenarios based on strategic metrics beyond financial returns. It answers: "How much ownership, control, and flexibility does Modern Magic retain?"

---

## Scoring Dimensions

### 1. Ownership Score (0-100)
**Question:** How much of the IP and revenue rights does MM retain?

| Score Range | Interpretation |
|-------------|----------------|
| 90-100 | Full ownership, minimal encumbrances |
| 70-89 | Strong ownership with some territory/window licenses |
| 50-69 | Shared ownership or significant licenses granted |
| 30-49 | Minority position or major rights sold |
| 0-29 | Work-for-hire or full buyout |

### 2. Control Score (0-100)
**Question:** How much creative and business control does MM retain?

| Score Range | Interpretation |
|-------------|----------------|
| 90-100 | Full creative control, no approvals needed |
| 70-89 | Minor approval requirements (budget, marketing) |
| 50-69 | Shared control, some creative approvals |
| 30-49 | Significant control ceded, veto rights granted |
| 0-29 | Minimal control, counterparty has final cut |

### 3. Optionality Score (0-100)
**Question:** How much future flexibility is preserved?

| Score Range | Interpretation |
|-------------|----------------|
| 90-100 | All sequel/derivative rights, no MFN, clean reversions |
| 70-89 | Most options preserved, minor constraints |
| 50-69 | Some sequel rights encumbered, MFN present |
| 30-49 | Significant future constraints |
| 0-29 | Franchise locked up, no optionality |

### 4. Friction Score (0-100)
**Question:** How complex and risky is execution?

| Score Range | Interpretation |
|-------------|----------------|
| 0-20 | Simple deal, minimal approvals |
| 21-40 | Standard complexity |
| 41-60 | Multiple parties, some approvals |
| 61-80 | Complex structure, many stakeholders |
| 81-100 | Very complex, high execution risk |

---

## Core Algorithm

```python
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional
from backend.models.deal_block import DealBlock, ApprovalRight


@dataclass
class ControlImpact:
    """Impact of a single clause or provision"""
    source: str  # Which DealBlock or provision
    dimension: str  # ownership, control, optionality, friction
    impact: int  # Positive or negative points
    explanation: str  # Human-readable explanation


@dataclass
class OwnershipControlResult:
    """Complete scoring result with explainability"""

    # Aggregate scores
    ownership_score: Decimal
    control_score: Decimal
    optionality_score: Decimal
    friction_score: Decimal

    # Weighted composite (customizable weights)
    composite_score: Decimal

    # Detailed breakdown
    impacts: List[ControlImpact] = field(default_factory=list)

    # By deal breakdown
    deal_impacts: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    # Flags
    has_mfn_risk: bool = False
    has_control_concentration: bool = False
    has_reversion_opportunity: bool = False

    def to_dict(self) -> Dict:
        return {
            "ownership_score": float(self.ownership_score),
            "control_score": float(self.control_score),
            "optionality_score": float(self.optionality_score),
            "friction_score": float(self.friction_score),
            "composite_score": float(self.composite_score),
            "impacts": [
                {
                    "source": i.source,
                    "dimension": i.dimension,
                    "impact": i.impact,
                    "explanation": i.explanation
                }
                for i in self.impacts
            ],
            "recommendations": self.recommendations,
            "flags": {
                "has_mfn_risk": self.has_mfn_risk,
                "has_control_concentration": self.has_control_concentration,
                "has_reversion_opportunity": self.has_reversion_opportunity
            }
        }


class OwnershipControlScorer:
    """
    Scores scenarios based on ownership, control, and optionality.
    """

    # Default weights for composite score
    DEFAULT_WEIGHTS = {
        "ownership": Decimal("0.35"),
        "control": Decimal("0.30"),
        "optionality": Decimal("0.20"),
        "friction": Decimal("0.15")  # Inverted: lower friction is better
    }

    # Scoring rules
    APPROVAL_PENALTIES = {
        ApprovalRight.FINAL_CUT: 25,
        ApprovalRight.SCRIPT: 15,
        ApprovalRight.DIRECTOR: 15,
        ApprovalRight.CAST: 10,
        ApprovalRight.BUDGET: 10,
        ApprovalRight.MARKETING: 5,
        ApprovalRight.RELEASE_DATE: 5,
        ApprovalRight.TERRITORY_SALES: 5,
    }

    IP_OWNERSHIP_SCORES = {
        "producer": 100,
        "shared": 50,
        "counterparty": 0,
    }

    def __init__(self, weights: Optional[Dict[str, Decimal]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def score_scenario(
        self,
        deal_blocks: List[DealBlock],
        capital_stack_equity_pct: Optional[Decimal] = None
    ) -> OwnershipControlResult:
        """
        Score a scenario based on its DealBlocks.

        Args:
            deal_blocks: List of DealBlocks in the scenario
            capital_stack_equity_pct: Optional MM equity % for context

        Returns:
            OwnershipControlResult with scores and explainability
        """
        impacts: List[ControlImpact] = []
        deal_impacts: Dict[str, Dict[str, int]] = {}

        # Initialize base scores (start at 100, deduct for encumbrances)
        ownership_base = 100
        control_base = 100
        optionality_base = 100
        friction_base = 0  # Starts at 0, increases with complexity

        # Process each DealBlock
        for deal in deal_blocks:
            deal_impact = {"ownership": 0, "control": 0, "optionality": 0, "friction": 0}

            # === OWNERSHIP SCORING ===

            # IP ownership
            if deal.ip_ownership != "producer":
                penalty = 100 - self.IP_OWNERSHIP_SCORES.get(deal.ip_ownership, 50)
                ownership_base -= penalty
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="ownership",
                    impact=-penalty,
                    explanation=f"IP ownership is '{deal.ip_ownership}' (-{penalty})"
                ))
                deal_impact["ownership"] -= penalty

            # Territory coverage (worldwide = more encumbered)
            if deal.is_worldwide and deal.deal_type not in ["equity_investment", "grant"]:
                penalty = 20
                ownership_base -= penalty
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="ownership",
                    impact=-penalty,
                    explanation=f"Worldwide rights granted (-{penalty})"
                ))
                deal_impact["ownership"] -= penalty
            elif deal.territories:
                territory_penalty = min(len(deal.territories) * 3, 15)
                ownership_base -= territory_penalty
                deal_impact["ownership"] -= territory_penalty

            # Rights windows (more windows = less retained)
            if deal.rights_windows:
                from backend.models.deal_block import RightsWindow
                if RightsWindow.ALL_RIGHTS in deal.rights_windows:
                    window_penalty = 15
                else:
                    window_penalty = min(len(deal.rights_windows) * 3, 12)
                ownership_base -= window_penalty
                deal_impact["ownership"] -= window_penalty

            # Long term licenses reduce ownership value
            if deal.term_years and deal.term_years > 10:
                term_penalty = min((deal.term_years - 10) * 2, 20)
                ownership_base -= term_penalty
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="ownership",
                    impact=-term_penalty,
                    explanation=f"Long license term ({deal.term_years} years) (-{term_penalty})"
                ))
                deal_impact["ownership"] -= term_penalty

            # === CONTROL SCORING ===

            # Approval rights
            for approval in deal.approval_rights_granted:
                penalty = self.APPROVAL_PENALTIES.get(approval, 5)
                control_base -= penalty
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="control",
                    impact=-penalty,
                    explanation=f"Counterparty has {approval.value} approval (-{penalty})"
                ))
                deal_impact["control"] -= penalty

            # Board seat
            if deal.has_board_seat:
                control_base -= 15
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="control",
                    impact=-15,
                    explanation="Board seat granted (-15)"
                ))
                deal_impact["control"] -= 15

            # Veto rights
            if deal.has_veto_rights:
                control_base -= 20
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="control",
                    impact=-20,
                    explanation=f"Veto rights granted: {deal.veto_scope or 'general'} (-20)"
                ))
                deal_impact["control"] -= 20

            # === OPTIONALITY SCORING ===

            # Sequel rights
            if deal.sequel_rights_holder and deal.sequel_rights_holder != "producer":
                penalty = 25
                optionality_base -= penalty
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="optionality",
                    impact=-penalty,
                    explanation=f"Sequel rights held by {deal.sequel_rights_holder} (-{penalty})"
                ))
                deal_impact["optionality"] -= penalty

            # MFN clause
            if deal.mfn_clause:
                penalty = 15
                optionality_base -= penalty
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="optionality",
                    impact=-penalty,
                    explanation=f"MFN clause present (-{penalty})"
                ))
                deal_impact["optionality"] -= penalty

            # Reversion trigger (positive!)
            if deal.reversion_trigger_years:
                bonus = min(15, 25 - deal.reversion_trigger_years)  # Earlier = better
                if bonus > 0:
                    optionality_base += bonus
                    impacts.append(ControlImpact(
                        source=deal.deal_name,
                        dimension="optionality",
                        impact=bonus,
                        explanation=f"Rights revert in {deal.reversion_trigger_years} years (+{bonus})"
                    ))
                    deal_impact["optionality"] += bonus

            # Cross-collateralization
            if deal.cross_collateralized:
                penalty = 10
                optionality_base -= penalty
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="optionality",
                    impact=-penalty,
                    explanation=f"Cross-collateralized with other properties (-{penalty})"
                ))
                deal_impact["optionality"] -= penalty

            # === FRICTION SCORING ===

            # Deal complexity
            friction_base += deal.complexity_score * 3
            deal_impact["friction"] += deal.complexity_score * 3

            # Number of approval rights increases friction
            friction_base += len(deal.approval_rights_granted) * 2
            deal_impact["friction"] += len(deal.approval_rights_granted) * 2

            # Store per-deal impacts
            deal_impacts[deal.deal_id] = deal_impact

        # Normalize scores
        ownership_score = Decimal(str(max(0, min(100, ownership_base))))
        control_score = Decimal(str(max(0, min(100, control_base))))
        optionality_score = Decimal(str(max(0, min(100, optionality_base))))
        friction_score = Decimal(str(max(0, min(100, friction_base))))

        # Calculate composite score
        # Friction is inverted (lower is better)
        composite = (
            self.weights["ownership"] * ownership_score +
            self.weights["control"] * control_score +
            self.weights["optionality"] * optionality_score +
            self.weights["friction"] * (Decimal("100") - friction_score)
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            ownership_score, control_score, optionality_score, friction_score,
            deal_blocks
        )

        # Set flags
        has_mfn = any(d.mfn_clause for d in deal_blocks)
        has_concentration = any(
            d.ownership_percentage and d.ownership_percentage > Decimal("40")
            for d in deal_blocks
        )
        has_reversion = any(d.reversion_trigger_years for d in deal_blocks)

        return OwnershipControlResult(
            ownership_score=ownership_score,
            control_score=control_score,
            optionality_score=optionality_score,
            friction_score=friction_score,
            composite_score=composite,
            impacts=impacts,
            deal_impacts=deal_impacts,
            recommendations=recommendations,
            has_mfn_risk=has_mfn,
            has_control_concentration=has_concentration,
            has_reversion_opportunity=has_reversion
        )

    def _generate_recommendations(
        self,
        ownership: Decimal,
        control: Decimal,
        optionality: Decimal,
        friction: Decimal,
        deals: List[DealBlock]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recs = []

        if ownership < Decimal("50"):
            recs.append(
                "Ownership score is low. Consider retaining more territories "
                "or negotiating shorter license terms."
            )

        if control < Decimal("50"):
            # Find worst offender
            approval_count = sum(len(d.approval_rights_granted) for d in deals)
            recs.append(
                f"Control score is low ({approval_count} approval rights granted). "
                "Consider limiting approval rights to budget only."
            )

        if optionality < Decimal("50"):
            if any(d.mfn_clause for d in deals):
                recs.append(
                    "MFN clause limits future deal flexibility. "
                    "Consider negotiating MFN removal or narrower scope."
                )
            if any(d.sequel_rights_holder != "producer" for d in deals if d.sequel_rights_holder):
                recs.append(
                    "Sequel rights are encumbered. This significantly "
                    "impacts franchise potential."
                )

        if friction > Decimal("60"):
            recs.append(
                f"High execution complexity (friction={friction}). "
                "Consider simplifying deal structure or reducing parties."
            )

        return recs
```

---

## Integration with ScenarioEvaluator

```python
# In scenario_evaluator.py

from backend.engines.scenario_optimizer.ownership_control_scorer import (
    OwnershipControlScorer,
    OwnershipControlResult
)

@dataclass
class ScenarioEvaluation:
    # ... existing fields ...

    # New strategic metrics
    ownership_score: Optional[Decimal] = None
    control_score: Optional[Decimal] = None
    optionality_score: Optional[Decimal] = None
    friction_score: Optional[Decimal] = None
    strategic_composite_score: Optional[Decimal] = None

    # Explainability
    control_impacts: List[Dict] = field(default_factory=list)
    strategic_recommendations: List[str] = field(default_factory=list)


class ScenarioEvaluator:
    def __init__(self):
        # ... existing init ...
        self.control_scorer = OwnershipControlScorer()

    def evaluate_scenario(
        self,
        capital_stack: CapitalStack,
        deal_blocks: List[DealBlock],  # NEW PARAMETER
        revenue_assumptions: RevenueAssumptions,
        # ...
    ) -> ScenarioEvaluation:
        # ... existing financial evaluation ...

        # NEW: Strategic scoring
        if deal_blocks:
            control_result = self.control_scorer.score_scenario(deal_blocks)

            evaluation.ownership_score = control_result.ownership_score
            evaluation.control_score = control_result.control_score
            evaluation.optionality_score = control_result.optionality_score
            evaluation.friction_score = control_result.friction_score
            evaluation.strategic_composite_score = control_result.composite_score
            evaluation.control_impacts = [i.__dict__ for i in control_result.impacts]
            evaluation.strategic_recommendations = control_result.recommendations

        return evaluation
```

---

## API Endpoints

### POST /api/v1/ownership/score
Score a list of DealBlocks

**Request:**
```json
{
    "deal_blocks": [...],
    "weights": {
        "ownership": 0.35,
        "control": 0.30,
        "optionality": 0.20,
        "friction": 0.15
    }
}
```

**Response:**
```json
{
    "ownership_score": 72.5,
    "control_score": 65.0,
    "optionality_score": 80.0,
    "friction_score": 35.0,
    "composite_score": 71.25,
    "impacts": [
        {
            "source": "NA Distribution Deal",
            "dimension": "control",
            "impact": -15,
            "explanation": "Counterparty has final_cut approval (-15)"
        }
    ],
    "recommendations": [
        "Control score is low. Consider limiting approval rights."
    ],
    "flags": {
        "has_mfn_risk": false,
        "has_control_concentration": false,
        "has_reversion_opportunity": true
    }
}
```

---

## Test Cases Required

1. **High Ownership Scenario**: All producer-owned, no worldwide licenses
2. **Low Ownership Scenario**: Streamer original (full buyout)
3. **Mixed Control**: Multiple deals with varying approval rights
4. **MFN Impact**: Verify MFN reduces optionality
5. **Reversion Bonus**: Verify early reversion increases optionality
6. **Friction Calculation**: Complex multi-party deal
7. **Composite Weighting**: Verify weights applied correctly
8. **Recommendations**: Each low score triggers appropriate rec

---

## Files to Create

```
backend/engines/scenario_optimizer/ownership_control_scorer.py  # Core engine
backend/engines/scenario_optimizer/__init__.py                  # Export
backend/api/app/schemas/ownership.py                            # API schemas
backend/api/app/api/v1/endpoints/ownership.py                   # API endpoint
backend/tests/test_ownership_control_scorer.py                  # Tests
frontend/lib/api/types.ts                                       # TypeScript types
frontend/components/ownership-score-display.tsx                 # UI component
```

---

## UI Display Recommendations

### Score Cards
Display all 4 scores as gauge/progress indicators:
- Green: 70-100
- Yellow: 40-69
- Red: 0-39

### Impact Timeline
Show clause-by-clause impacts as a waterfall chart (like financial waterfall but for scores).

### Recommendations Panel
Highlight top 3 recommendations with "Fix" action buttons that suggest deal modifications.
