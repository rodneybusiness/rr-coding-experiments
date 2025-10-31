"""
Incentive Policy Models - Tax credits, rebates, and subsidies

This module defines the structure for jurisdictional tax incentives
and their calculation mechanics.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class IncentiveType(str, Enum):
    """Types of tax incentives"""
    REFUNDABLE_TAX_CREDIT = "refundable_tax_credit"
    TRANSFERABLE_TAX_CREDIT = "transferable_tax_credit"
    NON_REFUNDABLE_TAX_CREDIT = "non_refundable_tax_credit"
    REBATE = "rebate"
    GRANT = "grant"
    SUBSIDY = "subsidy"


class MonetizationMethod(str, Enum):
    """How the incentive is converted to cash"""
    DIRECT_CASH = "direct_cash"  # Refundable credits, rebates
    TRANSFER_SALE = "transfer_sale"  # Sold to third party
    TAX_LIABILITY_OFFSET = "tax_liability_offset"  # Offset against taxes owed
    LOAN_COLLATERAL = "loan_collateral"  # Used as security for loan


class QPECategory(str, Enum):
    """Qualified Production Expenditure categories"""
    LABOR_RESIDENT = "labor_resident"
    LABOR_NON_RESIDENT = "labor_non_resident"
    GOODS_SERVICES_LOCAL = "goods_services_local"
    GOODS_SERVICES_IMPORTED = "goods_services_imported"
    POST_PRODUCTION = "post_production"
    VFX_ANIMATION = "vfx_animation"
    DEVELOPMENT_COSTS = "development_costs"


class QPEDefinition(BaseModel):
    """Definition of Qualified Production Expenditure (QPE/QAPE)"""

    # Inclusions
    included_categories: List[QPECategory] = Field(
        ..., description="Categories of spend that qualify"
    )

    # Exclusions (common)
    excludes_financing_costs: bool = Field(default=True)
    excludes_distribution_costs: bool = Field(default=True)
    excludes_completion_bond: bool = Field(default=True)
    excludes_insurance: bool = Field(default=False)

    # Caps and limits
    labor_cap_per_person: Optional[Decimal] = Field(
        default=None, description="Max qualifying amount per individual"
    )

    # Residency/local requirements
    minimum_local_labor_percentage: Optional[Decimal] = Field(
        default=None, ge=0, le=100, description="Required % of local crew/cast"
    )

    minimum_local_spend_percentage: Optional[Decimal] = Field(
        default=None, ge=0, le=100, description="Required % spent in jurisdiction"
    )

    # Additional notes
    special_rules: Optional[str] = None


class CulturalTest(BaseModel):
    """Cultural test requirements (common in EU/Canada/UK)"""

    requires_cultural_test: bool = Field(default=False)
    test_name: Optional[str] = Field(default=None, description="e.g., 'BFI Cultural Test', 'Canadian Content Points'")

    # Points system
    minimum_points_required: Optional[int] = None
    total_points_available: Optional[int] = None

    # Categories (simplified - actual tests are more complex)
    points_for_setting: Optional[int] = None
    points_for_characters: Optional[int] = None
    points_for_creative_team: Optional[int] = None
    points_for_production: Optional[int] = None

    test_details_url: Optional[str] = None


class IncentivePolicy(BaseModel):
    """Complete definition of a jurisdictional tax incentive program"""

    # Identification
    policy_id: str = Field(..., description="Unique identifier")
    jurisdiction: str = Field(..., description="Country or state/province")
    program_name: str = Field(..., description="Official program name")

    # Rates
    headline_rate: Decimal = Field(..., ge=0, le=100, description="Nominal rate %")
    enhanced_rate: Optional[Decimal] = Field(default=None, ge=0, le=100, description="Enhanced rate for qualifying criteria")

    incentive_type: IncentiveType

    # Base calculation
    qpe_definition: QPEDefinition

    # Caps
    per_project_cap: Optional[Decimal] = Field(default=None, description="Maximum per project")
    annual_program_cap: Optional[Decimal] = Field(default=None, description="Annual budget for entire program")
    per_applicant_annual_cap: Optional[Decimal] = Field(default=None, description="Max per production company per year")

    # Minimum spend
    minimum_total_spend: Optional[Decimal] = Field(default=None, description="Minimum budget to qualify")
    minimum_local_spend: Optional[Decimal] = Field(default=None, description="Minimum spend in jurisdiction")

    # Cultural/Content tests
    cultural_test: Optional[CulturalTest] = None

    # Entity requirements
    requires_local_spv: bool = Field(default=False, description="Must use local company")
    spv_requirements: Optional[str] = None

    # Monetization
    monetization_methods: List[MonetizationMethod] = Field(..., description="How credit can be monetized")

    # If transferable
    typical_transfer_discount_low: Optional[Decimal] = Field(default=None, ge=0, le=100, description="Low end of transfer discount %")
    typical_transfer_discount_high: Optional[Decimal] = Field(default=None, ge=0, le=100, description="High end of transfer discount %")

    # Timing
    timing_months_audit_to_certification: int = Field(default=6, description="Months from production end to certification")
    timing_months_certification_to_cash: int = Field(default=3, description="Months from cert to cash receipt")

    # Tax treatment
    is_taxable_income_federal: bool = Field(default=True, description="Is credit taxable as income?")
    is_taxable_income_local: bool = Field(default=False, description="Is credit taxable locally?")

    federal_tax_rate: Optional[Decimal] = Field(default=None, ge=0, le=100, description="Applicable federal tax rate %")
    local_tax_rate: Optional[Decimal] = Field(default=None, ge=0, le=100, description="Applicable local tax rate %")

    # Administrative
    audit_cost_typical: Optional[Decimal] = Field(default=None, description="Typical cost of required audit")
    application_fee: Optional[Decimal] = Field(default=None, description="Application fee if any")

    # Metadata
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    program_url: Optional[str] = None
    last_updated: date = Field(..., description="When this data was last updated")

    notes: Optional[str] = None

    def calculate_net_benefit(
        self,
        qualified_spend: Decimal,
        monetization_method: MonetizationMethod,
        transfer_discount: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate the net cash benefit from this incentive

        Args:
            qualified_spend: Total QPE amount
            monetization_method: How the credit will be monetized
            transfer_discount: If transferring, the discount % (0-100)

        Returns:
            Dictionary with gross_credit, net_credit, discount_amount, tax_cost, net_cash_benefit
        """

        # Calculate gross credit
        gross_credit = qualified_spend * (self.headline_rate / 100)

        # Apply per-project cap if exists
        if self.per_project_cap and gross_credit > self.per_project_cap:
            gross_credit = self.per_project_cap

        # Calculate discount if transferring
        discount_amount = Decimal("0")
        if monetization_method == MonetizationMethod.TRANSFER_SALE:
            if transfer_discount is None:
                # Use midpoint of typical range
                if self.typical_transfer_discount_low and self.typical_transfer_discount_high:
                    transfer_discount = (self.typical_transfer_discount_low + self.typical_transfer_discount_high) / 2
                else:
                    raise ValueError("Transfer discount must be provided for transfer sale")

            discount_amount = gross_credit * (transfer_discount / 100)

        net_credit = gross_credit - discount_amount

        # Calculate tax cost (if credit is taxable income)
        tax_cost = Decimal("0")
        if self.is_taxable_income_federal and self.federal_tax_rate:
            tax_cost += net_credit * (self.federal_tax_rate / 100)

        if self.is_taxable_income_local and self.local_tax_rate:
            tax_cost += net_credit * (self.local_tax_rate / 100)

        # Calculate net cash benefit
        net_cash_benefit = net_credit - tax_cost

        # Subtract audit costs if applicable
        if self.audit_cost_typical:
            net_cash_benefit -= self.audit_cost_typical

        return {
            "qualified_spend": qualified_spend,
            "gross_credit": gross_credit,
            "discount_amount": discount_amount,
            "net_credit": net_credit,
            "tax_cost": tax_cost,
            "audit_cost": self.audit_cost_typical or Decimal("0"),
            "net_cash_benefit": net_cash_benefit,
            "effective_rate": (net_cash_benefit / qualified_spend * 100) if qualified_spend > 0 else Decimal("0")
        }

    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "UK-AVEC-2025",
                "jurisdiction": "United Kingdom",
                "program_name": "Audio-Visual Expenditure Credit (AVEC)",
                "headline_rate": "34",
                "incentive_type": "refundable_tax_credit",
                "qpe_definition": {
                    "included_categories": ["labor_resident", "goods_services_local"],
                    "excludes_financing_costs": True
                },
                "monetization_methods": ["direct_cash", "loan_collateral"],
                "last_updated": "2025-10-31"
            }
        }
