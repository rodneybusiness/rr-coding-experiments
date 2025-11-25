"""
Incentive Calculator

Core calculation engine for tax incentives in single and multi-jurisdiction scenarios.
Handles net benefit calculations, stacking logic, and comprehensive validation.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal

from models.incentive_policy import IncentivePolicy, MonetizationMethod
from models.project_profile import ProjectProfile
from .policy_registry import PolicyRegistry
from .labor_cap_enforcer import LaborCapEnforcer, LaborEnforcementResult


logger = logging.getLogger(__name__)


@dataclass
class JurisdictionSpend:
    """
    Spending allocation for a single jurisdiction.

    Represents how production budget is allocated to a specific jurisdiction,
    broken down by spend category for accurate incentive calculation.

    Attributes:
        jurisdiction: Country or region name
        policy_ids: List of policy IDs to apply (for stacking scenarios)
        qualified_spend: Total spend that qualifies for incentives
        total_spend: Total spend including non-qualified costs
        labor_spend: Spending on labor/personnel
        goods_services_spend: Spending on goods and services
        post_production_spend: Post-production spending
        vfx_animation_spend: VFX and animation-specific spending
    """
    jurisdiction: str
    policy_ids: List[str]
    qualified_spend: Decimal
    total_spend: Decimal
    labor_spend: Decimal = Decimal("0")
    goods_services_spend: Decimal = Decimal("0")
    post_production_spend: Decimal = Decimal("0")
    vfx_animation_spend: Decimal = Decimal("0")

    def __post_init__(self):
        """Validate spend allocations"""
        # Convert to Decimal if needed
        if not isinstance(self.qualified_spend, Decimal):
            self.qualified_spend = Decimal(str(self.qualified_spend))
        if not isinstance(self.total_spend, Decimal):
            self.total_spend = Decimal(str(self.total_spend))
        if not isinstance(self.labor_spend, Decimal):
            self.labor_spend = Decimal(str(self.labor_spend))
        if not isinstance(self.goods_services_spend, Decimal):
            self.goods_services_spend = Decimal(str(self.goods_services_spend))
        if not isinstance(self.post_production_spend, Decimal):
            self.post_production_spend = Decimal(str(self.post_production_spend))
        if not isinstance(self.vfx_animation_spend, Decimal):
            self.vfx_animation_spend = Decimal(str(self.vfx_animation_spend))

        # Validate qualified <= total
        if self.qualified_spend > self.total_spend:
            raise ValueError(
                f"Qualified spend ({self.qualified_spend}) cannot exceed "
                f"total spend ({self.total_spend}) for {self.jurisdiction}"
            )


@dataclass
class IncentiveResult:
    """
    Result of incentive calculation for one policy.

    Contains complete breakdown of gross credit, discounts, costs, and net benefit.

    Attributes:
        policy_id: Policy identifier
        jurisdiction: Country/region
        policy_name: Human-readable program name
        qualified_spend: Amount of qualified spend
        gross_credit: Gross incentive amount before adjustments
        transfer_discount: Discount rate if transferred (0-100)
        discount_amount: Dollar amount of discount
        tax_cost: Tax owed on incentive receipt
        audit_cost: Cost of required audit
        application_fee: Application/processing fee
        net_cash_benefit: Final net cash benefit
        effective_rate: Net benefit as % of qualified spend
        monetization_method: How incentive is monetized
        timing_months: Total months from completion to cash
        warnings: List of validation warnings
        metadata: Additional calculation details
    """
    policy_id: str
    jurisdiction: str
    policy_name: str
    qualified_spend: Decimal
    gross_credit: Decimal
    transfer_discount: Optional[Decimal]
    discount_amount: Decimal
    tax_cost: Decimal
    audit_cost: Decimal
    application_fee: Decimal
    net_cash_benefit: Decimal
    effective_rate: Decimal
    monetization_method: MonetizationMethod
    timing_months: int
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "policy_id": self.policy_id,
            "jurisdiction": self.jurisdiction,
            "policy_name": self.policy_name,
            "qualified_spend": str(self.qualified_spend),
            "gross_credit": str(self.gross_credit),
            "transfer_discount": str(self.transfer_discount) if self.transfer_discount else None,
            "discount_amount": str(self.discount_amount),
            "tax_cost": str(self.tax_cost),
            "audit_cost": str(self.audit_cost),
            "application_fee": str(self.application_fee),
            "net_cash_benefit": str(self.net_cash_benefit),
            "effective_rate": str(self.effective_rate),
            "monetization_method": self.monetization_method.value,
            "timing_months": self.timing_months,
            "warnings": self.warnings,
            "metadata": self.metadata
        }


@dataclass
class MultiJurisdictionResult:
    """
    Result of multi-jurisdiction calculation.

    Aggregates results across multiple jurisdictions with stacking applied.

    Attributes:
        total_budget: Total production budget
        total_qualified_spend: Sum of qualified spend across jurisdictions
        jurisdiction_results: List of per-jurisdiction results
        total_gross_credits: Sum of gross credits
        total_net_benefits: Sum of net benefits
        blended_effective_rate: Weighted average effective rate
        stacking_applied: List of stacking combinations used
        total_timing_weighted_months: Average timing weighted by benefit size
        warnings: List of validation warnings
    """
    total_budget: Decimal
    total_qualified_spend: Decimal
    jurisdiction_results: List[IncentiveResult]
    total_gross_credits: Decimal
    total_net_benefits: Decimal
    blended_effective_rate: Decimal
    stacking_applied: List[str]
    total_timing_weighted_months: Decimal
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "total_budget": str(self.total_budget),
            "total_qualified_spend": str(self.total_qualified_spend),
            "jurisdiction_results": [r.to_dict() for r in self.jurisdiction_results],
            "total_gross_credits": str(self.total_gross_credits),
            "total_net_benefits": str(self.total_net_benefits),
            "blended_effective_rate": str(self.blended_effective_rate),
            "stacking_applied": self.stacking_applied,
            "total_timing_weighted_months": str(self.total_timing_weighted_months),
            "warnings": self.warnings
        }


class IncentiveCalculator:
    """
    Core incentive calculation engine.

    Calculates tax incentive net benefits for single and multi-jurisdiction
    production scenarios with support for policy stacking and comprehensive
    validation.

    Attributes:
        registry: PolicyRegistry instance for policy lookup
    """

    def __init__(self, registry: PolicyRegistry):
        """
        Initialize calculator with policy registry.

        Args:
            registry: PolicyRegistry instance with loaded policies
        """
        self.registry = registry
        self.labor_enforcer = LaborCapEnforcer()
        logger.info("IncentiveCalculator initialized with LaborCapEnforcer")

    def calculate_single_jurisdiction(
        self,
        policy_id: str,
        jurisdiction_spend: JurisdictionSpend,
        monetization_method: MonetizationMethod,
        transfer_discount: Optional[Decimal] = None
    ) -> IncentiveResult:
        """
        Calculate incentive for a single policy.

        Args:
            policy_id: Policy identifier
            jurisdiction_spend: Spending allocation details
            monetization_method: How incentive will be monetized
            transfer_discount: Optional discount rate (0-100) for transfers/loans

        Returns:
            IncentiveResult with complete breakdown

        Raises:
            ValueError: If policy not found or validation fails
        """
        # Get policy
        policy = self.registry.get_by_id(policy_id)
        if not policy:
            raise ValueError(f"Policy not found: {policy_id}")

        warnings = []
        labor_cap_applied = False
        labor_cap_basis = None
        labor_enforcement_result: Optional[LaborEnforcementResult] = None

        # Normalize monetization method to allow aliases/derived strategies
        normalized_method = self._normalize_monetization_method(monetization_method, policy)

        # Validate monetization method is supported
        if normalized_method not in policy.monetization_methods and monetization_method not in policy.monetization_methods:
            raise ValueError(
                f"Monetization method {monetization_method.value} not supported by "
                f"policy {policy_id}. Supported methods: "
                f"{[m.value for m in policy.monetization_methods]}"
            )

        # Check minimum spend requirements
        if policy.minimum_total_spend and jurisdiction_spend.total_spend < policy.minimum_total_spend:
            warnings.append(
                f"Total spend ${jurisdiction_spend.total_spend:,.0f} is below minimum "
                f"required ${policy.minimum_total_spend:,.0f}"
            )

        if policy.minimum_local_spend and jurisdiction_spend.qualified_spend < policy.minimum_local_spend:
            warnings.append(
                f"Qualified spend ${jurisdiction_spend.qualified_spend:,.0f} is below "
                f"minimum required ${policy.minimum_local_spend:,.0f}"
            )

        # Check cultural test requirement
        if policy.cultural_test.requires_cultural_test:
            warnings.append(
                f"Cultural test required: {policy.cultural_test.test_name or 'See policy details'}"
            )

        # Check SPV requirement
        if policy.requires_local_spv:
            warnings.append(
                f"Local SPV required: {policy.spv_requirements or 'See policy details'}"
            )

        # Determine qualified spend for calculation
        # Check if we should use labor enforcer
        use_labor_enforcer = (
            self._has_labor_cap_rules(policy)
            and jurisdiction_spend.labor_spend > 0
        )

        if use_labor_enforcer:
            # Use LaborCapEnforcer for policies with labor cap rules
            labor_enforcement_result = self.labor_enforcer.enforce_labor_caps(
                policy=policy,
                qualified_spend=jurisdiction_spend.qualified_spend,
                labor_spend=jurisdiction_spend.labor_spend,
                vfx_labor_spend=jurisdiction_spend.vfx_animation_spend if jurisdiction_spend.vfx_animation_spend > 0 else None
            )

            # Use enforcer's adjusted amounts
            calc_spend = labor_enforcement_result.adjusted_qualified_spend
            labor_cap_applied = labor_enforcement_result.labor_cap_applied
            labor_cap_basis = labor_enforcement_result.adjusted_labor_spend

            # Add enforcer warnings to our warnings list
            warnings.extend(labor_enforcement_result.warnings)

            # For labor-enforced policies, we use the enforcer's credit calculation
            # to ensure consistency with labor cap logic
            gross_credit = labor_enforcement_result.total_credit

            # Calculate net benefit using policy's discount/tax logic
            calc_result = policy.calculate_net_benefit(
                qualified_spend=calc_spend,
                monetization_method=normalized_method,
                transfer_discount=transfer_discount
            )

            # Use policy's net benefit calculation but with enforcer's gross credit
            # Recalculate with enforcer's gross credit
            discount_factor = Decimal("1")
            if transfer_discount and transfer_discount > 0:
                discount_factor = Decimal("1") - (transfer_discount / Decimal("100"))

            net_benefit = gross_credit * discount_factor
            effective_rate = (net_benefit / calc_spend * Decimal("100")) if calc_spend > 0 else Decimal("0")

        else:
            # Use traditional calculation for policies without labor cap rules
            calc_spend = jurisdiction_spend.qualified_spend

            # Calculate gross credit using policy method
            calc_result = policy.calculate_net_benefit(
                qualified_spend=calc_spend,
                monetization_method=normalized_method,
                transfer_discount=transfer_discount
            )

            gross_credit = calc_result["gross_credit"]
            net_benefit = calc_result["net_cash_benefit"]
            effective_rate = calc_result["effective_rate"]

        # Extract components for detailed reporting
        discount_amount = Decimal("0")
        if transfer_discount and transfer_discount > 0:
            discount_amount = gross_credit * (transfer_discount / Decimal("100"))

        # Tax costs (if applicable)
        tax_cost = Decimal("0")
        if policy.is_taxable_income_federal and policy.federal_tax_rate:
            tax_cost += net_benefit * (policy.federal_tax_rate / Decimal("100"))
        if policy.is_taxable_income_local and policy.local_tax_rate:
            tax_cost += net_benefit * (policy.local_tax_rate / Decimal("100"))

        # Audit cost
        audit_cost = Decimal(str(policy.audit_cost_typical)) if policy.audit_cost_typical else Decimal("0")

        # Application fee
        application_fee = Decimal(str(policy.application_fee)) if policy.application_fee else Decimal("0")

        # Calculate timing
        timing_months = (
            (policy.timing_months_audit_to_certification or 0) +
            (policy.timing_months_certification_to_cash or 0)
        )

        # Adjust timing for loan/transfer (assume immediate)
        if monetization_method in [MonetizationMethod.TAX_CREDIT_LOAN, MonetizationMethod.TRANSFER_TO_INVESTOR]:
            timing_months = 1  # Assume 1 month for loan closing

        logger.info(
            f"Calculated {policy_id}: Qualified ${calc_spend:,.0f} → "
            f"Gross ${gross_credit:,.0f} → Net ${net_benefit:,.0f} ({effective_rate}%)"
        )

        # Build metadata
        metadata = {
            "per_project_cap": str(policy.per_project_cap) if policy.per_project_cap else None,
            "cap_applied": gross_credit == policy.per_project_cap if policy.per_project_cap else False,
            "labor_cap_basis": str(labor_cap_basis) if labor_cap_basis else None,
            "labor_cap_applied": labor_cap_applied
        }

        # Add labor enforcement details if enforcer was used
        if labor_enforcement_result:
            metadata["labor_enforcement"] = labor_enforcement_result.to_dict()

        return IncentiveResult(
            policy_id=policy_id,
            jurisdiction=policy.jurisdiction,
            policy_name=policy.program_name,
            qualified_spend=calc_spend,
            gross_credit=gross_credit,
            transfer_discount=transfer_discount,
            discount_amount=discount_amount,
            tax_cost=tax_cost,
            audit_cost=audit_cost,
            application_fee=application_fee,
            net_cash_benefit=net_benefit,
            effective_rate=effective_rate,
            monetization_method=monetization_method,
            timing_months=timing_months,
            warnings=warnings,
            metadata=metadata
        )

    @staticmethod
    def _normalize_monetization_method(
        monetization_method: MonetizationMethod,
        policy: IncentivePolicy
    ) -> MonetizationMethod:
        """
        Map alias/derived monetization methods to supported base methods for validation.

        TRANSFER_TO_INVESTOR → TRANSFER_SALE for transferable credits.
        TAX_CREDIT_LOAN → LOAN_COLLATERAL if explicitly supported, otherwise
        fall back to TRANSFER_SALE when transferable credits can be bridged.
        """
        if monetization_method == MonetizationMethod.TRANSFER_TO_INVESTOR:
            return MonetizationMethod.TRANSFER_SALE

        if monetization_method == MonetizationMethod.TAX_CREDIT_LOAN:
            if MonetizationMethod.LOAN_COLLATERAL in policy.monetization_methods:
                return MonetizationMethod.LOAN_COLLATERAL
            if MonetizationMethod.TRANSFER_SALE in policy.monetization_methods:
                return MonetizationMethod.TRANSFER_SALE

        return monetization_method

    @staticmethod
    def _has_labor_cap_rules(policy: IncentivePolicy) -> bool:
        """
        Check if policy has any labor-specific cap or rate rules.

        Returns:
            True if policy has labor caps, labor-only credit, or labor-specific rates
        """
        qpe = policy.qpe_definition
        return (
            qpe.labor_max_percent_of_spend is not None
            or qpe.labor_only_credit
            or qpe.labor_specific_rate is not None
            or qpe.labor_uplift_rate is not None
            or qpe.vfx_animation_rate is not None
        )

    def calculate_multi_jurisdiction(
        self,
        total_budget: Decimal,
        jurisdiction_spends: List[JurisdictionSpend],
        monetization_preferences: Dict[str, MonetizationMethod],
        transfer_discounts: Optional[Dict[str, Decimal]] = None
    ) -> MultiJurisdictionResult:
        """
        Calculate incentives across multiple jurisdictions.

        Args:
            total_budget: Total production budget
            jurisdiction_spends: List of spending allocations per jurisdiction
            monetization_preferences: Dict mapping policy_id to monetization method
            transfer_discounts: Optional dict mapping policy_id to discount rate

        Returns:
            MultiJurisdictionResult with aggregated data

        Raises:
            ValueError: If validation fails
        """
        if transfer_discounts is None:
            transfer_discounts = {}

        jurisdiction_results = []
        stacking_applied = []
        warnings = []

        # Calculate total qualified spend
        total_qualified = sum(js.qualified_spend for js in jurisdiction_spends)

        # Validate budget allocation
        total_allocated = sum(js.total_spend for js in jurisdiction_spends)
        if total_allocated != total_budget:
            warnings.append(
                f"Total allocated spend ${total_allocated:,.0f} does not match "
                f"budget ${total_budget:,.0f}"
            )

        # Process each jurisdiction
        for js in jurisdiction_spends:
            jurisdiction_policies = []

            # Calculate each policy for this jurisdiction
            for policy_id in js.policy_ids:
                monetization_method = monetization_preferences.get(
                    policy_id,
                    MonetizationMethod.DIRECT_CASH  # Default
                )
                transfer_discount = transfer_discounts.get(policy_id)

                result = self.calculate_single_jurisdiction(
                    policy_id=policy_id,
                    jurisdiction_spend=js,
                    monetization_method=monetization_method,
                    transfer_discount=transfer_discount
                )

                jurisdiction_policies.append(result)

            # Apply stacking rules if multiple policies for this jurisdiction
            if len(jurisdiction_policies) > 1:
                jurisdiction_policies, stacking_info = self._apply_stacking_rules(
                    jurisdiction=js.jurisdiction,
                    policy_results=jurisdiction_policies
                )
                if stacking_info:
                    stacking_applied.extend(stacking_info)

            jurisdiction_results.extend(jurisdiction_policies)

        # Aggregate results
        total_gross_credits = sum(r.gross_credit for r in jurisdiction_results)
        total_net_benefits = sum(r.net_cash_benefit for r in jurisdiction_results)

        # Calculate blended effective rate
        blended_effective_rate = (
            (total_net_benefits / total_qualified * Decimal("100"))
            if total_qualified > 0 else Decimal("0")
        )

        # Calculate weighted average timing
        total_timing_weighted = Decimal("0")
        for r in jurisdiction_results:
            weight = r.net_cash_benefit / total_net_benefits if total_net_benefits > 0 else Decimal("0")
            total_timing_weighted += Decimal(str(r.timing_months)) * weight

        # Collect all warnings
        for r in jurisdiction_results:
            warnings.extend(r.warnings)

        logger.info(
            f"Multi-jurisdiction calculation: {len(jurisdiction_spends)} jurisdictions, "
            f"{len(jurisdiction_results)} policies, total net benefit ${total_net_benefits:,.0f}"
        )

        return MultiJurisdictionResult(
            total_budget=total_budget,
            total_qualified_spend=total_qualified,
            jurisdiction_results=jurisdiction_results,
            total_gross_credits=total_gross_credits,
            total_net_benefits=total_net_benefits,
            blended_effective_rate=blended_effective_rate,
            stacking_applied=stacking_applied,
            total_timing_weighted_months=total_timing_weighted,
            warnings=warnings
        )

    def _apply_stacking_rules(
        self,
        jurisdiction: str,
        policy_results: List[IncentiveResult]
    ) -> tuple[List[IncentiveResult], List[str]]:
        """
        Apply stacking rules for jurisdictions with multiple policies.

        Known stacking scenarios:
        - Canada: Federal CPTC + Provincial (Quebec/Ontario) - OK, different bases
        - Australia: Producer Offset + PDV Offset - OK if criteria met

        Args:
            jurisdiction: Jurisdiction name
            policy_results: List of IncentiveResult objects

        Returns:
            Tuple of (adjusted results, stacking info strings)
        """
        stacking_info = []

        # Canada stacking: Federal + Provincial
        if jurisdiction.startswith("Canada"):
            federal_result = None
            provincial_result = None

            for result in policy_results:
                if "FEDERAL" in result.policy_id:
                    federal_result = result
                elif "QC" in result.policy_id or "ON" in result.policy_id:
                    provincial_result = result

            if federal_result and provincial_result:
                # Stacking is allowed - different tax bases
                # Federal is capped at 15% of budget, provincial has separate calculation
                stacking_info.append(
                    f"{jurisdiction}: {federal_result.policy_name} + "
                    f"{provincial_result.policy_name}"
                )
                logger.info(f"Applied Canada stacking rules for {jurisdiction}")

        # Australia stacking: Producer Offset + PDV Offset
        elif jurisdiction == "Australia":
            producer_result = None
            pdv_result = None

            for result in policy_results:
                if "PRODUCER" in result.policy_id:
                    producer_result = result
                elif "PDV" in result.policy_id:
                    pdv_result = result

            if producer_result and pdv_result:
                # Stacking allowed - different spend categories
                # Combined cap at 60% of qualifying spend
                combined_benefit = producer_result.net_cash_benefit + pdv_result.net_cash_benefit
                combined_qualified = producer_result.qualified_spend + pdv_result.qualified_spend

                # Check 60% cap
                cap_60_percent = combined_qualified * Decimal("0.60")
                if combined_benefit > cap_60_percent:
                    # Proportionally reduce both benefits
                    reduction_factor = cap_60_percent / combined_benefit

                    producer_result.net_cash_benefit *= reduction_factor
                    producer_result.gross_credit *= reduction_factor
                    producer_result.effective_rate = (
                        producer_result.net_cash_benefit /
                        producer_result.qualified_spend * Decimal("100")
                    )
                    producer_result.warnings.append(
                        "Benefit reduced due to 60% combined stacking cap"
                    )

                    pdv_result.net_cash_benefit *= reduction_factor
                    pdv_result.gross_credit *= reduction_factor
                    pdv_result.effective_rate = (
                        pdv_result.net_cash_benefit /
                        pdv_result.qualified_spend * Decimal("100")
                    )
                    pdv_result.warnings.append(
                        "Benefit reduced due to 60% combined stacking cap"
                    )

                stacking_info.append(
                    f"Australia: Producer Offset + PDV Offset (60% cap applied)"
                )
                logger.info("Applied Australia stacking rules with 60% cap")

        return policy_results, stacking_info

    def validate_cultural_test_requirements(
        self,
        policy: IncentivePolicy,
        project_profile: Optional[ProjectProfile] = None
    ) -> Dict[str, any]:
        """
        Check if project would pass cultural test.

        If project_profile provided, attempts to assess likelihood of passing.
        Otherwise, returns requirements information.

        Args:
            policy: IncentivePolicy to check
            project_profile: Optional ProjectProfile with project details

        Returns:
            Dict with cultural test assessment:
            {
                "requires_test": bool,
                "test_name": str,
                "likely_passes": Optional[bool],
                "notes": str
            }
        """
        result = {
            "requires_test": policy.cultural_test.requires_cultural_test,
            "test_name": policy.cultural_test.test_name,
            "likely_passes": None,
            "notes": ""
        }

        if not policy.cultural_test.requires_cultural_test:
            result["notes"] = "No cultural test required"
            return result

        # If project profile provided, attempt basic assessment
        if project_profile:
            # This is simplified - real assessment would require detailed scoring
            result["notes"] = (
                "Cultural test assessment requires detailed point calculation. "
                "Consult policy documentation: "
                f"{policy.cultural_test.test_details_url or policy.program_url}"
            )
        else:
            result["notes"] = (
                f"Cultural test required: {policy.cultural_test.test_name}. "
                f"See: {policy.cultural_test.test_details_url or policy.program_url}"
            )

        return result
