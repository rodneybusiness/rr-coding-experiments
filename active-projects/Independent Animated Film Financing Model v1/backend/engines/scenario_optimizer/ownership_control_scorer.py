"""
Ownership & Control Scorer

Evaluates financing scenarios based on strategic metrics beyond financial returns:
ownership retention, creative control, future optionality, and execution complexity.
"""

import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional, Any

from backend.models.deal_block import DealBlock, DealType, ApprovalRight, RightsWindow

logger = logging.getLogger(__name__)


@dataclass
class ControlImpact:
    """Impact of a single clause or provision on strategic scores"""
    source: str  # Which DealBlock or provision
    dimension: str  # ownership, control, optionality, friction
    impact: int  # Positive or negative points
    explanation: str  # Human-readable explanation


@dataclass
class OwnershipControlResult:
    """Complete scoring result with explainability"""

    # Aggregate scores (0-100 scale)
    ownership_score: Decimal
    control_score: Decimal
    optionality_score: Decimal
    friction_score: Decimal

    # Weighted composite score (customizable weights)
    composite_score: Decimal

    # Detailed breakdown for explainability
    impacts: List[ControlImpact] = field(default_factory=list)

    # Per-deal impact breakdown
    deal_impacts: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Actionable recommendations
    recommendations: List[str] = field(default_factory=list)

    # Risk flags for quick identification
    has_mfn_risk: bool = False
    has_control_concentration: bool = False
    has_reversion_opportunity: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary for API responses"""
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
            "deal_impacts": self.deal_impacts,
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

    Scoring Dimensions:
    - Ownership (0-100): How much IP and revenue rights does producer retain?
    - Control (0-100): How much creative and business control is retained?
    - Optionality (0-100): How much future flexibility is preserved?
    - Friction (0-100): How complex and risky is execution? (lower is better)

    Composite score combines all dimensions with configurable weights.
    """

    # Default weights for composite score calculation
    DEFAULT_WEIGHTS = {
        "ownership": Decimal("0.35"),
        "control": Decimal("0.30"),
        "optionality": Decimal("0.20"),
        "friction": Decimal("0.15")  # Inverted: lower friction is better
    }

    # Penalties for specific approval rights granted to counterparties
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

    # IP ownership scores (higher = more retained by producer)
    IP_OWNERSHIP_SCORES = {
        "producer": 100,
        "shared": 50,
        "counterparty": 0,
    }

    # Deal types that don't penalize for worldwide rights
    WORLDWIDE_EXEMPT_DEAL_TYPES = {
        DealType.EQUITY_INVESTMENT,
        DealType.GRANT,
        DealType.TAX_INCENTIVE,
    }

    def __init__(self, weights: Optional[Dict[str, Decimal]] = None):
        """
        Initialize scorer with optional custom weights.

        Args:
            weights: Optional dict with keys ownership, control, optionality, friction.
                     Values should sum to 1.0. Defaults to DEFAULT_WEIGHTS.
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        logger.info("OwnershipControlScorer initialized")

    def score_scenario(
        self,
        deal_blocks: List[DealBlock],
        capital_stack_equity_pct: Optional[Decimal] = None
    ) -> OwnershipControlResult:
        """
        Score a scenario based on its DealBlocks.

        Args:
            deal_blocks: List of DealBlocks in the scenario
            capital_stack_equity_pct: Optional MM equity % for additional context

        Returns:
            OwnershipControlResult with scores, impacts, and recommendations
        """
        logger.info(f"Scoring scenario with {len(deal_blocks)} deal blocks")

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
            ownership_delta, ownership_impacts = self._score_ownership(deal)
            ownership_base += ownership_delta
            impacts.extend(ownership_impacts)
            deal_impact["ownership"] = ownership_delta

            # === CONTROL SCORING ===
            control_delta, control_impacts = self._score_control(deal)
            control_base += control_delta
            impacts.extend(control_impacts)
            deal_impact["control"] = control_delta

            # === OPTIONALITY SCORING ===
            optionality_delta, optionality_impacts = self._score_optionality(deal)
            optionality_base += optionality_delta
            impacts.extend(optionality_impacts)
            deal_impact["optionality"] = optionality_delta

            # === FRICTION SCORING ===
            friction_delta, friction_impacts = self._score_friction(deal)
            friction_base += friction_delta
            impacts.extend(friction_impacts)
            deal_impact["friction"] = friction_delta

            # Store per-deal impacts
            deal_impacts[deal.deal_id] = deal_impact

        # Normalize scores to 0-100 range
        ownership_score = Decimal(str(max(0, min(100, ownership_base))))
        control_score = Decimal(str(max(0, min(100, control_base))))
        optionality_score = Decimal(str(max(0, min(100, optionality_base))))
        friction_score = Decimal(str(max(0, min(100, friction_base))))

        # Calculate weighted composite score
        # Note: Friction is inverted (100 - friction) since lower friction is better
        composite = (
            self.weights["ownership"] * ownership_score +
            self.weights["control"] * control_score +
            self.weights["optionality"] * optionality_score +
            self.weights["friction"] * (Decimal("100") - friction_score)
        )

        # Generate recommendations based on scores
        recommendations = self._generate_recommendations(
            ownership_score, control_score, optionality_score, friction_score,
            deal_blocks
        )

        # Set risk flags
        has_mfn = any(d.mfn_clause for d in deal_blocks)
        has_concentration = any(
            d.ownership_percentage and d.ownership_percentage > Decimal("40")
            for d in deal_blocks
        )
        has_reversion = any(d.reversion_trigger_years for d in deal_blocks)

        result = OwnershipControlResult(
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

        logger.info(
            f"Scenario scored - Ownership: {ownership_score}, Control: {control_score}, "
            f"Optionality: {optionality_score}, Friction: {friction_score}, "
            f"Composite: {composite:.1f}"
        )

        return result

    def _score_ownership(self, deal: DealBlock) -> tuple[int, List[ControlImpact]]:
        """Score ownership dimension for a single deal"""
        delta = 0
        impacts = []

        # IP ownership - major factor
        if deal.ip_ownership != "producer":
            penalty = 100 - self.IP_OWNERSHIP_SCORES.get(deal.ip_ownership, 50)
            delta -= penalty
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="ownership",
                impact=-penalty,
                explanation=f"IP ownership is '{deal.ip_ownership}' (-{penalty})"
            ))

        # Territory coverage (worldwide = more encumbered)
        if deal.is_worldwide and deal.deal_type not in self.WORLDWIDE_EXEMPT_DEAL_TYPES:
            penalty = 20
            delta -= penalty
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="ownership",
                impact=-penalty,
                explanation=f"Worldwide rights granted (-{penalty})"
            ))
        elif deal.territories:
            territory_penalty = min(len(deal.territories) * 3, 15)
            delta -= territory_penalty
            if territory_penalty > 5:
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="ownership",
                    impact=-territory_penalty,
                    explanation=f"{len(deal.territories)} territories licensed (-{territory_penalty})"
                ))

        # Rights windows (more windows = less retained)
        if deal.rights_windows:
            if RightsWindow.ALL_RIGHTS in deal.rights_windows:
                window_penalty = 15
            else:
                window_penalty = min(len(deal.rights_windows) * 3, 12)
            delta -= window_penalty
            if window_penalty > 5:
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="ownership",
                    impact=-window_penalty,
                    explanation=f"{len(deal.rights_windows)} rights windows licensed (-{window_penalty})"
                ))

        # Long term licenses reduce ownership value
        if deal.term_years and deal.term_years > 10:
            term_penalty = min((deal.term_years - 10) * 2, 20)
            delta -= term_penalty
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="ownership",
                impact=-term_penalty,
                explanation=f"Long license term ({deal.term_years} years) (-{term_penalty})"
            ))

        # Ownership percentage ceded
        if deal.ownership_percentage and deal.ownership_percentage > Decimal("0"):
            ownership_penalty = int(deal.ownership_percentage / Decimal("2"))  # 50% ownership = -25 points
            delta -= ownership_penalty
            if ownership_penalty > 10:
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="ownership",
                    impact=-ownership_penalty,
                    explanation=f"{deal.ownership_percentage}% ownership ceded (-{ownership_penalty})"
                ))

        return delta, impacts

    def _score_control(self, deal: DealBlock) -> tuple[int, List[ControlImpact]]:
        """Score control dimension for a single deal"""
        delta = 0
        impacts = []

        # Approval rights - each type has specific penalty
        for approval in deal.approval_rights_granted:
            penalty = self.APPROVAL_PENALTIES.get(approval, 5)
            delta -= penalty
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="control",
                impact=-penalty,
                explanation=f"Counterparty has {approval.value} approval (-{penalty})"
            ))

        # Board seat
        if deal.has_board_seat:
            penalty = 15
            delta -= penalty
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="control",
                impact=-penalty,
                explanation=f"Board seat granted (-{penalty})"
            ))

        # Veto rights
        if deal.has_veto_rights:
            penalty = 20
            delta -= penalty
            scope_desc = deal.veto_scope if deal.veto_scope else "general"
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="control",
                impact=-penalty,
                explanation=f"Veto rights granted: {scope_desc} (-{penalty})"
            ))

        # IP transferred to counterparty implies loss of control
        if deal.ip_ownership == "counterparty":
            penalty = 30
            delta -= penalty
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="control",
                impact=-penalty,
                explanation=f"IP ownership transferred - full control lost (-{penalty})"
            ))

        return delta, impacts

    def _score_optionality(self, deal: DealBlock) -> tuple[int, List[ControlImpact]]:
        """Score optionality dimension for a single deal"""
        delta = 0
        impacts = []

        # Sequel rights - major optionality factor
        if deal.sequel_rights_holder and deal.sequel_rights_holder != "producer":
            penalty = 25
            delta -= penalty
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="optionality",
                impact=-penalty,
                explanation=f"Sequel rights held by {deal.sequel_rights_holder} (-{penalty})"
            ))

        # MFN clause - constrains future deal flexibility
        if deal.mfn_clause:
            penalty = 15
            delta -= penalty
            scope_desc = f" ({deal.mfn_scope})" if deal.mfn_scope else ""
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="optionality",
                impact=-penalty,
                explanation=f"MFN clause present{scope_desc} (-{penalty})"
            ))

        # Reversion trigger - POSITIVE for optionality
        if deal.reversion_trigger_years:
            # Earlier reversion = bigger bonus (up to 15 points for <10 years)
            bonus = max(0, min(15, 25 - deal.reversion_trigger_years))
            if bonus > 0:
                delta += bonus
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="optionality",
                    impact=bonus,
                    explanation=f"Rights revert in {deal.reversion_trigger_years} years (+{bonus})"
                ))

        # Cross-collateralization - reduces flexibility
        if deal.cross_collateralized:
            penalty = 10
            delta -= penalty
            scope_desc = f": {deal.cross_collateral_scope}" if deal.cross_collateral_scope else ""
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="optionality",
                impact=-penalty,
                explanation=f"Cross-collateralized{scope_desc} (-{penalty})"
            ))

        # Exclusivity with long holdbacks
        if deal.exclusivity and deal.holdback_days and deal.holdback_days > 180:
            holdback_penalty = min((deal.holdback_days - 180) // 30, 10)  # ~1 point per month over 6
            if holdback_penalty > 0:
                delta -= holdback_penalty
                impacts.append(ControlImpact(
                    source=deal.deal_name,
                    dimension="optionality",
                    impact=-holdback_penalty,
                    explanation=f"Long holdback period ({deal.holdback_days} days) (-{holdback_penalty})"
                ))

        return delta, impacts

    def _score_friction(self, deal: DealBlock) -> tuple[int, List[ControlImpact]]:
        """Score friction dimension for a single deal (higher = more friction)"""
        delta = 0
        impacts = []

        # Base complexity from deal's own assessment
        complexity_add = deal.complexity_score * 3  # 1-10 scale → 3-30 points
        delta += complexity_add

        # Number of approval rights increases friction
        approval_friction = len(deal.approval_rights_granted) * 2
        if approval_friction > 0:
            delta += approval_friction

        # Board seat adds coordination overhead
        if deal.has_board_seat:
            delta += 5

        # Veto rights create decision bottlenecks
        if deal.has_veto_rights:
            delta += 8

        # MFN clauses require ongoing compliance monitoring
        if deal.mfn_clause:
            delta += 5

        # Cross-collateralization adds accounting complexity
        if deal.cross_collateralized:
            delta += 7

        # Only add impact entry if significant friction
        total_friction = complexity_add + approval_friction
        if total_friction > 15:
            impacts.append(ControlImpact(
                source=deal.deal_name,
                dimension="friction",
                impact=total_friction,
                explanation=f"Deal complexity and approvals add friction (+{total_friction})"
            ))

        return delta, impacts

    def _generate_recommendations(
        self,
        ownership: Decimal,
        control: Decimal,
        optionality: Decimal,
        friction: Decimal,
        deals: List[DealBlock]
    ) -> List[str]:
        """Generate actionable recommendations based on scores"""
        recs = []

        # Low ownership recommendations
        if ownership < Decimal("50"):
            # Find what's driving low ownership
            worldwide_deals = [d for d in deals if d.is_worldwide]
            ip_transferred = [d for d in deals if d.ip_ownership != "producer"]

            if ip_transferred:
                recs.append(
                    f"Ownership score is low ({ownership:.0f}). "
                    f"{len(ip_transferred)} deal(s) involve IP transfer. "
                    "Consider negotiating shared IP or license-only structures."
                )
            elif worldwide_deals:
                recs.append(
                    f"Ownership score is low ({ownership:.0f}). "
                    "Consider retaining more territories or negotiating shorter license terms."
                )
            else:
                recs.append(
                    f"Ownership score is low ({ownership:.0f}). "
                    "Review deal terms for ownership preservation opportunities."
                )

        # Low control recommendations
        if control < Decimal("50"):
            approval_count = sum(len(d.approval_rights_granted) for d in deals)
            veto_deals = [d for d in deals if d.has_veto_rights]

            if veto_deals:
                recs.append(
                    f"Control score is low ({control:.0f}). "
                    f"{len(veto_deals)} deal(s) include veto rights. "
                    "Consider limiting veto scope to material matters only."
                )
            elif approval_count > 5:
                recs.append(
                    f"Control score is low ({control:.0f}). "
                    f"{approval_count} approval rights granted across deals. "
                    "Consider limiting approval rights to budget-only."
                )

        # Low optionality recommendations
        if optionality < Decimal("50"):
            mfn_deals = [d for d in deals if d.mfn_clause]
            sequel_encumbered = [
                d for d in deals
                if d.sequel_rights_holder and d.sequel_rights_holder != "producer"
            ]

            if mfn_deals:
                recs.append(
                    f"Optionality score is low ({optionality:.0f}). "
                    f"{len(mfn_deals)} MFN clause(s) limit future deal flexibility. "
                    "Consider negotiating MFN removal or narrower scope."
                )
            if sequel_encumbered:
                recs.append(
                    f"Sequel rights encumbered in {len(sequel_encumbered)} deal(s). "
                    "This significantly impacts franchise potential. "
                    "Consider first-negotiation or matching rights instead."
                )

        # High friction recommendations
        if friction > Decimal("60"):
            high_complexity_deals = [d for d in deals if d.complexity_score >= 7]
            recs.append(
                f"High execution complexity (friction={friction:.0f}). "
                f"{len(high_complexity_deals)} high-complexity deal(s). "
                "Consider simplifying deal structures or consolidating parties."
            )

        # Positive recommendations (opportunities)
        reversion_deals = [d for d in deals if d.reversion_trigger_years]
        if reversion_deals and optionality >= Decimal("70"):
            shortest_reversion = min(d.reversion_trigger_years for d in reversion_deals)
            recs.append(
                f"Strong optionality with rights reversion in {shortest_reversion} years. "
                "Plan for rights recapture and sequel development."
            )

        return recs

    def compare_scenarios(
        self,
        scenarios: Dict[str, List[DealBlock]]
    ) -> Dict[str, OwnershipControlResult]:
        """
        Compare multiple scenarios.

        Args:
            scenarios: Dict of scenario_name → list of DealBlocks

        Returns:
            Dict of scenario_name → OwnershipControlResult
        """
        results = {}
        for name, deals in scenarios.items():
            results[name] = self.score_scenario(deals)
        return results
