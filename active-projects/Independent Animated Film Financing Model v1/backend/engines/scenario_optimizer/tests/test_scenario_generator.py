"""
Unit Tests for ScenarioGenerator

Tests template-based generation, budget allocation variations, and deal type constraints.
"""

import pytest
from decimal import Decimal
from copy import deepcopy

from engines.scenario_optimizer import (
    ScenarioGenerator,
    FinancingTemplate,
    ScenarioConfig,
    DEFAULT_TEMPLATES
)
from models.capital_stack import CapitalStack
from models.financial_instruments import (
    Equity, SeniorDebt, MezzanineDebt, GapFinancing, PreSale, TaxIncentive
)


class TestScenarioGenerator:
    """Test ScenarioGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return ScenarioGenerator()

    @pytest.fixture
    def project_budget(self):
        """Standard project budget."""
        return Decimal("30000000")

    # Template Loading Tests

    def test_initialization_loads_default_templates(self, generator):
        """Test that generator loads 5 default templates on init."""
        assert len(generator.templates) == 5
        assert "debt_heavy" in generator.templates
        assert "equity_heavy" in generator.templates
        assert "balanced" in generator.templates
        assert "presale_focused" in generator.templates
        assert "incentive_maximized" in generator.templates

    def test_list_templates(self, generator):
        """Test listing available templates."""
        templates = generator.list_templates()
        assert len(templates) == 5
        assert set(templates) == set(DEFAULT_TEMPLATES)

    def test_get_template(self, generator):
        """Test getting specific template."""
        template = generator.get_template("debt_heavy")
        assert template is not None
        assert template.template_name == "debt_heavy"
        assert isinstance(template, FinancingTemplate)

    def test_get_nonexistent_template(self, generator):
        """Test getting template that doesn't exist."""
        template = generator.get_template("nonexistent")
        assert template is None

    # Template-Based Generation Tests

    def test_generate_from_debt_heavy_template(self, generator, project_budget):
        """Test generating debt-heavy scenario."""
        stack = generator.generate_from_template("debt_heavy", project_budget)

        assert stack is not None
        assert stack.project_budget == project_budget
        assert len(stack.components) > 0

        # Verify debt-heavy structure
        debt_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, (SeniorDebt, MezzanineDebt))
        )
        debt_pct = (debt_amount / project_budget) * Decimal("100")
        assert debt_pct >= Decimal("60.0")  # Should have significant debt

    def test_generate_from_equity_heavy_template(self, generator, project_budget):
        """Test generating equity-heavy scenario."""
        stack = generator.generate_from_template("equity_heavy", project_budget)

        assert stack is not None

        # Verify equity-heavy structure
        equity_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, Equity)
        )
        equity_pct = (equity_amount / project_budget) * Decimal("100")
        assert equity_pct >= Decimal("50.0")  # Should have significant equity

    def test_generate_from_balanced_template(self, generator, project_budget):
        """Test generating balanced scenario."""
        stack = generator.generate_from_template("balanced", project_budget)

        assert stack is not None
        assert len(stack.components) >= 3  # Should have multiple instrument types

        # Verify balanced structure (no single type dominates)
        for component in stack.components:
            pct = (component.instrument.amount / project_budget) * Decimal("100")
            assert pct < Decimal("50.0")  # No single instrument > 50%

    def test_generate_from_presale_focused_template(self, generator, project_budget):
        """Test generating pre-sale focused scenario."""
        stack = generator.generate_from_template("presale_focused", project_budget)

        assert stack is not None

        # Verify pre-sale presence
        presale_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, PreSale)
        )
        presale_pct = (presale_amount / project_budget) * Decimal("100")
        assert presale_pct >= Decimal("25.0")  # Significant pre-sales

    def test_generate_from_incentive_maximized_template(self, generator, project_budget):
        """Test generating incentive-maximized scenario."""
        stack = generator.generate_from_template("incentive_maximized", project_budget)

        assert stack is not None

        # Verify tax incentive presence
        incentive_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, TaxIncentive)
        )
        incentive_pct = (incentive_amount / project_budget) * Decimal("100")
        assert incentive_pct >= Decimal("20.0")  # Significant tax incentives

    def test_generate_with_custom_scenario_name(self, generator, project_budget):
        """Test generating scenario with custom name."""
        custom_name = "my_custom_scenario"
        stack = generator.generate_from_template(
            "balanced",
            project_budget,
            scenario_name=custom_name
        )

        assert stack.stack_name == custom_name

    def test_generate_with_invalid_template_raises_error(self, generator, project_budget):
        """Test that invalid template name raises ValueError."""
        with pytest.raises(ValueError, match="Template.*not found"):
            generator.generate_from_template("invalid_template", project_budget)

    # Budget Allocation Variation Tests

    def test_generate_with_allocation_customizations(self, generator, project_budget):
        """Test generating scenario with custom allocations."""
        customizations = {
            "allocations": {
                "equity": Decimal("50.0"),
                "senior_debt": Decimal("30.0")
            }
        }

        stack = generator.generate_from_template(
            "balanced",
            project_budget,
            customizations=customizations
        )

        # Verify custom allocations were applied
        equity_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, Equity)
        )
        equity_pct = (equity_amount / project_budget) * Decimal("100")

        # Should be close to 50% (within 1% tolerance for rounding)
        assert abs(equity_pct - Decimal("50.0")) < Decimal("1.0")

    def test_budget_sum_matches_project_budget(self, generator, project_budget):
        """Test that generated components sum to project budget."""
        stack = generator.generate_from_template("balanced", project_budget)

        component_sum = sum(c.instrument.amount for c in stack.components)

        # Allow 1% tolerance for rounding
        tolerance = project_budget * Decimal("0.01")
        assert abs(component_sum - project_budget) <= tolerance

    def test_generate_with_different_budget_sizes(self, generator):
        """Test generating scenarios with various budget sizes."""
        budgets = [
            Decimal("10000000"),   # Small budget
            Decimal("50000000"),   # Medium budget
            Decimal("100000000")   # Large budget
        ]

        for budget in budgets:
            stack = generator.generate_from_template("balanced", budget)
            assert stack.project_budget == budget

            component_sum = sum(c.instrument.amount for c in stack.components)
            tolerance = budget * Decimal("0.01")
            assert abs(component_sum - budget) <= tolerance

    # Multiple Scenario Generation Tests

    def test_generate_multiple_scenarios(self, generator, project_budget):
        """Test generating multiple scenarios from different templates."""
        scenarios = generator.generate_multiple_scenarios(project_budget)

        assert len(scenarios) == 5  # Should generate from all 5 default templates

        # Each should be a valid CapitalStack
        for stack in scenarios:
            assert isinstance(stack, CapitalStack)
            assert stack.project_budget == project_budget

    def test_generate_multiple_scenarios_with_specific_templates(self, generator, project_budget):
        """Test generating multiple scenarios from specific templates."""
        template_names = ["debt_heavy", "equity_heavy"]
        scenarios = generator.generate_multiple_scenarios(
            project_budget,
            template_names=template_names
        )

        assert len(scenarios) == 2

        # Verify correct templates were used
        scenario_names = [s.stack_name for s in scenarios]
        assert any("debt_heavy" in name for name in scenario_names)
        assert any("equity_heavy" in name for name in scenario_names)

    # Custom Template Tests

    def test_add_custom_template(self, generator):
        """Test adding a custom template."""
        custom_template = FinancingTemplate(
            template_name="custom_test",
            description="Custom test template",
            target_allocations={
                "equity": Decimal("40.0"),
                "senior_debt": Decimal("40.0"),
                "tax_incentives": Decimal("20.0")
            },
            typical_terms={}
        )

        initial_count = len(generator.templates)
        generator.add_custom_template(custom_template)

        assert len(generator.templates) == initial_count + 1
        assert "custom_test" in generator.templates
        assert generator.get_template("custom_test") == custom_template

    def test_generate_from_custom_template(self, generator, project_budget):
        """Test generating scenario from custom template."""
        custom_template = FinancingTemplate(
            template_name="custom_high_equity",
            description="Very high equity template",
            target_allocations={
                "equity": Decimal("80.0"),
                "senior_debt": Decimal("20.0")
            },
            typical_terms={
                "equity": {
                    "ownership": 50.0,
                    "premium": 15.0
                },
                "senior_debt": {
                    "interest_rate": 7.0,
                    "term_months": 24,
                    "origination_fee": 1.5
                }
            }
        )

        generator.add_custom_template(custom_template)
        stack = generator.generate_from_template("custom_high_equity", project_budget)

        assert stack is not None

        equity_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, Equity)
        )
        equity_pct = (equity_amount / project_budget) * Decimal("100")

        # Should be close to 80%
        assert abs(equity_pct - Decimal("80.0")) < Decimal("1.0")

    # Component Position Tests

    def test_components_have_sequential_positions(self, generator, project_budget):
        """Test that generated components have sequential positions."""
        stack = generator.generate_from_template("balanced", project_budget)

        positions = [c.position for c in stack.components]
        assert positions == sorted(positions)  # Should be in order
        assert positions == list(range(1, len(positions) + 1))  # Sequential from 1

    # Instrument Type Tests

    def test_senior_debt_has_correct_attributes(self, generator, project_budget):
        """Test that SeniorDebt instruments have correct attributes."""
        stack = generator.generate_from_template("debt_heavy", project_budget)

        senior_debts = [
            c.instrument for c in stack.components
            if isinstance(c.instrument, SeniorDebt)
        ]

        assert len(senior_debts) > 0

        for debt in senior_debts:
            assert debt.amount > 0
            assert debt.interest_rate > 0
            assert debt.term_months > 0
            assert hasattr(debt, 'origination_fee_percentage')

    def test_mezzanine_debt_has_equity_kicker(self, generator, project_budget):
        """Test that MezzanineDebt has equity kicker."""
        stack = generator.generate_from_template("debt_heavy", project_budget)

        mezz_debts = [
            c.instrument for c in stack.components
            if isinstance(c.instrument, MezzanineDebt)
        ]

        if mezz_debts:  # Only test if mezzanine is present
            for debt in mezz_debts:
                assert debt.equity_kicker_percentage > 0

    def test_gap_financing_has_presales_requirement(self, generator, project_budget):
        """Test that GapFinancing has minimum pre-sales percentage."""
        stack = generator.generate_from_template("balanced", project_budget)

        gap_financing = [
            c.instrument for c in stack.components
            if isinstance(c.instrument, GapFinancing)
        ]

        if gap_financing:  # Only test if gap financing is present
            for gap in gap_financing:
                assert gap.minimum_presales_percentage > 0

    def test_tax_incentive_has_qualified_spend(self, generator, project_budget):
        """Test that TaxIncentive has qualified spend calculated."""
        stack = generator.generate_from_template("incentive_maximized", project_budget)

        incentives = [
            c.instrument for c in stack.components
            if isinstance(c.instrument, TaxIncentive)
        ]

        assert len(incentives) > 0

        for incentive in incentives:
            assert incentive.qualified_spend > 0
            assert incentive.credit_rate > 0

            # Verify: amount = qualified_spend * credit_rate / 100
            expected_amount = incentive.qualified_spend * (incentive.credit_rate / Decimal("100"))
            # Allow for larger tolerance due to rounding in template generation
            assert abs(incentive.amount - expected_amount) < incentive.amount * Decimal("0.05")  # 5% tolerance

    def test_presale_has_mg_amount(self, generator, project_budget):
        """Test that PreSale has MG amount set."""
        stack = generator.generate_from_template("presale_focused", project_budget)

        presales = [
            c.instrument for c in stack.components
            if isinstance(c.instrument, PreSale)
        ]

        assert len(presales) > 0

        for presale in presales:
            assert presale.mg_amount > 0
            assert presale.payment_on_delivery > 0

    # Edge Case Tests

    def test_generate_with_zero_allocation_instruments_excluded(self, generator, project_budget):
        """Test that instruments with 0% allocation are excluded."""
        customizations = {
            "allocations": {
                "mezzanine_debt": Decimal("0.0")  # Explicitly zero
            }
        }

        stack = generator.generate_from_template(
            "debt_heavy",
            project_budget,
            customizations=customizations
        )

        # Should not have mezzanine debt
        mezz_debts = [
            c.instrument for c in stack.components
            if isinstance(c.instrument, MezzanineDebt)
        ]

        # If mezzanine was in template, it should now be excluded or zero
        total_mezz = sum(d.amount for d in mezz_debts)
        assert total_mezz == 0

    def test_template_validation_warns_on_non_100_percent(self):
        """Test that template creation warns if allocations don't sum to 100%."""
        # This should log a warning but not fail
        template = FinancingTemplate(
            template_name="invalid_sum",
            description="Test invalid sum",
            target_allocations={
                "equity": Decimal("50.0"),
                "senior_debt": Decimal("30.0")  # Sums to 80%, not 100%
            },
            typical_terms={}
        )

        # Should create successfully (just warns)
        assert template.template_name == "invalid_sum"


class TestFinancingTemplate:
    """Test FinancingTemplate dataclass."""

    def test_template_creation(self):
        """Test creating a financing template."""
        template = FinancingTemplate(
            template_name="test_template",
            description="Test template",
            target_allocations={
                "equity": Decimal("60.0"),
                "senior_debt": Decimal("40.0")
            },
            typical_terms={
                "equity": {"ownership": 50.0}
            }
        )

        assert template.template_name == "test_template"
        assert template.description == "Test template"
        assert len(template.target_allocations) == 2

    def test_template_with_constraints(self):
        """Test template with constraints."""
        template = FinancingTemplate(
            template_name="test_constrained",
            description="Test with constraints",
            target_allocations={
                "equity": Decimal("50.0"),
                "senior_debt": Decimal("50.0")
            },
            typical_terms={},
            constraints={
                "max_leverage_ratio": Decimal("2.0")
            }
        )

        assert "max_leverage_ratio" in template.constraints
        assert template.constraints["max_leverage_ratio"] == Decimal("2.0")

    def test_template_with_use_cases(self):
        """Test template with use cases."""
        template = FinancingTemplate(
            template_name="test_use_cases",
            description="Test with use cases",
            target_allocations={
                "equity": Decimal("100.0")
            },
            typical_terms={},
            use_cases=[
                "First-time filmmakers",
                "Experimental content"
            ]
        )

        assert len(template.use_cases) == 2
        assert "First-time filmmakers" in template.use_cases


class TestScenarioConfig:
    """Test ScenarioConfig dataclass."""

    def test_scenario_config_creation(self):
        """Test creating a scenario config."""
        template = FinancingTemplate(
            template_name="test",
            description="Test",
            target_allocations={"equity": Decimal("100.0")},
            typical_terms={}
        )

        config = ScenarioConfig(
            scenario_name="test_scenario",
            template=template,
            project_budget=Decimal("30000000")
        )

        assert config.scenario_name == "test_scenario"
        assert config.template == template
        assert config.project_budget == Decimal("30000000")

    def test_scenario_config_with_customizations(self):
        """Test scenario config with customizations."""
        template = FinancingTemplate(
            template_name="test",
            description="Test",
            target_allocations={"equity": Decimal("100.0")},
            typical_terms={}
        )

        config = ScenarioConfig(
            scenario_name="test_scenario",
            template=template,
            project_budget=Decimal("30000000"),
            customizations={
                "allocations": {"equity": Decimal("80.0")}
            },
            jurisdiction_targets=["Canada", "UK"]
        )

        assert "allocations" in config.customizations
        assert len(config.jurisdiction_targets) == 2
