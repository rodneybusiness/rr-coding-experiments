"""
Unit tests for core Pydantic models
"""

import pytest
from decimal import Decimal
from datetime import date

from models.financial_instruments import (
    Equity,
    SeniorDebt,
    GapDebt,
    TaxCreditLoan,
    PreSale,
    InstrumentType,
    RecoupmentPriority
)
from models.project_profile import (
    ProjectProfile,
    ProjectType,
    AnimationTechnique,
    TargetAudience,
    DevelopmentStatus,
    StrategicPathway,
    ProductionJurisdiction
)
from models.incentive_policy import (
    IncentivePolicy,
    IncentiveType,
    MonetizationMethod,
    QPEDefinition,
    QPECategory
)
from models.capital_stack import CapitalStack, CapitalComponent
from models.waterfall import WaterfallStructure, WaterfallNode, PayeeType, RecoupmentBasis


class TestFinancialInstruments:
    """Test financial instrument models"""

    def test_equity_creation(self):
        """Test creating an Equity instrument"""
        equity = Equity(
            instrument_id="EQ-001",
            amount=Decimal("5000000"),
            ownership_percentage=Decimal("30"),
            premium_percentage=Decimal("20"),
            provider_name="Test Fund LP"
        )

        assert equity.instrument_type == InstrumentType.EQUITY
        assert equity.amount == Decimal("5000000")
        assert equity.ownership_percentage == Decimal("30")
        assert equity.recoupment_priority == RecoupmentPriority.EQUITY

    def test_equity_validation(self):
        """Test equity validation rules"""
        with pytest.raises(ValueError):
            Equity(
                instrument_id="EQ-002",
                amount=Decimal("-100"),  # Invalid: negative amount
                ownership_percentage=Decimal("30")
            )

        with pytest.raises(ValueError):
            Equity(
                instrument_id="EQ-003",
                amount=Decimal("1000000"),
                ownership_percentage=Decimal("150")  # Invalid: > 100%
            )

    def test_debt_fees_calculation(self):
        """Test debt fee calculations"""
        debt = SeniorDebt(
            instrument_id="DEBT-001",
            amount=Decimal("10000000"),
            interest_rate=Decimal("8.5"),
            origination_fee_percentage=Decimal("2.0"),
            commitment_fee_percentage=Decimal("0.5")
        )

        assert debt.total_fees_percentage == Decimal("2.5")
        assert debt.total_fees_amount == Decimal("250000")

    def test_gap_debt_validation(self):
        """Test gap debt percentage validation"""
        # Valid gap percentage
        gap = GapDebt(
            instrument_id="GAP-001",
            amount=Decimal("3000000"),
            interest_rate=Decimal("12"),
            gap_percentage=Decimal("40")
        )
        assert gap.gap_percentage == Decimal("40")

        # Invalid: too high
        with pytest.raises(ValueError):
            GapDebt(
                instrument_id="GAP-002",
                amount=Decimal("3000000"),
                interest_rate=Decimal("12"),
                gap_percentage=Decimal("75")  # > 50%
            )

    def test_tax_credit_loan(self):
        """Test tax credit loan model"""
        tax_loan = TaxCreditLoan(
            instrument_id="TAX-001",
            amount=Decimal("5000000"),
            interest_rate=Decimal("8"),
            tax_credit_jurisdiction="Quebec",
            certified_tax_credit_amount=Decimal("6000000"),
            advance_rate=Decimal("83.33")
        )

        assert tax_loan.instrument_type == InstrumentType.TAX_CREDIT_LOAN
        assert tax_loan.certified_tax_credit_amount == Decimal("6000000")


class TestProjectProfile:
    """Test project profile model"""

    def test_project_creation(self):
        """Test creating a project profile"""
        jurisdiction = ProductionJurisdiction(
            country="Canada",
            state_province="Quebec",
            estimated_spend_percentage=Decimal("60"),
            estimated_local_labor_percentage=Decimal("75")
        )

        project = ProjectProfile(
            project_id="PROJ-001",
            project_name="Test Film",
            project_type=ProjectType.FEATURE_FILM,
            animation_technique=AnimationTechnique.CGI_3D,
            target_audience=TargetAudience.FAMILY,
            target_runtime_minutes=90,
            total_budget=Decimal("25000000"),
            development_status=DevelopmentStatus.GREENLIT,
            production_jurisdictions=[jurisdiction],
            strategic_pathway=StrategicPathway.INDEPENDENT_PATCHWORK
        )

        assert project.total_budget == Decimal("25000000")
        assert project.contingency_percentage == Decimal("10")  # default
        assert len(project.production_jurisdictions) == 1

    def test_priority_weights_validation(self):
        """Test priority weights sum to 100%"""
        jurisdiction = ProductionJurisdiction(
            country="Canada",
            estimated_spend_percentage=Decimal("100")
        )

        project = ProjectProfile(
            project_id="PROJ-002",
            project_name="Test",
            project_type=ProjectType.FEATURE_FILM,
            animation_technique=AnimationTechnique.CGI_3D,
            target_audience=TargetAudience.FAMILY,
            total_budget=Decimal("10000000"),
            development_status=DevelopmentStatus.CONCEPT,
            production_jurisdictions=[jurisdiction],
            strategic_pathway=StrategicPathway.STUDIO_BUYOUT,
            priority_creative_control=Decimal("40"),
            priority_financial_return=Decimal("30"),
            priority_risk_mitigation=Decimal("30")
        )

        assert project.validate_priority_weights() is True


class TestIncentivePolicy:
    """Test incentive policy model and calculations"""

    def test_incentive_policy_creation(self):
        """Test creating an incentive policy"""
        qpe_def = QPEDefinition(
            included_categories=[QPECategory.LABOR_RESIDENT, QPECategory.VFX_ANIMATION],
            minimum_local_labor_percentage=Decimal("75")
        )

        policy = IncentivePolicy(
            policy_id="UK-AVEC-2025",
            jurisdiction="United Kingdom",
            program_name="Audio-Visual Expenditure Credit",
            headline_rate=Decimal("34"),
            incentive_type=IncentiveType.REFUNDABLE_TAX_CREDIT,
            qpe_definition=qpe_def,
            monetization_methods=[MonetizationMethod.DIRECT_CASH, MonetizationMethod.LOAN_COLLATERAL],
            is_taxable_income_federal=False,
            last_updated=date(2025, 10, 31)
        )

        assert policy.headline_rate == Decimal("34")
        assert policy.incentive_type == IncentiveType.REFUNDABLE_TAX_CREDIT

    def test_net_benefit_calculation_direct_cash(self):
        """Test net benefit calculation for direct cash (refundable credit)"""
        qpe_def = QPEDefinition(
            included_categories=[QPECategory.LABOR_RESIDENT]
        )

        policy = IncentivePolicy(
            policy_id="TEST-001",
            jurisdiction="Test",
            program_name="Test Credit",
            headline_rate=Decimal("30"),
            incentive_type=IncentiveType.REFUNDABLE_TAX_CREDIT,
            qpe_definition=qpe_def,
            monetization_methods=[MonetizationMethod.DIRECT_CASH],
            is_taxable_income_federal=True,
            federal_tax_rate=Decimal("21"),
            audit_cost_typical=Decimal("50000"),
            last_updated=date.today()
        )

        result = policy.calculate_net_benefit(
            qualified_spend=Decimal("10000000"),
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Gross credit: $10M * 30% = $3M
        assert result["gross_credit"] == Decimal("3000000")
        # No discount for direct cash
        assert result["discount_amount"] == Decimal("0")
        assert result["net_credit"] == Decimal("3000000")
        # Tax cost: $3M * 21% = $630K
        assert result["tax_cost"] == Decimal("630000")
        # Net benefit: $3M - $630K - $50K = $2.32M
        assert result["net_cash_benefit"] == Decimal("2320000")
        # Effective rate: $2.32M / $10M = 23.2%
        assert result["effective_rate"] == Decimal("23.2")

    def test_net_benefit_calculation_with_transfer(self):
        """Test net benefit calculation for transferable credit"""
        qpe_def = QPEDefinition(
            included_categories=[QPECategory.LABOR_RESIDENT]
        )

        policy = IncentivePolicy(
            policy_id="TEST-002",
            jurisdiction="Test",
            program_name="Transferable Credit",
            headline_rate=Decimal("25"),
            incentive_type=IncentiveType.TRANSFERABLE_TAX_CREDIT,
            qpe_definition=qpe_def,
            monetization_methods=[MonetizationMethod.TRANSFER_SALE],
            typical_transfer_discount_low=Decimal("8"),
            typical_transfer_discount_high=Decimal("12"),
            is_taxable_income_federal=False,
            audit_cost_typical=Decimal("30000"),
            last_updated=date.today()
        )

        result = policy.calculate_net_benefit(
            qualified_spend=Decimal("5000000"),
            monetization_method=MonetizationMethod.TRANSFER_SALE,
            transfer_discount=Decimal("10")
        )

        # Gross credit: $5M * 25% = $1.25M
        assert result["gross_credit"] == Decimal("1250000")
        # Discount: $1.25M * 10% = $125K
        assert result["discount_amount"] == Decimal("125000")
        # Net credit: $1.25M - $125K = $1.125M
        assert result["net_credit"] == Decimal("1125000")
        # No tax (not taxable)
        assert result["tax_cost"] == Decimal("0")
        # Net benefit: $1.125M - $30K = $1.095M
        assert result["net_cash_benefit"] == Decimal("1095000")


class TestCapitalStack:
    """Test capital stack model"""

    def test_capital_stack_creation(self):
        """Test creating a capital stack"""
        equity = Equity(
            instrument_id="EQ-001",
            amount=Decimal("5000000"),
            ownership_percentage=Decimal("40"),
            premium_percentage=Decimal("20")
        )

        component = CapitalComponent(
            component_id="COMP-001",
            instrument=equity,
            position=1,
            is_committed=True
        )

        stack = CapitalStack(
            stack_id="STACK-001",
            project_id="PROJ-001",
            components=[component]
        )

        assert stack.total_capital_raised() == Decimal("5000000")
        assert stack.total_equity() == Decimal("5000000")
        assert stack.total_debt() == Decimal("0")

    def test_capital_stack_calculations(self):
        """Test capital stack calculation methods"""
        equity = Equity(
            instrument_id="EQ-001",
            amount=Decimal("8000000"),
            ownership_percentage=Decimal("50")
        )

        debt = SeniorDebt(
            instrument_id="DEBT-001",
            amount=Decimal("12000000"),
            interest_rate=Decimal("8")
        )

        stack = CapitalStack(
            stack_id="STACK-002",
            project_id="PROJ-002",
            components=[
                CapitalComponent(component_id="C1", instrument=equity, position=2),
                CapitalComponent(component_id="C2", instrument=debt, position=1)
            ]
        )

        summary = stack.stack_summary()

        assert summary["total_capital"] == Decimal("20000000")
        assert summary["total_equity"] == Decimal("8000000")
        assert summary["total_debt"] == Decimal("12000000")
        assert summary["debt_to_equity_ratio"] == Decimal("1.5")
        assert summary["equity_percentage"] == Decimal("40")
        assert summary["debt_percentage"] == Decimal("60")


class TestWaterfall:
    """Test waterfall structure and calculations"""

    def test_waterfall_node_payment_calculation(self):
        """Test individual node payment calculation"""
        node = WaterfallNode(
            node_id="NODE-001",
            priority=RecoupmentPriority.DISTRIBUTION_FEES,
            description="Distribution Fees",
            payee_type=PayeeType.DISTRIBUTOR,
            payee_name="XYZ Distribution",
            recoupment_basis=RecoupmentBasis.GROSS_RECEIPTS,
            percentage_of_receipts=Decimal("25")
        )

        payment = node.calculate_payment(
            available_pool=Decimal("10000000"),
            basis_amount=Decimal("10000000")
        )

        # 25% of $10M = $2.5M
        assert payment == Decimal("2500000")

    def test_simple_waterfall_execution(self):
        """Test executing a simple waterfall"""
        waterfall = WaterfallStructure(
            waterfall_id="WF-001",
            project_id="PROJ-001",
            nodes=[
                WaterfallNode(
                    node_id="N1",
                    priority=RecoupmentPriority.DISTRIBUTION_FEES,
                    description="Dist Fees",
                    payee_type=PayeeType.DISTRIBUTOR,
                    payee_name="Distributor A",
                    recoupment_basis=RecoupmentBasis.GROSS_RECEIPTS,
                    percentage_of_receipts=Decimal("25")
                ),
                WaterfallNode(
                    node_id="N2",
                    priority=RecoupmentPriority.SENIOR_DEBT_PRINCIPAL,
                    description="Senior Debt",
                    payee_type=PayeeType.LENDER,
                    payee_name="Bank A",
                    recoupment_basis=RecoupmentBasis.REMAINING_POOL,
                    fixed_amount=Decimal("10000000")
                ),
                WaterfallNode(
                    node_id="N3",
                    priority=RecoupmentPriority.EQUITY_RECOUPMENT,
                    description="Equity Recoup",
                    payee_type=PayeeType.INVESTOR,
                    payee_name="Investor A",
                    recoupment_basis=RecoupmentBasis.REMAINING_POOL,
                    fixed_amount=Decimal("5000000")
                )
            ]
        )

        result = waterfall.calculate_waterfall(gross_receipts=Decimal("20000000"))

        # $20M gross
        # - $5M distribution fees (25%)
        # = $15M remaining
        # - $10M senior debt
        # = $5M remaining
        # - $5M equity
        # = $0 remaining

        assert result["gross_receipts"] == Decimal("20000000")
        assert result["total_distributed"] == Decimal("20000000")
        assert result["remaining_pool"] == Decimal("0")
        assert result["payee_totals"]["Distributor A"] == Decimal("5000000")
        assert result["payee_totals"]["Bank A"] == Decimal("10000000")
        assert result["payee_totals"]["Investor A"] == Decimal("5000000")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
