"""
DealBlock Model Tests

Comprehensive tests for the DealBlock model and templates.
"""

import pytest
from decimal import Decimal
from datetime import date

import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from models.deal_block import (
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


class TestDealBlockCreation:
    """Test DealBlock creation and validation"""

    def test_valid_basic_deal(self):
        """Test creating a valid basic deal"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test Distribution Deal",
            deal_type=DealType.THEATRICAL_DISTRIBUTION,
            counterparty_name="Test Studio",
            amount=Decimal("5000000"),
        )

        assert deal.deal_id == "DEAL-001"
        assert deal.deal_type == DealType.THEATRICAL_DISTRIBUTION
        assert deal.amount == Decimal("5000000")
        assert deal.status == DealStatus.PROSPECTIVE  # Default

    def test_valid_full_deal(self):
        """Test creating a deal with all fields"""
        deal = DealBlock(
            deal_id="DEAL-002",
            deal_name="Full Deal",
            deal_type=DealType.EQUITY_INVESTMENT,
            status=DealStatus.COMMITTED,
            counterparty_name="Investment Fund LP",
            counterparty_type="investor",
            amount=Decimal("10000000"),
            currency="USD",
            payment_schedule={"signing": Decimal("25"), "closing": Decimal("75")},
            recoupment_priority=8,
            ownership_percentage=Decimal("30"),
            premium_percentage=Decimal("20"),
            backend_participation_pct=Decimal("25"),
            has_board_seat=True,
            approval_rights_granted=[ApprovalRight.BUDGET, ApprovalRight.DIRECTOR],
            ip_ownership="producer",
            probability_of_closing=Decimal("90"),
        )

        assert deal.status == DealStatus.COMMITTED
        assert deal.ownership_percentage == Decimal("30")
        assert len(deal.approval_rights_granted) == 2
        assert deal.has_board_seat is True

    def test_invalid_amount_rejected(self):
        """Test that negative/zero amount is rejected"""
        with pytest.raises(ValueError):
            DealBlock(
                deal_id="DEAL-BAD",
                deal_name="Bad Deal",
                deal_type=DealType.EQUITY_INVESTMENT,
                counterparty_name="Test",
                amount=Decimal("-1000"),
            )

    def test_invalid_ip_ownership_rejected(self):
        """Test that invalid IP ownership value is rejected"""
        with pytest.raises(ValueError, match="IP ownership must be one of"):
            DealBlock(
                deal_id="DEAL-BAD",
                deal_name="Bad Deal",
                deal_type=DealType.EQUITY_INVESTMENT,
                counterparty_name="Test",
                amount=Decimal("1000000"),
                ip_ownership="invalid_value",
            )

    def test_payment_schedule_validation(self):
        """Test payment schedule cannot exceed 100%"""
        with pytest.raises(ValueError, match="cannot exceed 100%"):
            DealBlock(
                deal_id="DEAL-BAD",
                deal_name="Bad Deal",
                deal_type=DealType.EQUITY_INVESTMENT,
                counterparty_name="Test",
                amount=Decimal("1000000"),
                payment_schedule={
                    "signing": Decimal("60"),
                    "delivery": Decimal("60"),
                },
            )


class TestDealBlockCalculations:
    """Test computed properties and calculations"""

    def test_net_amount_no_fees(self):
        """Test net amount with no fees"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("10000000"),
        )

        assert deal.net_amount_after_fees() == Decimal("10000000")

    def test_net_amount_with_commission(self):
        """Test net amount with sales commission"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("10000000"),
            sales_commission_pct=Decimal("15"),
        )

        expected = Decimal("10000000") * Decimal("0.85")
        assert deal.net_amount_after_fees() == expected

    def test_net_amount_with_multiple_fees(self):
        """Test net amount with multiple fees"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.GAP_FINANCING,
            counterparty_name="Test",
            amount=Decimal("10000000"),
            sales_commission_pct=Decimal("10"),
            origination_fee_pct=Decimal("3"),
        )

        # 10% + 3% = 13% fees, so 87% net
        expected = Decimal("10000000") * Decimal("0.87")
        assert deal.net_amount_after_fees() == expected

    def test_expected_value_full_probability(self):
        """Test expected value with 100% probability"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("10000000"),
            probability_of_closing=Decimal("100"),
        )

        assert deal.expected_value() == Decimal("10000000")

    def test_expected_value_partial_probability(self):
        """Test expected value with partial probability"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("10000000"),
            probability_of_closing=Decimal("50"),
        )

        assert deal.expected_value() == Decimal("5000000")


class TestControlImpactScoring:
    """Test control impact score calculations"""

    def test_control_impact_no_control_ceded(self):
        """Test control impact when no control is ceded"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("5000000"),
            ip_ownership="producer",
        )

        assert deal.control_impact_score() == 0

    def test_control_impact_approval_rights(self):
        """Test control impact from approval rights"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.EQUITY_INVESTMENT,
            counterparty_name="Test",
            amount=Decimal("5000000"),
            approval_rights_granted=[
                ApprovalRight.SCRIPT,
                ApprovalRight.DIRECTOR,
            ],
        )

        # 2 approvals * 10 points each = 20
        assert deal.control_impact_score() == 20

    def test_control_impact_board_and_veto(self):
        """Test control impact from board seat and veto"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.EQUITY_INVESTMENT,
            counterparty_name="Test",
            amount=Decimal("5000000"),
            has_board_seat=True,
            has_veto_rights=True,
        )

        # Board: 15 + Veto: 20 = 35
        assert deal.control_impact_score() == 35

    def test_control_impact_ip_transfer(self):
        """Test control impact from IP transfer"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.STREAMER_ORIGINAL,
            counterparty_name="Test",
            amount=Decimal("30000000"),
            ip_ownership="counterparty",
        )

        # IP to counterparty: 40
        assert deal.control_impact_score() == 40

    def test_control_impact_sequel_rights(self):
        """Test control impact from sequel rights transfer"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.STREAMER_ORIGINAL,
            counterparty_name="Test",
            amount=Decimal("30000000"),
            sequel_rights_holder="counterparty",
        )

        # Sequel rights: 15
        assert deal.control_impact_score() == 15

    def test_control_impact_full_buyout(self):
        """Test control impact for full streamer original"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Streamer Original",
            deal_type=DealType.STREAMER_ORIGINAL,
            counterparty_name="Major Streamer",
            amount=Decimal("30000000"),
            ip_ownership="counterparty",  # +40
            has_veto_rights=True,  # +20
            sequel_rights_holder="counterparty",  # +15
            approval_rights_granted=[
                ApprovalRight.FINAL_CUT,  # +10 (counted in loop)
                ApprovalRight.SCRIPT,
                ApprovalRight.DIRECTOR,
                ApprovalRight.CAST,
            ],  # 4 * 10 = 40
        )

        # 40 + 20 + 15 + 40 = 115, capped at 100
        assert deal.control_impact_score() == 100


class TestOwnershipImpactScoring:
    """Test ownership impact score calculations"""

    def test_ownership_full_retained(self):
        """Test ownership score when fully retained"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.EQUITY_INVESTMENT,
            counterparty_name="Test",
            amount=Decimal("5000000"),
            ip_ownership="producer",
        )

        assert deal.ownership_impact_score() == 100

    def test_ownership_ip_transfer_counterparty(self):
        """Test ownership impact from IP transfer"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.STREAMER_ORIGINAL,
            counterparty_name="Test",
            amount=Decimal("30000000"),
            ip_ownership="counterparty",
        )

        # Base 100 - 50 for counterparty IP = 50
        assert deal.ownership_impact_score() == 50

    def test_ownership_worldwide_penalty(self):
        """Test ownership penalty for worldwide rights"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.STREAMER_LICENSE,
            counterparty_name="Test",
            amount=Decimal("6000000"),
            is_worldwide=True,
        )

        # Base 100 - 20 for worldwide = 80
        assert deal.ownership_impact_score() == 80

    def test_ownership_long_term_penalty(self):
        """Test ownership penalty for long license terms"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.STREAMER_LICENSE,
            counterparty_name="Test",
            amount=Decimal("6000000"),
            term_years=25,  # 15 years over threshold
        )

        # Base 100 - (15 * 2) = 100 - 30 = 70, but capped at -20
        # Actually: min((25-10)*2, 20) = min(30, 20) = 20
        # So 100 - 20 = 80
        assert deal.ownership_impact_score() == 80


class TestOptionalityScoring:
    """Test optionality score calculations"""

    def test_optionality_full_retained(self):
        """Test optionality when fully retained"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("5000000"),
        )

        assert deal.optionality_score() == 100

    def test_optionality_mfn_penalty(self):
        """Test optionality penalty for MFN clause"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.EQUITY_INVESTMENT,
            counterparty_name="Test",
            amount=Decimal("5000000"),
            mfn_clause=True,
        )

        # Base 100 - 15 for MFN = 85
        assert deal.optionality_score() == 85

    def test_optionality_sequel_rights_penalty(self):
        """Test optionality penalty for sequel rights transfer"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.STREAMER_ORIGINAL,
            counterparty_name="Test",
            amount=Decimal("30000000"),
            sequel_rights_holder="counterparty",
        )

        # Base 100 - 25 for sequel rights = 75
        assert deal.optionality_score() == 75

    def test_optionality_reversion_bonus(self):
        """Test optionality bonus for reversion trigger"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.STREAMER_LICENSE,
            counterparty_name="Test",
            amount=Decimal("6000000"),
            reversion_trigger_years=10,
        )

        # Base 100 + bonus for 10-year reversion would exceed 100
        # But scores are capped at 100
        assert deal.optionality_score() == 100  # Capped at max

    def test_optionality_cross_collateral_penalty(self):
        """Test optionality penalty for cross-collateralization"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.OUTPUT_DEAL,
            counterparty_name="Test",
            amount=Decimal("10000000"),
            cross_collateralized=True,
        )

        # Base 100 - 10 for cross-coll = 90
        assert deal.optionality_score() == 90


class TestDealBlockTemplates:
    """Test deal template factory functions"""

    def test_equity_investment_template(self):
        """Test equity investment template"""
        deal = create_equity_investment_template(
            deal_id="EQ-001",
            counterparty_name="Test Fund",
            amount=Decimal("8000000"),
            ownership_percentage=Decimal("25"),
        )

        assert deal.deal_type == DealType.EQUITY_INVESTMENT
        assert deal.ownership_percentage == Decimal("25")
        assert deal.premium_percentage == Decimal("20")  # Default
        assert deal.has_board_seat is True  # Default
        assert deal.ip_ownership == "producer"

    def test_presale_template(self):
        """Test pre-sale template"""
        deal = create_presale_template(
            deal_id="PS-001",
            counterparty_name="UK Distributor",
            amount=Decimal("3000000"),
            territories=["UK", "Ireland"],
        )

        assert deal.deal_type == DealType.PRESALE_MG
        assert deal.territories == ["UK", "Ireland"]
        assert deal.sales_commission_pct == Decimal("15")  # Default
        assert deal.backend_participation_pct == Decimal("50")

    def test_streamer_license_template(self):
        """Test streamer license template"""
        deal = create_streamer_license_template(
            deal_id="SL-001",
            counterparty_name="Major Streamer",
            amount=Decimal("6000000"),
            territories=["North America"],
        )

        assert deal.deal_type == DealType.STREAMER_LICENSE
        assert deal.term_years == 7  # Default
        assert deal.holdback_days == 120  # Default
        assert deal.ip_ownership == "producer"
        assert deal.is_recoupable is False

    def test_streamer_original_template(self):
        """Test streamer original template"""
        deal = create_streamer_original_template(
            deal_id="SO-001",
            counterparty_name="Major Streamer",
            budget=Decimal("30000000"),
        )

        assert deal.deal_type == DealType.STREAMER_ORIGINAL
        assert deal.ip_ownership == "counterparty"
        assert deal.sequel_rights_holder == "counterparty"
        assert deal.is_worldwide is True
        assert ApprovalRight.FINAL_CUT in deal.approval_rights_granted

    def test_gap_financing_template(self):
        """Test gap financing template"""
        deal = create_gap_financing_template(
            deal_id="GF-001",
            counterparty_name="Film Bank",
            amount=Decimal("4000000"),
        )

        assert deal.deal_type == DealType.GAP_FINANCING
        assert deal.interest_rate == Decimal("12")  # Default
        assert deal.origination_fee_pct == Decimal("3")  # Default
        assert deal.recoupment_priority == 5


class TestDealBlockSerialization:
    """Test to_dict() method and serialization"""

    def test_to_dict_basic(self):
        """Test basic serialization"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test Deal",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test Partner",
            amount=Decimal("5000000"),
        )

        result = deal.to_dict()

        assert result["deal_id"] == "DEAL-001"
        assert result["deal_name"] == "Test Deal"
        assert result["deal_type"] == "presale_mg"
        assert result["amount"] == "5000000"
        assert "net_amount" in result
        assert "expected_value" in result
        assert "control_impact" in result
        assert "ownership_impact" in result
        assert "optionality" in result

    def test_to_dict_computed_values(self):
        """Test computed values in serialization"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test Deal",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test Partner",
            amount=Decimal("10000000"),
            sales_commission_pct=Decimal("15"),
            probability_of_closing=Decimal("80"),
        )

        result = deal.to_dict()

        # Net amount: 10M - 15% = 8.5M
        assert result["net_amount"] == "8500000"

        # Expected value: 8.5M * 80% = 6.8M
        assert result["expected_value"] == "6800000"

    def test_to_dict_rights_windows(self):
        """Test rights windows serialization"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test Deal",
            deal_type=DealType.STREAMER_LICENSE,
            counterparty_name="Test Streamer",
            amount=Decimal("5000000"),
            rights_windows=[RightsWindow.SVOD, RightsWindow.AVOD],
        )

        result = deal.to_dict()

        assert result["rights_windows"] == ["svod", "avod"]

    def test_to_dict_approval_rights(self):
        """Test approval rights serialization"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test Deal",
            deal_type=DealType.EQUITY_INVESTMENT,
            counterparty_name="Test Investor",
            amount=Decimal("5000000"),
            approval_rights_granted=[ApprovalRight.BUDGET, ApprovalRight.CAST],
        )

        result = deal.to_dict()

        assert result["approval_rights_granted"] == ["budget", "cast"]


class TestDealBlockEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_zero_fees(self):
        """Test with explicitly zero fees"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("5000000"),
            sales_commission_pct=Decimal("0"),
            origination_fee_pct=Decimal("0"),
        )

        assert deal.net_amount_after_fees() == Decimal("5000000")

    def test_minimum_amount(self):
        """Test with minimum valid amount"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.GRANT,
            counterparty_name="Film Fund",
            amount=Decimal("0.01"),
        )

        assert deal.amount == Decimal("0.01")

    def test_empty_territories(self):
        """Test with empty territories list"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.EQUITY_INVESTMENT,
            counterparty_name="Test",
            amount=Decimal("5000000"),
            territories=[],
        )

        assert deal.territories == []
        assert deal.ownership_impact_score() == 100  # No territory penalty

    def test_all_approval_rights(self):
        """Test with all approval rights granted"""
        deal = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.STREAMER_ORIGINAL,
            counterparty_name="Test",
            amount=Decimal("30000000"),
            approval_rights_granted=list(ApprovalRight),
        )

        # 8 approval rights * 10 = 80 points
        assert deal.control_impact_score() >= 80

    def test_probability_boundaries(self):
        """Test probability at boundaries"""
        # 100%
        deal_certain = DealBlock(
            deal_id="DEAL-001",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("1000000"),
            probability_of_closing=Decimal("100"),
        )
        assert deal_certain.expected_value() == Decimal("1000000")

        # 0%
        deal_unlikely = DealBlock(
            deal_id="DEAL-002",
            deal_name="Test",
            deal_type=DealType.PRESALE_MG,
            counterparty_name="Test",
            amount=Decimal("1000000"),
            probability_of_closing=Decimal("0"),
        )
        assert deal_unlikely.expected_value() == Decimal("0")
