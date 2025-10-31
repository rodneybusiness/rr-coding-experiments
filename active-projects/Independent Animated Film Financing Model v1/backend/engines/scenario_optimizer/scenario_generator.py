"""
Scenario Generator

Generates diverse financing scenarios from templates and custom configurations.
Provides 5 default templates: debt-heavy, equity-heavy, balanced, pre-sale focused, and incentive-maximized.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal
from copy import deepcopy

from backend.models.capital_stack import CapitalStack, CapitalComponent
from backend.models.financial_instruments import (
    Equity, SeniorDebt, MezzanineDebt, GapFinancing, PreSale, TaxIncentive
)

logger = logging.getLogger(__name__)


@dataclass
class FinancingTemplate:
    """
    Template for financing structure.

    Attributes:
        template_name: Template identifier
        description: Human-readable description
        target_allocations: Target % for each instrument type
        typical_terms: Typical terms for each instrument
        constraints: Default constraints for this template
        use_cases: When to use this template
    """
    template_name: str
    description: str
    target_allocations: Dict[str, Decimal]  # instrument_type -> percentage
    typical_terms: Dict[str, Dict[str, Any]]  # instrument_type -> terms dict
    constraints: Dict[str, Any] = field(default_factory=dict)
    use_cases: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate that allocations sum to ~100%"""
        total = sum(self.target_allocations.values())
        if not (Decimal("99.0") <= total <= Decimal("101.0")):
            logger.warning(f"Template '{self.template_name}' allocations sum to {total}%, not 100%")


@dataclass
class ScenarioConfig:
    """
    Configuration for generating a specific scenario.

    Attributes:
        scenario_name: Scenario identifier
        template: Base template to use
        project_budget: Total project budget
        customizations: Custom allocations or terms to override template
        jurisdiction_targets: Target jurisdictions for tax incentives
        metadata: Additional scenario metadata
    """
    scenario_name: str
    template: FinancingTemplate
    project_budget: Decimal
    customizations: Dict[str, Any] = field(default_factory=dict)
    jurisdiction_targets: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScenarioGenerator:
    """
    Generate diverse financing scenarios from templates.

    Provides 5 default templates and supports custom template creation.
    Generates complete CapitalStack objects ready for optimization and evaluation.
    """

    def __init__(self):
        """Initialize with default templates."""
        self.templates = self._load_default_templates()
        logger.info(f"ScenarioGenerator initialized with {len(self.templates)} templates")

    def generate_from_template(
        self,
        template_name: str,
        project_budget: Decimal,
        scenario_name: Optional[str] = None,
        customizations: Optional[Dict[str, Any]] = None
    ) -> CapitalStack:
        """
        Generate capital stack from template.

        Args:
            template_name: Name of template to use
            project_budget: Total project budget
            scenario_name: Custom scenario name (defaults to template name)
            customizations: Custom allocations or terms

        Returns:
            CapitalStack ready for evaluation

        Raises:
            ValueError: If template not found
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.templates.keys())}")

        template = self.templates[template_name]
        scenario_name = scenario_name or f"{template_name}_scenario"

        # Apply customizations to allocations
        allocations = deepcopy(template.target_allocations)
        if customizations and "allocations" in customizations:
            allocations.update(customizations["allocations"])

        # Generate components
        components = []
        position = 1

        # Senior Debt (if present)
        if "senior_debt" in allocations and allocations["senior_debt"] > Decimal("0"):
            amount = (allocations["senior_debt"] / Decimal("100")) * project_budget
            terms = template.typical_terms.get("senior_debt", {})

            senior_debt = SeniorDebt(
                amount=amount,
                interest_rate=Decimal(str(terms.get("interest_rate", 8.0))),
                term_months=int(terms.get("term_months", 24)),
                origination_fee_percentage=Decimal(str(terms.get("origination_fee", 2.0)))
            )
            components.append(CapitalComponent(instrument=senior_debt, position=position))
            position += 1

        # Mezzanine Debt (if present)
        if "mezzanine_debt" in allocations and allocations["mezzanine_debt"] > Decimal("0"):
            amount = (allocations["mezzanine_debt"] / Decimal("100")) * project_budget
            terms = template.typical_terms.get("mezzanine_debt", {})

            mezz_debt = MezzanineDebt(
                amount=amount,
                interest_rate=Decimal(str(terms.get("interest_rate", 12.0))),
                term_months=int(terms.get("term_months", 36)),
                equity_kicker_percentage=Decimal(str(terms.get("equity_kicker", 5.0)))
            )
            components.append(CapitalComponent(instrument=mezz_debt, position=position))
            position += 1

        # Gap Financing (if present)
        if "gap_financing" in allocations and allocations["gap_financing"] > Decimal("0"):
            amount = (allocations["gap_financing"] / Decimal("100")) * project_budget
            terms = template.typical_terms.get("gap_financing", {})

            gap = GapFinancing(
                amount=amount,
                interest_rate=Decimal(str(terms.get("interest_rate", 10.0))),
                term_months=int(terms.get("term_months", 24)),
                minimum_presales_percentage=Decimal(str(terms.get("min_presales", 30.0)))
            )
            components.append(CapitalComponent(instrument=gap, position=position))
            position += 1

        # Pre-Sales (if present)
        if "pre_sales" in allocations and allocations["pre_sales"] > Decimal("0"):
            amount = (allocations["pre_sales"] / Decimal("100")) * project_budget
            terms = template.typical_terms.get("pre_sales", {})

            presale = PreSale(
                amount=amount,
                territory=terms.get("territory", "Worldwide"),
                rights_description=terms.get("rights_description", "All Rights"),
                mg_amount=amount,  # MG amount equals the amount
                payment_on_delivery=amount * Decimal("0.8")  # 80% on delivery
            )
            components.append(CapitalComponent(instrument=presale, position=position))
            position += 1

        # Tax Incentives (if present)
        if "tax_incentives" in allocations and allocations["tax_incentives"] > Decimal("0"):
            amount = (allocations["tax_incentives"] / Decimal("100")) * project_budget
            terms = template.typical_terms.get("tax_incentives", {})

            incentive = TaxIncentive(
                amount=amount,
                jurisdiction=terms.get("jurisdiction", "Multi-Jurisdiction"),
                qualified_spend=amount / Decimal(str(terms.get("credit_rate", 0.30))),
                credit_rate=Decimal(str(terms.get("credit_rate", 30.0))),
                timing_months=int(terms.get("timing_months", 18))
            )
            components.append(CapitalComponent(instrument=incentive, position=position))
            position += 1

        # Equity (usually last)
        if "equity" in allocations and allocations["equity"] > Decimal("0"):
            amount = (allocations["equity"] / Decimal("100")) * project_budget
            terms = template.typical_terms.get("equity", {})

            equity = Equity(
                amount=amount,
                ownership_percentage=Decimal(str(terms.get("ownership", 100.0))),
                premium_percentage=Decimal(str(terms.get("premium", 20.0)))
            )
            components.append(CapitalComponent(instrument=equity, position=position))
            position += 1

        # Create capital stack
        stack = CapitalStack(
            stack_name=scenario_name,
            project_budget=project_budget,
            components=components
        )

        logger.info(f"Generated scenario '{scenario_name}' with {len(components)} components")

        return stack

    def generate_multiple_scenarios(
        self,
        project_budget: Decimal,
        template_names: Optional[List[str]] = None
    ) -> List[CapitalStack]:
        """
        Generate multiple scenarios from different templates.

        Args:
            project_budget: Total project budget
            template_names: Templates to use (defaults to all)

        Returns:
            List of CapitalStack scenarios
        """
        if template_names is None:
            template_names = list(self.templates.keys())

        scenarios = []
        for template_name in template_names:
            try:
                stack = self.generate_from_template(template_name, project_budget)
                scenarios.append(stack)
            except Exception as e:
                logger.error(f"Failed to generate scenario from template '{template_name}': {e}")

        logger.info(f"Generated {len(scenarios)} scenarios from {len(template_names)} templates")

        return scenarios

    def add_custom_template(self, template: FinancingTemplate):
        """
        Add custom template to generator.

        Args:
            template: Custom FinancingTemplate
        """
        self.templates[template.template_name] = template
        logger.info(f"Added custom template '{template.template_name}'")

    def get_template(self, template_name: str) -> Optional[FinancingTemplate]:
        """Get template by name."""
        return self.templates.get(template_name)

    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())

    def _load_default_templates(self) -> Dict[str, FinancingTemplate]:
        """
        Load 5 default financing templates.

        Returns:
            Dict mapping template_name → FinancingTemplate
        """
        templates = {}

        # Template 1: Debt-Heavy
        templates["debt_heavy"] = FinancingTemplate(
            template_name="debt_heavy",
            description="Maximizes debt financing to preserve equity ownership",
            target_allocations={
                "senior_debt": Decimal("50.0"),
                "mezzanine_debt": Decimal("20.0"),
                "equity": Decimal("20.0"),
                "pre_sales": Decimal("5.0"),
                "tax_incentives": Decimal("5.0")
            },
            typical_terms={
                "senior_debt": {
                    "interest_rate": 8.0,
                    "term_months": 24,
                    "origination_fee": 2.0
                },
                "mezzanine_debt": {
                    "interest_rate": 12.0,
                    "term_months": 36,
                    "equity_kicker": 5.0
                },
                "equity": {
                    "ownership": 80.0,  # High ownership retained
                    "premium": 25.0
                },
                "pre_sales": {
                    "buyer_name": "Regional Broadcaster",
                    "territory": "Europe",
                    "rights_term": 7,
                    "discount_rate": 15.0
                },
                "tax_incentives": {
                    "jurisdiction": "Multi-Jurisdiction",
                    "credit_rate": 30.0,
                    "timing_months": 18
                }
            },
            constraints={
                "min_debt_service_coverage": Decimal("1.25"),
                "max_leverage_ratio": Decimal("3.5")
            },
            use_cases=[
                "Producer wants to retain creative control",
                "Strong pre-sales or distribution guarantees",
                "Confidence in revenue projections"
            ]
        )

        # Template 2: Equity-Heavy
        templates["equity_heavy"] = FinancingTemplate(
            template_name="equity_heavy",
            description="Minimizes debt to reduce financial risk",
            target_allocations={
                "senior_debt": Decimal("20.0"),
                "equity": Decimal("60.0"),
                "pre_sales": Decimal("10.0"),
                "tax_incentives": Decimal("10.0")
            },
            typical_terms={
                "senior_debt": {
                    "interest_rate": 7.0,
                    "term_months": 24,
                    "origination_fee": 1.5
                },
                "equity": {
                    "ownership": 40.0,  # Lower ownership retained
                    "premium": 20.0
                },
                "pre_sales": {
                    "buyer_name": "SVOD Platform",
                    "territory": "North America",
                    "rights_term": 10,
                    "discount_rate": 12.0
                },
                "tax_incentives": {
                    "jurisdiction": "Multi-Jurisdiction",
                    "credit_rate": 35.0,
                    "timing_months": 15
                }
            },
            constraints={
                "min_equity_percentage": Decimal("50.0"),
                "max_debt_ratio": Decimal("0.35")
            },
            use_cases=[
                "First-time filmmaker with uncertain revenue",
                "Innovative/experimental content",
                "Risk-averse investors"
            ]
        )

        # Template 3: Balanced
        templates["balanced"] = FinancingTemplate(
            template_name="balanced",
            description="Balanced mix of debt, equity, and alternative financing",
            target_allocations={
                "senior_debt": Decimal("30.0"),
                "gap_financing": Decimal("15.0"),
                "equity": Decimal("35.0"),
                "pre_sales": Decimal("10.0"),
                "tax_incentives": Decimal("10.0")
            },
            typical_terms={
                "senior_debt": {
                    "interest_rate": 8.0,
                    "term_months": 24,
                    "origination_fee": 2.0
                },
                "gap_financing": {
                    "interest_rate": 10.0,
                    "term_months": 24,
                    "min_presales": 30.0
                },
                "equity": {
                    "ownership": 60.0,
                    "premium": 20.0
                },
                "pre_sales": {
                    "buyer_name": "International Distributor",
                    "territory": "APAC",
                    "rights_term": 10,
                    "discount_rate": 15.0
                },
                "tax_incentives": {
                    "jurisdiction": "Multi-Jurisdiction",
                    "credit_rate": 32.0,
                    "timing_months": 16
                }
            },
            constraints={
                "min_equity_percentage": Decimal("30.0"),
                "max_debt_ratio": Decimal("0.55")
            },
            use_cases=[
                "Standard commercial animation project",
                "Moderate risk tolerance",
                "Diverse investor base"
            ]
        )

        # Template 4: Pre-Sale Focused
        templates["presale_focused"] = FinancingTemplate(
            template_name="presale_focused",
            description="Maximizes pre-sales and distribution commitments",
            target_allocations={
                "senior_debt": Decimal("25.0"),
                "gap_financing": Decimal("5.0"),
                "equity": Decimal("25.0"),
                "pre_sales": Decimal("35.0"),
                "tax_incentives": Decimal("10.0")
            },
            typical_terms={
                "senior_debt": {
                    "interest_rate": 7.5,
                    "term_months": 24,
                    "origination_fee": 1.5
                },
                "gap_financing": {
                    "interest_rate": 9.0,
                    "term_months": 24,
                    "min_presales": 40.0
                },
                "equity": {
                    "ownership": 70.0,
                    "premium": 15.0
                },
                "pre_sales": {
                    "buyer_name": "Global SVOD Platform",
                    "territory": "Worldwide",
                    "rights_term": 15,
                    "discount_rate": 10.0
                },
                "tax_incentives": {
                    "jurisdiction": "Multi-Jurisdiction",
                    "credit_rate": 30.0,
                    "timing_months": 18
                }
            },
            constraints={
                "min_presales_percentage": Decimal("30.0"),
                "max_debt_ratio": Decimal("0.40")
            },
            use_cases=[
                "Strong IP with high market demand",
                "Established distribution relationships",
                "Platform exclusive deals"
            ]
        )

        # Template 5: Incentive-Maximized
        templates["incentive_maximized"] = FinancingTemplate(
            template_name="incentive_maximized",
            description="Maximizes tax incentives through multi-jurisdiction production",
            target_allocations={
                "senior_debt": Decimal("30.0"),
                "gap_financing": Decimal("5.0"),
                "equity": Decimal("30.0"),
                "pre_sales": Decimal("10.0"),
                "tax_incentives": Decimal("25.0")
            },
            typical_terms={
                "senior_debt": {
                    "interest_rate": 8.0,
                    "term_months": 24,
                    "origination_fee": 2.0
                },
                "gap_financing": {
                    "interest_rate": 10.0,
                    "term_months": 24,
                    "min_presales": 25.0
                },
                "equity": {
                    "ownership": 65.0,
                    "premium": 20.0
                },
                "pre_sales": {
                    "buyer_name": "Territory Distributor",
                    "territory": "Latin America",
                    "rights_term": 10,
                    "discount_rate": 15.0
                },
                "tax_incentives": {
                    "jurisdiction": "Multi-Jurisdiction (Canada Federal+Quebec, Australia)",
                    "credit_rate": 40.0,  # Stacked rate
                    "timing_months": 20
                }
            },
            constraints={
                "min_tax_incentive_percentage": Decimal("20.0"),
                "max_debt_ratio": Decimal("0.45")
            },
            use_cases=[
                "Production can leverage multiple jurisdictions",
                "Significant labor spend qualifies for incentives",
                "Long production timeline accommodates incentive timing"
            ]
        )

        logger.info(f"Loaded {len(templates)} default templates")

        return templates


# Export default templates for easy access
DEFAULT_TEMPLATES = [
    "debt_heavy",
    "equity_heavy",
    "balanced",
    "presale_focused",
    "incentive_maximized"
]
