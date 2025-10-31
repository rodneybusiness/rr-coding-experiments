"""
Monetization Comparator

Compares different monetization strategies for tax incentives to identify
optimal approach considering net proceeds, timing, and time value of money.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
import math

from backend.models.incentive_policy import MonetizationMethod
from backend.engines.incentive_calculator.calculator import (
    IncentiveCalculator,
    JurisdictionSpend,
)
from backend.engines.incentive_calculator.policy_registry import PolicyRegistry


logger = logging.getLogger(__name__)


@dataclass
class MonetizationScenario:
    """
    Single monetization strategy.

    Attributes:
        strategy_name: Human-readable strategy name
        monetization_method: Method used
        gross_credit: Gross incentive amount
        discount_rate: Transfer discount or loan fee (0-100)
        discount_amount: Dollar amount of discount/fee
        net_proceeds: Net cash proceeds
        timing_months: Months to receipt
        effective_rate: Net proceeds as % of qualified spend
        notes: Additional details
    """
    strategy_name: str
    monetization_method: MonetizationMethod
    gross_credit: Decimal
    discount_rate: Decimal
    discount_amount: Decimal
    net_proceeds: Decimal
    timing_months: int
    effective_rate: Decimal
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "strategy_name": self.strategy_name,
            "monetization_method": self.monetization_method.value,
            "gross_credit": str(self.gross_credit),
            "discount_rate": str(self.discount_rate),
            "discount_amount": str(self.discount_amount),
            "net_proceeds": str(self.net_proceeds),
            "timing_months": self.timing_months,
            "effective_rate": str(self.effective_rate),
            "notes": self.notes
        }


@dataclass
class MonetizationComparison:
    """
    Comparison of multiple monetization strategies.

    Attributes:
        policy_id: Policy being analyzed
        policy_name: Program name
        qualified_spend: Amount of qualified spend
        scenarios: List of scenarios
        recommended_strategy: Name of recommended strategy
        recommendation_reason: Explanation of recommendation
    """
    policy_id: str
    policy_name: str
    qualified_spend: Decimal
    scenarios: List[MonetizationScenario]
    recommended_strategy: str
    recommendation_reason: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "policy_id": self.policy_id,
            "policy_name": self.policy_name,
            "qualified_spend": str(self.qualified_spend),
            "scenarios": [s.to_dict() for s in self.scenarios],
            "recommended_strategy": self.recommended_strategy,
            "recommendation_reason": self.recommendation_reason
        }


class MonetizationComparator:
    """
    Compare monetization strategies for tax incentives.

    Analyzes different ways to monetize incentives (direct cash, transfer,
    loan, offset) and recommends optimal approach.

    Attributes:
        calculator: IncentiveCalculator instance
        registry: PolicyRegistry instance
    """

    # Default market rates (from rate_card_2025.json)
    DEFAULT_TRANSFER_DISCOUNT = Decimal("20.0")  # 20%
    DEFAULT_LOAN_FEE = Decimal("10.0")  # 10%

    def __init__(self, calculator: IncentiveCalculator):
        """
        Initialize with calculator reference.

        Args:
            calculator: IncentiveCalculator instance
        """
        self.calculator = calculator
        self.registry = calculator.registry
        logger.info("MonetizationComparator initialized")

    def compare_strategies(
        self,
        policy_id: str,
        qualified_spend: Decimal,
        jurisdiction_spend: JurisdictionSpend,
        strategies: Optional[List[MonetizationMethod]] = None,
        transfer_discount: Optional[Decimal] = None,
        loan_fee: Optional[Decimal] = None
    ) -> MonetizationComparison:
        """
        Compare available monetization strategies for a policy.

        Args:
            policy_id: Policy to analyze
            qualified_spend: Amount of qualified spend
            jurisdiction_spend: Full spending detail
            strategies: List of strategies to compare (if None, use all supported)
            transfer_discount: Custom transfer discount rate (uses default if None)
            loan_fee: Custom loan fee rate (uses default if None)

        Returns:
            MonetizationComparison with all scenarios

        Raises:
            ValueError: If policy not found
        """
        # Get policy
        policy = self.registry.get_by_id(policy_id)
        if not policy:
            raise ValueError(f"Policy not found: {policy_id}")

        # Use policy's supported methods if not specified
        if strategies is None:
            strategies = policy.monetization_methods

        # Use default rates if not provided
        if transfer_discount is None:
            transfer_discount = self.DEFAULT_TRANSFER_DISCOUNT
        if loan_fee is None:
            loan_fee = self.DEFAULT_LOAN_FEE

        scenarios = []

        for method in strategies:
            if method not in policy.monetization_methods:
                logger.warning(
                    f"Skipping {method.value} - not supported by policy {policy_id}"
                )
                continue

            # Determine discount rate for this method
            discount_rate = Decimal("0")
            if method == MonetizationMethod.TRANSFER_TO_INVESTOR:
                discount_rate = transfer_discount
            elif method == MonetizationMethod.TAX_CREDIT_LOAN:
                discount_rate = loan_fee

            # Calculate result
            result = self.calculator.calculate_single_jurisdiction(
                policy_id=policy_id,
                jurisdiction_spend=jurisdiction_spend,
                monetization_method=method,
                transfer_discount=discount_rate if discount_rate > 0 else None
            )

            # Create scenario
            scenario = MonetizationScenario(
                strategy_name=self._get_strategy_name(method),
                monetization_method=method,
                gross_credit=result.gross_credit,
                discount_rate=discount_rate,
                discount_amount=result.discount_amount,
                net_proceeds=result.net_cash_benefit,
                timing_months=result.timing_months,
                effective_rate=result.effective_rate,
                notes=self._get_strategy_notes(method, policy)
            )

            scenarios.append(scenario)

        # Sort by net proceeds (descending)
        scenarios.sort(key=lambda s: s.net_proceeds, reverse=True)

        # Determine recommendation
        recommended_strategy, recommendation_reason = self._recommend_strategy(
            scenarios=scenarios,
            policy=policy
        )

        logger.info(
            f"Compared {len(scenarios)} monetization strategies for {policy_id}. "
            f"Recommended: {recommended_strategy}"
        )

        return MonetizationComparison(
            policy_id=policy_id,
            policy_name=policy.program_name,
            qualified_spend=qualified_spend,
            scenarios=scenarios,
            recommended_strategy=recommended_strategy,
            recommendation_reason=recommendation_reason
        )

    def optimal_strategy(
        self,
        comparison: MonetizationComparison,
        time_value_discount_rate: Optional[Decimal] = None
    ) -> MonetizationScenario:
        """
        Select optimal strategy considering time value of money.

        Args:
            comparison: MonetizationComparison to analyze
            time_value_discount_rate: Annual discount rate (e.g., 0.12 for 12%)
                                     If provided, adjusts for timing differences

        Returns:
            MonetizationScenario that maximizes NPV
        """
        if not comparison.scenarios:
            raise ValueError("No scenarios to compare")

        if time_value_discount_rate is None:
            # Without time value, just return highest net proceeds
            return comparison.scenarios[0]  # Already sorted by net proceeds

        # Calculate NPV for each scenario
        scenarios_with_npv = []

        for scenario in comparison.scenarios:
            # NPV = Net Proceeds / (1 + r)^(t/12)
            # Where t is months, convert to years by /12
            years = Decimal(str(scenario.timing_months)) / Decimal("12")
            discount_factor = (Decimal("1") + time_value_discount_rate) ** float(years)
            npv = scenario.net_proceeds / Decimal(str(discount_factor))

            scenarios_with_npv.append((scenario, npv))

        # Sort by NPV
        scenarios_with_npv.sort(key=lambda x: x[1], reverse=True)

        optimal = scenarios_with_npv[0][0]

        logger.info(
            f"Optimal strategy with time value consideration: {optimal.strategy_name}"
        )

        return optimal

    def loan_vs_direct_analysis(
        self,
        policy_id: str,
        qualified_spend: Decimal,
        jurisdiction_spend: JurisdictionSpend,
        loan_fee_rate: Decimal,
        production_schedule_months: int
    ) -> Dict[str, any]:
        """
        Detailed comparison of tax credit loan vs. direct monetization.

        Args:
            policy_id: Policy to analyze
            qualified_spend: Qualified spend amount
            jurisdiction_spend: Full spending detail
            loan_fee_rate: Loan fee percentage (0-100)
            production_schedule_months: Production timeline

        Returns:
            Dict with detailed comparison:
            {
                "loan_scenario": {...},
                "direct_scenario": {...},
                "difference": {...}
            }
        """
        # Calculate loan scenario
        loan_result = self.calculator.calculate_single_jurisdiction(
            policy_id=policy_id,
            jurisdiction_spend=jurisdiction_spend,
            monetization_method=MonetizationMethod.TAX_CREDIT_LOAN,
            transfer_discount=loan_fee_rate
        )

        # Calculate direct scenario
        direct_result = self.calculator.calculate_single_jurisdiction(
            policy_id=policy_id,
            jurisdiction_spend=jurisdiction_spend,
            monetization_method=MonetizationMethod.DIRECT_CASH
        )

        # Calculate differences
        loan_cost = direct_result.net_cash_benefit - loan_result.net_cash_benefit
        months_earlier = direct_result.timing_months - loan_result.timing_months

        # Calculate break-even opportunity cost
        # This is the annual return rate where loan = direct
        if months_earlier > 0 and loan_cost > 0:
            # Solve for r: loan_proceeds = direct_proceeds / (1+r)^(months/12)
            # r = (direct/loan)^(12/months) - 1
            ratio = float(direct_result.net_cash_benefit / loan_result.net_cash_benefit)
            time_in_years = months_earlier / 12.0
            break_even_rate = (ratio ** (1 / time_in_years)) - 1
            break_even_rate_pct = Decimal(str(break_even_rate * 100))
        else:
            break_even_rate_pct = Decimal("0")

        analysis = {
            "loan_scenario": {
                "upfront_proceeds": str(loan_result.net_cash_benefit),
                "loan_fee": str(loan_result.discount_amount),
                "month_received": loan_result.timing_months,
                "net_benefit": str(loan_result.net_cash_benefit),
                "effective_rate": str(loan_result.effective_rate)
            },
            "direct_scenario": {
                "cash_received": str(direct_result.net_cash_benefit),
                "month_received": direct_result.timing_months,
                "net_benefit": str(direct_result.net_cash_benefit),
                "effective_rate": str(direct_result.effective_rate)
            },
            "difference": {
                "loan_cost": str(loan_cost),
                "months_earlier": months_earlier,
                "break_even_opportunity_cost_pct": str(break_even_rate_pct),
                "recommendation": (
                    f"Loan is worth it if opportunity cost > {break_even_rate_pct}% annually. "
                    f"You pay ${loan_cost:,.0f} to receive funds {months_earlier} months earlier."
                )
            },
            "summary": (
                f"Tax credit loan provides ${loan_result.net_cash_benefit:,.0f} in month "
                f"{loan_result.timing_months} vs. ${direct_result.net_cash_benefit:,.0f} in "
                f"month {direct_result.timing_months} for direct cash. "
                f"Loan cost: ${loan_cost:,.0f} ({loan_fee_rate}% fee)."
            )
        }

        logger.info(f"Loan vs. Direct analysis for {policy_id}: {analysis['summary']}")

        return analysis

    def _get_strategy_name(self, method: MonetizationMethod) -> str:
        """Get human-readable strategy name"""
        names = {
            MonetizationMethod.DIRECT_CASH: "Direct Cash Refund/Rebate",
            MonetizationMethod.TAX_LIABILITY_OFFSET: "Tax Liability Offset",
            MonetizationMethod.TRANSFER_TO_INVESTOR: "Transfer to Third-Party Investor",
            MonetizationMethod.TAX_CREDIT_LOAN: "Tax Credit Bridge Loan"
        }
        return names.get(method, method.value)

    def _get_strategy_notes(self, method: MonetizationMethod, policy) -> str:
        """Get notes about strategy"""
        if method == MonetizationMethod.DIRECT_CASH:
            return (
                f"Refundable/rebate paid directly. "
                f"Timing: ~{policy.timing_months_audit_to_certification + policy.timing_months_certification_to_cash} "
                f"months after production completion."
            )
        elif method == MonetizationMethod.TAX_LIABILITY_OFFSET:
            return (
                "Requires sufficient tax liability. "
                "No discount, but only useful if you owe taxes."
            )
        elif method == MonetizationMethod.TRANSFER_TO_INVESTOR:
            return (
                f"Sell credit to investor at ~{self.DEFAULT_TRANSFER_DISCOUNT}% discount. "
                "Immediate liquidity."
            )
        elif method == MonetizationMethod.TAX_CREDIT_LOAN:
            return (
                f"Borrow against future credit at ~{self.DEFAULT_LOAN_FEE}% fee. "
                "Receive funds during production."
            )
        return ""

    def _recommend_strategy(
        self,
        scenarios: List[MonetizationScenario],
        policy
    ) -> tuple[str, str]:
        """
        Determine recommended strategy.

        Args:
            scenarios: List of scenarios (sorted by net proceeds)
            policy: IncentivePolicy

        Returns:
            Tuple of (strategy_name, reason)
        """
        if not scenarios:
            return ("N/A", "No valid monetization strategies available")

        # Best by net proceeds
        best = scenarios[0]

        # Check if timing is critical
        has_loan = any(s.monetization_method == MonetizationMethod.TAX_CREDIT_LOAN for s in scenarios)

        if has_loan:
            loan_scenario = next(
                s for s in scenarios
                if s.monetization_method == MonetizationMethod.TAX_CREDIT_LOAN
            )

            # If loan provides funds very early and cost is reasonable
            cost_difference = best.net_proceeds - loan_scenario.net_proceeds
            cost_percentage = (cost_difference / best.net_proceeds * Decimal("100"))

            if loan_scenario.timing_months <= 2 and cost_percentage < Decimal("15"):
                return (
                    loan_scenario.strategy_name,
                    f"Tax credit loan provides liquidity in month {loan_scenario.timing_months} "
                    f"at a reasonable cost ({cost_percentage:.1f}% vs. direct cash). "
                    "Recommended if production needs immediate funding."
                )

        # Default: recommend highest net proceeds
        return (
            best.strategy_name,
            f"Maximizes net proceeds at ${best.net_proceeds:,.0f} "
            f"({best.effective_rate}% effective rate). "
            f"Receipt in month {best.timing_months}."
        )
