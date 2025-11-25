"""
Tests for OwnershipControlScorer

Comprehensive test coverage for ownership, control, optionality, and friction scoring.
"""

import pytest
from decimal import Decimal
from typing import List

from models.deal_block import (
    DealBlock,
    DealType,
    DealStatus,
    ApprovalRight,
    RightsWindow,
)

from engines.scenario_optimizer.ownership_control_scorer import (
    OwnershipControlScorer,
    OwnershipControlResult,
    ControlImpact,
)


# ============================================================================
# Test Fixtures
# ============================================================================

def create_basic_deal(
    deal_id: str = "DEAL-001",
    deal_name: str = "Test Deal",
    deal_type: DealType = DealType.PRESALE_MG,
    amount: Decimal = Decimal("5000000"),
    **kwargs
) -> DealBlock:
    """Helper to create basic deal blocks for testing"""
    return DealBlock(
        deal_id=deal_id,
        deal_name=deal_name,
        deal_type=deal_type,
        counterparty_name=kwargs.get("counterparty_name", "Test Counterparty"),
        amount=amount,
        **{k: v for k, v in kwargs.items() if k != "counterparty_name"}
    )


# ============================================================================
# Test: High Ownership Scenario
# ============================================================================

class TestHighOwnershipScenario:
    """Test scenarios where producer retains full ownership"""

    def test_producer_owned_single_territory(self):
        """All producer-owned, single territory license"""
        deal = create_basic_deal(
            deal_type=DealType.PRESALE_MG,
            ip_ownership="producer",
            territories=["France"],
            is_worldwide=False,
            term_years=7,
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # High ownership expected (only minor territory penalty)
        assert result.ownership_score >= Decimal("85")
        assert result.control_score == Decimal("100")  # No control ceded

    def test_equity_investment_preserves_ownership(self):
        """Equity investment without IP transfer"""
        deal = create_basic_deal(
            deal_type=DealType.EQUITY_INVESTMENT,
            ip_ownership="producer",
            ownership_percentage=Decimal("20"),
            is_worldwide=True,  # Worldwide OK for equity
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Equity is worldwide-exempt, only small ownership penalty
        assert result.ownership_score >= Decimal("80")


# ============================================================================
# Test: Low Ownership Scenario (Streamer Original / Buyout)
# ============================================================================

class TestLowOwnershipScenario:
    """Test scenarios where ownership is significantly ceded"""

    def test_streamer_original_full_buyout(self):
        """Streamer original with full IP transfer"""
        deal = create_basic_deal(
            deal_type=DealType.STREAMER_ORIGINAL,
            ip_ownership="counterparty",
            is_worldwide=True,
            rights_windows=[RightsWindow.ALL_RIGHTS],
            term_years=25,
            approval_rights_granted=[
                ApprovalRight.FINAL_CUT,
                ApprovalRight.SCRIPT,
                ApprovalRight.DIRECTOR,
                ApprovalRight.CAST,
            ],
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Very low ownership and control expected
        assert result.ownership_score <= Decimal("30")
        assert result.control_score <= Decimal("40")

    def test_ip_transfer_to_counterparty(self):
        """IP transferred to counterparty"""
        deal = create_basic_deal(
            ip_ownership="counterparty",
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Should have significant ownership penalty
        assert result.ownership_score <= Decimal("50")

        # Should also affect control (IP ownership = control loss)
        assert result.control_score <= Decimal("80")


# ============================================================================
# Test: Control Scoring
# ============================================================================

class TestControlScoring:
    """Test control dimension scoring"""

    def test_no_control_ceded(self):
        """No approval rights, no board seats, no veto"""
        deal = create_basic_deal()

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        assert result.control_score == Decimal("100")

    def test_final_cut_approval(self):
        """Final cut approval (highest penalty)"""
        deal = create_basic_deal(
            approval_rights_granted=[ApprovalRight.FINAL_CUT]
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Final cut = -25 points
        assert result.control_score == Decimal("75")

    def test_multiple_approval_rights(self):
        """Multiple approval rights granted"""
        deal = create_basic_deal(
            approval_rights_granted=[
                ApprovalRight.BUDGET,      # -10
                ApprovalRight.MARKETING,   # -5
                ApprovalRight.CAST,        # -10
            ]
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # 100 - 10 - 5 - 10 = 75
        assert result.control_score == Decimal("75")

    def test_board_seat_penalty(self):
        """Board seat granted"""
        deal = create_basic_deal(has_board_seat=True)

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Board seat = -15 points
        assert result.control_score == Decimal("85")

    def test_veto_rights_penalty(self):
        """Veto rights granted"""
        deal = create_basic_deal(
            has_veto_rights=True,
            veto_scope="major business decisions"
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Veto = -20 points
        assert result.control_score == Decimal("80")

    def test_combined_control_penalties(self):
        """Multiple control mechanisms ceded"""
        deal = create_basic_deal(
            approval_rights_granted=[ApprovalRight.FINAL_CUT],  # -25
            has_board_seat=True,  # -15
            has_veto_rights=True,  # -20
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # 100 - 25 - 15 - 20 = 40
        assert result.control_score == Decimal("40")


# ============================================================================
# Test: Optionality Scoring
# ============================================================================

class TestOptionalityScoring:
    """Test optionality dimension scoring"""

    def test_full_optionality_retained(self):
        """No sequel rights, no MFN, no cross-coll"""
        deal = create_basic_deal()

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        assert result.optionality_score == Decimal("100")

    def test_mfn_penalty(self):
        """MFN clause reduces optionality"""
        deal = create_basic_deal(
            mfn_clause=True,
            mfn_scope="all financial terms"
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # MFN = -15 points
        assert result.optionality_score == Decimal("85")
        assert result.has_mfn_risk is True

    def test_sequel_rights_encumbered(self):
        """Sequel rights held by counterparty"""
        deal = create_basic_deal(
            sequel_rights_holder="Counterparty Studio"
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Sequel rights = -25 points
        assert result.optionality_score == Decimal("75")

    def test_reversion_bonus(self):
        """Early reversion trigger increases optionality"""
        deal = create_basic_deal(
            reversion_trigger_years=10  # Bonus = min(15, 25-10) = 15
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Base 100 + 15 bonus = 115, capped at 100
        assert result.optionality_score == Decimal("100")
        assert result.has_reversion_opportunity is True

    def test_late_reversion_smaller_bonus(self):
        """Late reversion trigger gives smaller bonus"""
        deal = create_basic_deal(
            reversion_trigger_years=20  # Bonus = min(15, 25-20) = 5
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Should have some bonus but not max
        # Check that reversion is detected
        assert result.has_reversion_opportunity is True

    def test_cross_collateralization_penalty(self):
        """Cross-coll reduces optionality"""
        deal = create_basic_deal(
            cross_collateralized=True,
            cross_collateral_scope="all studio slate"
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Cross-coll = -10 points
        assert result.optionality_score == Decimal("90")


# ============================================================================
# Test: Friction Scoring
# ============================================================================

class TestFrictionScoring:
    """Test friction dimension scoring"""

    def test_low_complexity_deal(self):
        """Simple deal with low friction"""
        deal = create_basic_deal(complexity_score=2)

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Complexity 2 * 3 = 6
        assert result.friction_score == Decimal("6")

    def test_high_complexity_deal(self):
        """Complex deal with multiple friction sources"""
        deal = create_basic_deal(
            complexity_score=8,  # 8 * 3 = 24
            approval_rights_granted=[
                ApprovalRight.BUDGET,
                ApprovalRight.MARKETING,
                ApprovalRight.CAST,
            ],  # 3 * 2 = 6
            has_board_seat=True,  # +5
            has_veto_rights=True,  # +8
            mfn_clause=True,  # +5
            cross_collateralized=True,  # +7
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Should have significant friction
        expected_min = 24 + 6 + 5 + 8 + 5 + 7  # = 55
        assert result.friction_score >= Decimal(str(expected_min))


# ============================================================================
# Test: Composite Score Calculation
# ============================================================================

class TestCompositeScore:
    """Test weighted composite score calculation"""

    def test_default_weights(self):
        """Composite with default weights"""
        deal = create_basic_deal(complexity_score=1)  # Minimal friction

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # With default weights and near-perfect scores:
        # ownership=~97 * 0.35 + control=100 * 0.30 + optionality=100 * 0.20 + (100-friction) * 0.15
        assert result.composite_score >= Decimal("90")

    def test_custom_weights(self):
        """Composite with custom weights emphasizing ownership"""
        deal = create_basic_deal(
            ip_ownership="counterparty",  # Low ownership
            complexity_score=1,
        )

        # Default weights
        scorer_default = OwnershipControlScorer()
        result_default = scorer_default.score_scenario([deal])

        # Custom weights: ownership = 0.70
        custom_weights = {
            "ownership": Decimal("0.70"),
            "control": Decimal("0.10"),
            "optionality": Decimal("0.10"),
            "friction": Decimal("0.10"),
        }
        scorer_custom = OwnershipControlScorer(weights=custom_weights)
        result_custom = scorer_custom.score_scenario([deal])

        # Custom should have lower composite due to heavier ownership weighting
        assert result_custom.composite_score < result_default.composite_score


# ============================================================================
# Test: Recommendations
# ============================================================================

class TestRecommendations:
    """Test recommendation generation"""

    def test_low_ownership_recommendation(self):
        """Low ownership triggers recommendation"""
        deal = create_basic_deal(
            ip_ownership="counterparty",
            is_worldwide=True,
            term_years=25,
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        assert len(result.recommendations) > 0
        assert any("ownership" in r.lower() for r in result.recommendations)

    def test_low_control_recommendation(self):
        """Low control triggers recommendation"""
        deal = create_basic_deal(
            approval_rights_granted=[
                ApprovalRight.FINAL_CUT,
                ApprovalRight.SCRIPT,
                ApprovalRight.DIRECTOR,
            ],
            has_veto_rights=True,
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        assert any("control" in r.lower() for r in result.recommendations)

    def test_mfn_recommendation(self):
        """MFN clause triggers specific recommendation when optionality is low"""
        # Need optionality < 50 to trigger recommendation
        deal = create_basic_deal(
            mfn_clause=True,  # -15
            sequel_rights_holder="Counterparty",  # -25
            cross_collateralized=True,  # -10
            holdback_days=365,  # Additional penalty
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Optionality should be low enough to trigger recommendation
        assert result.optionality_score < Decimal("60")
        # Should have MFN-specific recommendation
        assert any("mfn" in r.lower() for r in result.recommendations)

    def test_high_friction_recommendation(self):
        """High friction triggers recommendation"""
        # Need friction > 60 to trigger recommendation
        # Multiple deals to accumulate friction
        deals = [
            create_basic_deal(
                deal_id=f"DEAL-{i}",
                complexity_score=10,  # 10 * 3 = 30 per deal
                approval_rights_granted=[
                    ApprovalRight.BUDGET,
                    ApprovalRight.MARKETING,
                    ApprovalRight.CAST,
                    ApprovalRight.DIRECTOR,
                ],
                has_board_seat=True,
                has_veto_rights=True,
                mfn_clause=True,
                cross_collateralized=True,
            )
            for i in range(3)  # Multiple deals to push friction over 60
        ]

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario(deals)

        # Friction should be high enough to trigger recommendation
        assert result.friction_score > Decimal("60")
        assert any("friction" in r.lower() or "complex" in r.lower() for r in result.recommendations)


# ============================================================================
# Test: Explainability (Impact Tracking)
# ============================================================================

class TestExplainability:
    """Test impact tracking and explainability"""

    def test_impacts_captured(self):
        """Impacts are captured for each penalty/bonus"""
        deal = create_basic_deal(
            ip_ownership="counterparty",
            approval_rights_granted=[ApprovalRight.FINAL_CUT],
            mfn_clause=True,
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # Should have multiple impacts recorded
        assert len(result.impacts) >= 3

        # Check impact structure
        for impact in result.impacts:
            assert impact.source is not None
            assert impact.dimension in ["ownership", "control", "optionality", "friction"]
            assert isinstance(impact.impact, int)
            assert impact.explanation is not None

    def test_deal_impacts_tracking(self):
        """Per-deal impact breakdown"""
        deal1 = create_basic_deal(
            deal_id="DEAL-001",
            ip_ownership="producer",
        )
        deal2 = create_basic_deal(
            deal_id="DEAL-002",
            ip_ownership="counterparty",
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal1, deal2])

        assert "DEAL-001" in result.deal_impacts
        assert "DEAL-002" in result.deal_impacts

        # Deal 2 should have worse ownership impact
        assert result.deal_impacts["DEAL-002"]["ownership"] < result.deal_impacts["DEAL-001"]["ownership"]


# ============================================================================
# Test: Multiple Deal Scenarios
# ============================================================================

class TestMultipleDealScenarios:
    """Test scenarios with multiple deals"""

    def test_cumulative_impacts(self):
        """Multiple deals accumulate impacts"""
        deal1 = create_basic_deal(
            deal_id="DEAL-001",
            approval_rights_granted=[ApprovalRight.BUDGET],  # -10 control
        )
        deal2 = create_basic_deal(
            deal_id="DEAL-002",
            approval_rights_granted=[ApprovalRight.MARKETING],  # -5 control
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal1, deal2])

        # Control should be 100 - 10 - 5 = 85
        assert result.control_score == Decimal("85")

    def test_mixed_deal_types(self):
        """Realistic scenario with mixed deal types"""
        deals = [
            create_basic_deal(
                deal_id="EQUITY-001",
                deal_name="Series A Investment",
                deal_type=DealType.EQUITY_INVESTMENT,
                amount=Decimal("15000000"),
                ownership_percentage=Decimal("25"),
                has_board_seat=True,
            ),
            create_basic_deal(
                deal_id="PRESALE-001",
                deal_name="France Theatrical MG",
                deal_type=DealType.PRESALE_MG,
                amount=Decimal("2000000"),
                territories=["France"],
                term_years=10,
            ),
            create_basic_deal(
                deal_id="STREAMER-001",
                deal_name="Netflix SVOD License",
                deal_type=DealType.STREAMER_LICENSE,
                amount=Decimal("8000000"),
                is_worldwide=True,
                rights_windows=[RightsWindow.SVOD],
                term_years=5,
                approval_rights_granted=[ApprovalRight.MARKETING],
            ),
        ]

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario(deals)

        # Should have reasonable scores (not extreme)
        assert Decimal("30") <= result.ownership_score <= Decimal("100")
        assert Decimal("30") <= result.control_score <= Decimal("100")
        assert Decimal("30") <= result.optionality_score <= Decimal("100")

        # Should have some friction from multiple deals
        assert result.friction_score >= Decimal("15")


# ============================================================================
# Test: Scenario Comparison
# ============================================================================

class TestScenarioComparison:
    """Test comparing multiple scenarios"""

    def test_compare_scenarios(self):
        """Compare two different deal structures"""
        scenario_a = [
            create_basic_deal(
                deal_id="A-001",
                ip_ownership="producer",
                complexity_score=3,
            )
        ]
        scenario_b = [
            create_basic_deal(
                deal_id="B-001",
                ip_ownership="counterparty",
                complexity_score=7,
            )
        ]

        scorer = OwnershipControlScorer()
        results = scorer.compare_scenarios({
            "Scenario A": scenario_a,
            "Scenario B": scenario_b,
        })

        assert "Scenario A" in results
        assert "Scenario B" in results

        # Scenario A should score better on ownership
        assert results["Scenario A"].ownership_score > results["Scenario B"].ownership_score

        # Scenario A should have lower friction
        assert results["Scenario A"].friction_score < results["Scenario B"].friction_score


# ============================================================================
# Test: Serialization
# ============================================================================

class TestSerialization:
    """Test result serialization"""

    def test_to_dict(self):
        """Result serializes to dict correctly"""
        deal = create_basic_deal(
            approval_rights_granted=[ApprovalRight.BUDGET],
            mfn_clause=True,
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        result_dict = result.to_dict()

        assert "ownership_score" in result_dict
        assert "control_score" in result_dict
        assert "optionality_score" in result_dict
        assert "friction_score" in result_dict
        assert "composite_score" in result_dict
        assert "impacts" in result_dict
        assert "recommendations" in result_dict
        assert "flags" in result_dict

        # Check flags structure
        assert "has_mfn_risk" in result_dict["flags"]
        assert result_dict["flags"]["has_mfn_risk"] is True

        # Check impacts are serialized
        assert isinstance(result_dict["impacts"], list)
        if result_dict["impacts"]:
            impact = result_dict["impacts"][0]
            assert "source" in impact
            assert "dimension" in impact
            assert "impact" in impact
            assert "explanation" in impact


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_deal_list(self):
        """Empty deal list should return perfect scores"""
        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([])

        # No deals = no encumbrances
        assert result.ownership_score == Decimal("100")
        assert result.control_score == Decimal("100")
        assert result.optionality_score == Decimal("100")
        assert result.friction_score == Decimal("0")

    def test_score_floor(self):
        """Scores should not go below 0"""
        # Create deal with maximum penalties
        deal = create_basic_deal(
            ip_ownership="counterparty",
            is_worldwide=True,
            term_years=50,
            rights_windows=[RightsWindow.ALL_RIGHTS],
            ownership_percentage=Decimal("100"),
            approval_rights_granted=[
                ApprovalRight.FINAL_CUT,
                ApprovalRight.SCRIPT,
                ApprovalRight.DIRECTOR,
                ApprovalRight.CAST,
                ApprovalRight.BUDGET,
                ApprovalRight.MARKETING,
            ],
            has_board_seat=True,
            has_veto_rights=True,
            sequel_rights_holder="Counterparty",
            mfn_clause=True,
            cross_collateralized=True,
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        # All scores should be >= 0
        assert result.ownership_score >= Decimal("0")
        assert result.control_score >= Decimal("0")
        assert result.optionality_score >= Decimal("0")
        assert result.friction_score >= Decimal("0")

    def test_score_ceiling(self):
        """Scores should not exceed 100"""
        # Even with reversion bonus, should cap at 100
        deal = create_basic_deal(
            reversion_trigger_years=5,  # Max bonus
        )

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario([deal])

        assert result.optionality_score <= Decimal("100")

    def test_friction_ceiling(self):
        """Friction should cap at 100"""
        deals = [
            create_basic_deal(
                deal_id=f"DEAL-{i}",
                complexity_score=10,
                approval_rights_granted=[
                    ApprovalRight.FINAL_CUT,
                    ApprovalRight.SCRIPT,
                    ApprovalRight.DIRECTOR,
                ],
                has_board_seat=True,
                has_veto_rights=True,
                mfn_clause=True,
                cross_collateralized=True,
            )
            for i in range(5)  # 5 very complex deals
        ]

        scorer = OwnershipControlScorer()
        result = scorer.score_scenario(deals)

        assert result.friction_score <= Decimal("100")
