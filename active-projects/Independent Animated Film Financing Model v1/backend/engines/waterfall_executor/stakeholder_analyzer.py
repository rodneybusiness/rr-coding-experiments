"""
Stakeholder Analyzer

Calculates investor returns (IRR, NPV, cash-on-cash, payback period) from
waterfall execution results.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
import math

from backend.models.capital_stack import CapitalStack
from backend.engines.waterfall_executor.waterfall_executor import TimeSeriesWaterfallResult

logger = logging.getLogger(__name__)


@dataclass
class StakeholderCashFlows:
    """
    Cash flows for a single stakeholder.

    Attributes:
        stakeholder_id: Unique identifier
        stakeholder_name: Display name
        stakeholder_type: Type (equity, debt, pre_sale, etc.)
        initial_investment: Amount invested
        investment_quarter: When investment was made
        quarterly_receipts: Quarter → amount received
        total_receipts: Sum of all receipts
        irr: Internal Rate of Return (annualized)
        npv: Net Present Value at discount rate
        cash_on_cash: Total receipts / initial investment
        payback_quarter: Quarter when investment recovered
        payback_years: Years to payback
        roi_percentage: (Total receipts - investment) / investment * 100
    """
    stakeholder_id: str
    stakeholder_name: str
    stakeholder_type: str

    initial_investment: Decimal
    investment_quarter: int

    quarterly_receipts: Dict[int, Decimal]
    total_receipts: Decimal

    irr: Optional[Decimal]
    npv: Optional[Decimal]
    cash_on_cash: Decimal
    payback_quarter: Optional[int]
    payback_years: Optional[Decimal]

    roi_percentage: Decimal

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "stakeholder_id": self.stakeholder_id,
            "stakeholder_name": self.stakeholder_name,
            "stakeholder_type": self.stakeholder_type,
            "initial_investment": str(self.initial_investment),
            "investment_quarter": self.investment_quarter,
            "quarterly_receipts": {k: str(v) for k, v in self.quarterly_receipts.items()},
            "total_receipts": str(self.total_receipts),
            "irr": str(self.irr) if self.irr is not None else None,
            "npv": str(self.npv) if self.npv is not None else None,
            "cash_on_cash": str(self.cash_on_cash),
            "payback_quarter": self.payback_quarter,
            "payback_years": str(self.payback_years) if self.payback_years is not None else None,
            "roi_percentage": str(self.roi_percentage),
            "metadata": self.metadata
        }


@dataclass
class StakeholderAnalysisResult:
    """
    Analysis for all stakeholders.

    Attributes:
        project_name: Project identifier
        waterfall_result: Waterfall execution result
        capital_stack: Capital stack used
        stakeholders: List of stakeholder cash flows
        discount_rate: Discount rate used for NPV
        summary_statistics: Aggregate stats
    """
    project_name: str
    waterfall_result: TimeSeriesWaterfallResult
    capital_stack: Optional[CapitalStack]

    stakeholders: List[StakeholderCashFlows]

    discount_rate: Decimal

    summary_statistics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_name": self.project_name,
            "waterfall_result": self.waterfall_result.to_dict(),
            "stakeholders": [s.to_dict() for s in self.stakeholders],
            "discount_rate": str(self.discount_rate),
            "summary_statistics": self.summary_statistics
        }


class StakeholderAnalyzer:
    """
    Calculate investor returns from waterfall execution.

    Computes IRR, NPV, cash-on-cash multiples, payback periods for each
    stakeholder based on their investment and waterfall receipts.
    """

    def __init__(
        self,
        capital_stack: CapitalStack,
        discount_rate: Decimal = Decimal("0.12")
    ):
        """
        Initialize with capital stack and discount rate.

        Args:
            capital_stack: CapitalStack from Phase 2A models
            discount_rate: Annual discount rate for NPV (e.g., 0.12 = 12%)
        """
        self.capital_stack = capital_stack
        self.discount_rate = discount_rate
        logger.info(f"StakeholderAnalyzer initialized with {discount_rate * 100}% discount rate")

    def analyze(
        self,
        waterfall_result: TimeSeriesWaterfallResult,
        investment_timing: Optional[Dict[str, int]] = None
    ) -> StakeholderAnalysisResult:
        """
        Analyze returns for all stakeholders.

        Args:
            waterfall_result: Result from WaterfallExecutor.execute_over_time()
            investment_timing: Optional dict mapping stakeholder → investment quarter

        Returns:
            StakeholderAnalysisResult with detailed returns
        """
        if investment_timing is None:
            investment_timing = {}

        stakeholders = []

        # Analyze each financial instrument in capital stack
        for component in self.capital_stack.components:
            instrument = component.instrument

            # Map instrument to waterfall payee
            payee_name = self._map_instrument_to_payee(instrument)

            # Extract quarterly receipts for this payee
            quarterly_receipts = self._extract_quarterly_receipts(
                waterfall_result,
                payee_name
            )

            # Get investment timing
            investment_quarter = investment_timing.get(payee_name, 0)

            # Build cash flow list (investment + receipts)
            cash_flows = [(investment_quarter, -instrument.amount)]  # Negative = outflow
            for quarter, receipt in quarterly_receipts.items():
                cash_flows.append((quarter, receipt))

            # Calculate metrics
            total_receipts = sum(quarterly_receipts.values())

            irr = self.calculate_irr(cash_flows)
            npv = self.calculate_npv(cash_flows, self.discount_rate)
            cash_on_cash = total_receipts / instrument.amount if instrument.amount > 0 else Decimal("0")

            payback_quarter, payback_years = self.calculate_payback_period(
                instrument.amount,
                quarterly_receipts
            )

            roi_percentage = ((total_receipts - instrument.amount) / instrument.amount * Decimal("100")) if instrument.amount > 0 else Decimal("0")

            # Create stakeholder cash flows
            stakeholder = StakeholderCashFlows(
                stakeholder_id=f"{instrument.instrument_type.value}_{payee_name}",
                stakeholder_name=payee_name,
                stakeholder_type=instrument.instrument_type.value,
                initial_investment=instrument.amount,
                investment_quarter=investment_quarter,
                quarterly_receipts=quarterly_receipts,
                total_receipts=total_receipts,
                irr=irr,
                npv=npv,
                cash_on_cash=cash_on_cash,
                payback_quarter=payback_quarter,
                payback_years=payback_years,
                roi_percentage=roi_percentage,
                metadata={"instrument": instrument.instrument_type.value}
            )

            stakeholders.append(stakeholder)

        # Generate summary statistics
        summary = self._generate_summary(stakeholders)

        result = StakeholderAnalysisResult(
            project_name=waterfall_result.project_name,
            waterfall_result=waterfall_result,
            capital_stack=self.capital_stack,
            stakeholders=stakeholders,
            discount_rate=self.discount_rate,
            summary_statistics=summary
        )

        logger.info(
            f"Analyzed {len(stakeholders)} stakeholders for '{waterfall_result.project_name}'"
        )

        return result

    def calculate_irr(
        self,
        cash_flows: List[Tuple[int, Decimal]]
    ) -> Optional[Decimal]:
        """
        Calculate Internal Rate of Return using Newton-Raphson method.

        Solves for r where NPV(r) = 0.

        Args:
            cash_flows: List of (quarter, amount) tuples
                       First entry should be negative (investment)

        Returns:
            Annualized IRR as decimal (e.g., 0.15 = 15%) or None if undefined
        """
        if not cash_flows or len(cash_flows) < 2:
            return None

        # Check if there's at least one negative (investment) and one positive (return)
        has_negative = any(cf[1] < 0 for cf in cash_flows)
        has_positive = any(cf[1] > 0 for cf in cash_flows)

        if not (has_negative and has_positive):
            return None

        # Convert to annual cash flows (quarters → years) and to float for calculation
        cash_flows_years = [(float(q) / 4.0, float(amt)) for q, amt in cash_flows]

        # Newton-Raphson iteration (use float for numerical stability)
        r = 0.10  # Initial guess: 10%
        max_iterations = 100
        precision = 0.00001

        for i in range(max_iterations):
            # Calculate NPV at current r
            npv = sum(amt / (1 + r) ** t for t, amt in cash_flows_years)

            # Calculate derivative (NPV')
            npv_prime = sum(-t * amt / (1 + r) ** (t + 1) for t, amt in cash_flows_years)

            if abs(npv_prime) < precision:
                return None  # Can't converge

            # Newton-Raphson step
            r_new = r - (npv / npv_prime)

            # Check convergence
            if abs(r_new - r) < precision:
                # Converged - convert back to Decimal
                return Decimal(str(r_new)) if r_new > -1.0 else None  # IRR must be > -100%

            r = r_new

            # Prevent divergence
            if abs(r) > 10.0:  # IRR > 1000% or < -1000%
                return None

        return None  # Didn't converge

    def calculate_npv(
        self,
        cash_flows: List[Tuple[int, Decimal]],
        discount_rate: Decimal
    ) -> Decimal:
        """
        Calculate Net Present Value.

        NPV = Σ (CF_t / (1 + r)^t) where t is in years

        Args:
            cash_flows: List of (quarter, amount) tuples
            discount_rate: Annual discount rate

        Returns:
            NPV in currency units
        """
        # Convert quarters to years and to float for calculation
        cash_flows_years = [(float(q) / 4.0, float(amt)) for q, amt in cash_flows]

        # Calculate NPV (use float for numerical operations)
        npv_float = sum(amt / (1 + float(discount_rate)) ** t for t, amt in cash_flows_years)

        # Convert result back to Decimal
        return Decimal(str(npv_float))

    def calculate_payback_period(
        self,
        initial_investment: Decimal,
        quarterly_receipts: Dict[int, Decimal]
    ) -> Tuple[Optional[int], Optional[Decimal]]:
        """
        Calculate payback period (when cumulative receipts = initial investment).

        Args:
            initial_investment: Initial investment amount
            quarterly_receipts: Quarter → receipt amount

        Returns:
            (payback_quarter, payback_years) or (None, None) if never pays back
        """
        if not quarterly_receipts or initial_investment == 0:
            return (None, None)

        cumulative = Decimal("0")
        for quarter in sorted(quarterly_receipts.keys()):
            cumulative += quarterly_receipts[quarter]

            if cumulative >= initial_investment:
                payback_years = Decimal(str(quarter)) / Decimal("4")
                return (quarter, payback_years)

        # Didn't pay back within projection period
        return (None, None)

    def _map_instrument_to_payee(self, instrument) -> str:
        """
        Map financial instrument to waterfall payee name.

        This is a simple mapping - in production, would use explicit
        mapping configuration.

        Args:
            instrument: FinancialInstrument

        Returns:
            Payee name string
        """
        # Simple mapping based on instrument type
        type_to_payee = {
            "equity": "Equity Investors",
            "senior_debt": "Senior Lender",
            "gap_debt": "Gap Lender",
            "mezzanine_debt": "Mezzanine Lender",
            "tax_credit_loan": "Tax Credit Lender",
            "bridge_financing": "Bridge Lender",
            "pre_sale": "Distributor (Pre-Sale)",
            "negative_pickup": "Distributor (Negative Pickup)",
            "grant": "Government (Grant)"
        }

        return type_to_payee.get(instrument.instrument_type.value, "Unknown Payee")

    def _extract_quarterly_receipts(
        self,
        waterfall_result: TimeSeriesWaterfallResult,
        payee_name: str
    ) -> Dict[int, Decimal]:
        """
        Extract quarterly receipts for a specific payee.

        Args:
            waterfall_result: Waterfall execution result
            payee_name: Payee to extract receipts for

        Returns:
            Dict mapping quarter → receipt amount
        """
        quarterly_receipts: Dict[int, Decimal] = {}

        for execution in waterfall_result.quarterly_executions:
            receipt = execution.payee_payouts.get(payee_name, Decimal("0"))
            if receipt > 0:
                quarterly_receipts[execution.quarter] = receipt

        return quarterly_receipts

    def _generate_summary(
        self,
        stakeholders: List[StakeholderCashFlows]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics across all stakeholders.

        Args:
            stakeholders: List of stakeholder cash flows

        Returns:
            Dict with aggregate stats
        """
        if not stakeholders:
            return {}

        total_invested = sum(s.initial_investment for s in stakeholders)
        total_recouped = sum(s.total_receipts for s in stakeholders)
        overall_recovery_rate = (total_recouped / total_invested * Decimal("100")) if total_invested > 0 else Decimal("0")

        # Calculate median IRR
        irrs = [s.irr for s in stakeholders if s.irr is not None]
        median_irr = self._calculate_median(irrs) if irrs else None

        # Calculate median cash-on-cash
        cocs = [s.cash_on_cash for s in stakeholders]
        median_coc = self._calculate_median(cocs) if cocs else None

        # Equity-specific metrics
        equity_stakeholders = [s for s in stakeholders if "equity" in s.stakeholder_type.lower()]
        equity_irr = None
        if equity_stakeholders and len(equity_stakeholders) > 0:
            equity_irrs = [s.irr for s in equity_stakeholders if s.irr is not None]
            equity_irr = self._calculate_median(equity_irrs) if equity_irrs else None

        # Debt-specific metrics
        debt_stakeholders = [s for s in stakeholders if "debt" in s.stakeholder_type.lower() or "lender" in s.stakeholder_name.lower()]
        debt_recovery_rate = None
        if debt_stakeholders:
            debt_invested = sum(s.initial_investment for s in debt_stakeholders)
            debt_recouped = sum(s.total_receipts for s in debt_stakeholders)
            debt_recovery_rate = (debt_recouped / debt_invested * Decimal("100")) if debt_invested > 0 else Decimal("0")

        summary = {
            "total_invested": str(total_invested),
            "total_recouped": str(total_recouped),
            "overall_recovery_rate": str(overall_recovery_rate),
            "median_irr": str(median_irr) if median_irr else None,
            "median_cash_on_cash": str(median_coc) if median_coc else None,
            "equity_irr": str(equity_irr) if equity_irr else None,
            "debt_recovery_rate": str(debt_recovery_rate) if debt_recovery_rate else None,
            "num_stakeholders": len(stakeholders)
        }

        return summary

    def _calculate_median(self, values: List[Decimal]) -> Optional[Decimal]:
        """Calculate median of decimal values"""
        if not values:
            return None

        sorted_values = sorted(values)
        n = len(sorted_values)

        if n % 2 == 1:
            return sorted_values[n // 2]
        else:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / Decimal("2")
