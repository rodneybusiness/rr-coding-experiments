"""
Unit Tests for Stakeholder Analyzer

Tests stakeholder identification, return calculations (IRR/NPV),
cash-on-cash multiples, and payback periods.
"""

import pytest
from decimal import Decimal

from engines.waterfall_executor.stakeholder_analyzer import (
    StakeholderCashFlows,
    StakeholderAnalysisResult,
    StakeholderAnalyzer
)
from engines.waterfall_executor.waterfall_executor import WaterfallExecutor
from engines.waterfall_executor.revenue_projector import RevenueProjector
from models.waterfall import WaterfallStructure, WaterfallNode, RecoupmentPriority
from models.capital_stack import CapitalStack, CapitalComponent
from models.financial_instruments import Equity, SeniorDebt, GapDebt


@pytest.fixture
def simple_waterfall():
    """Create simple waterfall for testing"""
    return WaterfallStructure(
        waterfall_name="Test Waterfall",
        default_distribution_fee_rate=Decimal("30.0"),
        nodes=[
            WaterfallNode(
                priority=RecoupmentPriority.SENIOR_DEBT,
                payee="Senior Lender",
                amount=Decimal("8000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                payee="Equity Investors",
                amount=Decimal("12000000"),
                percentage=None
            ),
            WaterfallNode(
                priority=RecoupmentPriority.NET_PROFITS,
                payee="Equity Investors",
                amount=None,
                percentage=Decimal("100.0")
            ),
        ]
    )


@pytest.fixture
def simple_capital_stack():
    """Create simple capital stack for testing"""
    equity = Equity(
        amount=Decimal("12000000"),
        ownership_percentage=Decimal("100.0"),
        premium_percentage=Decimal("20.0")
    )

    senior_debt = SeniorDebt(
        amount=Decimal("8000000"),
        interest_rate=Decimal("8.0"),
        term_months=24,
        origination_fee_percentage=Decimal("2.0")
    )

    return CapitalStack(
        stack_name="Test Stack",
        project_budget=Decimal("20000000"),
        components=[
            CapitalComponent(instrument=senior_debt, position=1),
            CapitalComponent(instrument=equity, position=2)
        ]
    )


@pytest.fixture
def waterfall_result_profitable(simple_waterfall):
    """Create profitable waterfall execution result"""
    projector = RevenueProjector()
    projection = projector.project(
        total_ultimate_revenue=Decimal("50000000"),
        release_strategy="wide_theatrical",
        project_name="Profitable Film"
    )

    executor = WaterfallExecutor(simple_waterfall)
    return executor.execute_over_time(projection)


@pytest.fixture
def waterfall_result_breakeven(simple_waterfall):
    """Create breakeven waterfall execution result"""
    projector = RevenueProjector()
    projection = projector.project(
        total_ultimate_revenue=Decimal("20000000"),
        release_strategy="wide_theatrical",
        project_name="Breakeven Film"
    )

    executor = WaterfallExecutor(simple_waterfall)
    return executor.execute_over_time(projection)


class TestStakeholderCashFlows:
    """Test StakeholderCashFlows dataclass"""

    def test_stakeholder_cash_flows_creation(self):
        """Test creating stakeholder cash flows"""
        cash_flows = StakeholderCashFlows(
            stakeholder_id="equity_test",
            stakeholder_name="Test Equity",
            stakeholder_type="equity",
            initial_investment=Decimal("10000000"),
            investment_quarter=0,
            quarterly_receipts={
                4: Decimal("2000000"),
                8: Decimal("3000000"),
                12: Decimal("5000000")
            },
            total_receipts=Decimal("10000000"),
            irr=Decimal("0.15"),
            npv=Decimal("500000"),
            cash_on_cash=Decimal("1.0"),
            payback_quarter=12,
            payback_years=Decimal("3.0"),
            roi_percentage=Decimal("0.0")
        )

        assert cash_flows.stakeholder_id == "equity_test"
        assert cash_flows.initial_investment == Decimal("10000000")
        assert cash_flows.total_receipts == Decimal("10000000")
        assert cash_flows.cash_on_cash == Decimal("1.0")

    def test_stakeholder_to_dict(self):
        """Test converting stakeholder to dictionary"""
        cash_flows = StakeholderCashFlows(
            stakeholder_id="equity_test",
            stakeholder_name="Test Equity",
            stakeholder_type="equity",
            initial_investment=Decimal("10000000"),
            investment_quarter=0,
            quarterly_receipts={4: Decimal("2000000")},
            total_receipts=Decimal("10000000"),
            irr=Decimal("0.15"),
            npv=Decimal("500000"),
            cash_on_cash=Decimal("1.0"),
            payback_quarter=12,
            payback_years=Decimal("3.0"),
            roi_percentage=Decimal("0.0")
        )

        result = cash_flows.to_dict()

        assert isinstance(result, dict)
        assert result["stakeholder_id"] == "equity_test"
        assert result["initial_investment"] == "10000000"
        assert result["irr"] == "0.15"


class TestStakeholderAnalyzer:
    """Test StakeholderAnalyzer class"""

    def test_analyzer_initialization(self, simple_capital_stack):
        """Test analyzer initialization"""
        analyzer = StakeholderAnalyzer(simple_capital_stack, discount_rate=Decimal("0.12"))

        assert analyzer.capital_stack == simple_capital_stack
        assert analyzer.discount_rate == Decimal("0.12")

    def test_analyzer_default_discount_rate(self, simple_capital_stack):
        """Test analyzer with default discount rate"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        assert analyzer.discount_rate == Decimal("0.12")

    def test_analyze_profitable_scenario(self, simple_capital_stack, waterfall_result_profitable):
        """Test analyzing profitable scenario"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)
        result = analyzer.analyze(waterfall_result_profitable)

        assert isinstance(result, StakeholderAnalysisResult)
        assert len(result.stakeholders) == 2  # Senior debt + equity

        # Check that stakeholders have positive returns
        for stakeholder in result.stakeholders:
            assert stakeholder.total_receipts > 0

    def test_analyze_identifies_all_stakeholders(self, simple_capital_stack, waterfall_result_profitable):
        """Test that all capital stack components are identified"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)
        result = analyzer.analyze(waterfall_result_profitable)

        stakeholder_types = {s.stakeholder_type for s in result.stakeholders}

        # Should have both equity and debt
        assert "equity" in stakeholder_types
        assert "senior_debt" in stakeholder_types

    def test_calculate_irr_positive_returns(self, simple_capital_stack):
        """Test IRR calculation with positive returns"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        # Cash flows: invest $10M at Q0, receive $15M at Q8
        cash_flows = [
            (0, Decimal("-10000000")),
            (8, Decimal("15000000"))
        ]

        irr = analyzer.calculate_irr(cash_flows)

        assert irr is not None
        assert irr > 0  # Should have positive IRR

    def test_calculate_irr_negative_returns(self, simple_capital_stack):
        """Test IRR calculation with negative returns (loss)"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        # Cash flows: invest $10M at Q0, receive $5M at Q8 (50% loss)
        cash_flows = [
            (0, Decimal("-10000000")),
            (8, Decimal("5000000"))
        ]

        irr = analyzer.calculate_irr(cash_flows)

        assert irr is not None
        assert irr < 0  # Should have negative IRR

    def test_calculate_irr_no_returns(self, simple_capital_stack):
        """Test IRR calculation with no returns"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        # Only investment, no receipts
        cash_flows = [
            (0, Decimal("-10000000"))
        ]

        irr = analyzer.calculate_irr(cash_flows)

        assert irr is None  # IRR undefined

    def test_calculate_irr_multiple_cash_flows(self, simple_capital_stack):
        """Test IRR calculation with multiple cash flows"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        # Investment at Q0, multiple receipts
        cash_flows = [
            (0, Decimal("-10000000")),
            (4, Decimal("3000000")),
            (8, Decimal("4000000")),
            (12, Decimal("5000000"))
        ]

        irr = analyzer.calculate_irr(cash_flows)

        assert irr is not None
        assert irr > 0

    def test_calculate_npv_positive(self, simple_capital_stack):
        """Test NPV calculation with positive value"""
        analyzer = StakeholderAnalyzer(simple_capital_stack, discount_rate=Decimal("0.10"))

        # Invest $10M, receive $12M in 1 year
        cash_flows = [
            (0, Decimal("-10000000")),
            (4, Decimal("12000000"))
        ]

        npv = analyzer.calculate_npv(cash_flows, Decimal("0.10"))

        # NPV = -10M + 12M / (1.10)^1 = -10M + 10.91M = 0.91M (approximately)
        assert npv > 0

    def test_calculate_npv_negative(self, simple_capital_stack):
        """Test NPV calculation with negative value"""
        analyzer = StakeholderAnalyzer(simple_capital_stack, discount_rate=Decimal("0.20"))

        # Invest $10M, receive $11M in 2 years at 20% discount rate
        cash_flows = [
            (0, Decimal("-10000000")),
            (8, Decimal("11000000"))
        ]

        npv = analyzer.calculate_npv(cash_flows, Decimal("0.20"))

        # NPV should be negative due to high discount rate and delay
        assert npv < 0

    def test_calculate_payback_period_exact(self, simple_capital_stack):
        """Test payback period calculation - exact recovery"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        initial_investment = Decimal("10000000")
        quarterly_receipts = {
            2: Decimal("3000000"),
            4: Decimal("4000000"),
            6: Decimal("3000000")  # Total = 10M exactly at Q6
        }

        payback_quarter, payback_years = analyzer.calculate_payback_period(
            initial_investment,
            quarterly_receipts
        )

        assert payback_quarter == 6
        assert payback_years == Decimal("1.5")  # 6 quarters / 4 = 1.5 years

    def test_calculate_payback_period_early(self, simple_capital_stack):
        """Test payback period calculation - early recovery"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        initial_investment = Decimal("10000000")
        quarterly_receipts = {
            2: Decimal("12000000")  # Recovers in first payment
        }

        payback_quarter, payback_years = analyzer.calculate_payback_period(
            initial_investment,
            quarterly_receipts
        )

        assert payback_quarter == 2
        assert payback_years == Decimal("0.5")

    def test_calculate_payback_period_never(self, simple_capital_stack):
        """Test payback period when investment never recovers"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        initial_investment = Decimal("10000000")
        quarterly_receipts = {
            2: Decimal("3000000"),
            4: Decimal("2000000")  # Total only 5M, never reaches 10M
        }

        payback_quarter, payback_years = analyzer.calculate_payback_period(
            initial_investment,
            quarterly_receipts
        )

        assert payback_quarter is None
        assert payback_years is None

    def test_calculate_payback_period_empty_receipts(self, simple_capital_stack):
        """Test payback period with no receipts"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        payback_quarter, payback_years = analyzer.calculate_payback_period(
            Decimal("10000000"),
            {}
        )

        assert payback_quarter is None
        assert payback_years is None

    def test_map_instrument_to_payee_equity(self, simple_capital_stack):
        """Test mapping equity instrument to payee"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        equity = Equity(
            amount=Decimal("10000000"),
            ownership_percentage=Decimal("100.0"),
            premium_percentage=Decimal("20.0")
        )

        payee = analyzer._map_instrument_to_payee(equity)

        assert payee == "Equity Investors"

    def test_map_instrument_to_payee_senior_debt(self, simple_capital_stack):
        """Test mapping senior debt instrument to payee"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        debt = SeniorDebt(
            amount=Decimal("8000000"),
            interest_rate=Decimal("8.0"),
            term_months=24,
            origination_fee_percentage=Decimal("2.0")
        )

        payee = analyzer._map_instrument_to_payee(debt)

        assert payee == "Senior Lender"

    def test_map_instrument_to_payee_gap_debt(self, simple_capital_stack):
        """Test mapping gap debt instrument to payee"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        gap_debt = GapDebt(
            amount=Decimal("3000000"),
            interest_rate=Decimal("12.0"),
            term_months=18,
            origination_fee_percentage=Decimal("3.0"),
            gap_percentage=Decimal("50.0")  # Required field
        )

        payee = analyzer._map_instrument_to_payee(gap_debt)

        assert payee == "Gap Lender"

    def test_extract_quarterly_receipts(self, simple_capital_stack, waterfall_result_profitable):
        """Test extracting quarterly receipts for a payee"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)

        receipts = analyzer._extract_quarterly_receipts(
            waterfall_result_profitable,
            "Senior Lender"
        )

        assert isinstance(receipts, dict)
        # Should have some quarters with receipts
        assert len(receipts) > 0
        # All receipts should be positive
        for quarter, amount in receipts.items():
            assert amount > 0

    def test_generate_summary_statistics(self, simple_capital_stack, waterfall_result_profitable):
        """Test summary statistics generation"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)
        result = analyzer.analyze(waterfall_result_profitable)

        summary = result.summary_statistics

        assert "total_invested" in summary
        assert "total_recouped" in summary
        assert "overall_recovery_rate" in summary
        assert "num_stakeholders" in summary

        # Should have 2 stakeholders
        assert summary["num_stakeholders"] == 2

    def test_analysis_result_to_dict(self, simple_capital_stack, waterfall_result_profitable):
        """Test converting analysis result to dictionary"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)
        result = analyzer.analyze(waterfall_result_profitable)

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "project_name" in result_dict
        assert "stakeholders" in result_dict
        assert "summary_statistics" in result_dict

    def test_cash_on_cash_calculation(self, simple_capital_stack, waterfall_result_profitable):
        """Test cash-on-cash multiple calculation"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)
        result = analyzer.analyze(waterfall_result_profitable)

        for stakeholder in result.stakeholders:
            # Cash-on-cash should be non-negative
            assert stakeholder.cash_on_cash >= 0

            # Cash-on-cash = total_receipts / initial_investment
            expected_coc = stakeholder.total_receipts / stakeholder.initial_investment
            assert stakeholder.cash_on_cash == expected_coc

    def test_roi_percentage_calculation(self, simple_capital_stack, waterfall_result_profitable):
        """Test ROI percentage calculation"""
        analyzer = StakeholderAnalyzer(simple_capital_stack)
        result = analyzer.analyze(waterfall_result_profitable)

        for stakeholder in result.stakeholders:
            # ROI = (receipts - investment) / investment * 100
            expected_roi = ((stakeholder.total_receipts - stakeholder.initial_investment)
                           / stakeholder.initial_investment * Decimal("100"))

            assert stakeholder.roi_percentage == expected_roi
