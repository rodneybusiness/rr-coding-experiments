"""
Cash Flow Projector

Projects monthly cash flow impact of tax incentives with detailed timeline
of production spending and incentive receipts.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal

from backend.engines.incentive_calculator.calculator import (
    JurisdictionSpend,
    IncentiveResult,
)


logger = logging.getLogger(__name__)


@dataclass
class CashFlowEvent:
    """
    Single cash flow event.

    Attributes:
        month: Months from project start (0 = start)
        event_type: Type of event (production_spend, incentive_receipt, etc.)
        description: Human-readable event description
        amount: Cash flow amount (positive = inflow, negative = outflow)
        cumulative_balance: Running cash balance after this event
        policy_id: Optional policy ID for incentive receipts
    """
    month: int
    event_type: str
    description: str
    amount: Decimal
    cumulative_balance: Decimal
    policy_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "month": self.month,
            "event_type": self.event_type,
            "description": self.description,
            "amount": str(self.amount),
            "cumulative_balance": str(self.cumulative_balance),
            "policy_id": self.policy_id
        }


@dataclass
class CashFlowProjection:
    """
    Complete cash flow timeline.

    Attributes:
        project_start_month: Starting month (typically 0)
        production_period_months: Length of production period
        events: List of all cash flow events
        monthly_summary: Dict mapping month to net cash flow
        cumulative_summary: Dict mapping month to cumulative balance
        peak_funding_required: Maximum negative balance (funding need)
        total_incentive_receipts: Total incentive cash received
        final_balance: Final cumulative balance
    """
    project_start_month: int
    production_period_months: int
    events: List[CashFlowEvent]
    monthly_summary: Dict[int, Decimal]
    cumulative_summary: Dict[int, Decimal]
    peak_funding_required: Decimal
    total_incentive_receipts: Decimal
    final_balance: Decimal

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "project_start_month": self.project_start_month,
            "production_period_months": self.production_period_months,
            "events": [e.to_dict() for e in self.events],
            "monthly_summary": {k: str(v) for k, v in self.monthly_summary.items()},
            "cumulative_summary": {k: str(v) for k, v in self.cumulative_summary.items()},
            "peak_funding_required": str(self.peak_funding_required),
            "total_incentive_receipts": str(self.total_incentive_receipts),
            "final_balance": str(self.final_balance)
        }


class CashFlowProjector:
    """
    Project cash flow timeline for incentive scenarios.

    Generates month-by-month cash flow projections showing production spending
    and incentive receipt timing.
    """

    def __init__(self):
        """Initialize projector"""
        logger.info("CashFlowProjector initialized")

    def project(
        self,
        production_budget: Decimal,
        production_schedule_months: int,
        jurisdiction_spends: List[JurisdictionSpend],
        incentive_results: List[IncentiveResult],
        spend_curve: Optional[List[Decimal]] = None
    ) -> CashFlowProjection:
        """
        Project cash flow with incentive timing.

        Args:
            production_budget: Total budget
            production_schedule_months: Production timeline
            jurisdiction_spends: Spending by jurisdiction
            incentive_results: Calculated incentive results
            spend_curve: Optional monthly spend profile (% of budget per month)
                        If not provided, uses S-curve default

        Returns:
            CashFlowProjection with month-by-month detail
        """
        # Generate spend curve if not provided
        if spend_curve is None:
            spend_curve = self._generate_s_curve(production_schedule_months)

        # Validate spend curve
        if len(spend_curve) != production_schedule_months:
            raise ValueError(
                f"Spend curve length ({len(spend_curve)}) must match "
                f"production schedule ({production_schedule_months} months)"
            )

        curve_total = sum(spend_curve)
        if abs(curve_total - Decimal("1.0")) > Decimal("0.01"):
            raise ValueError(
                f"Spend curve must sum to 1.0 (100%), got {curve_total}"
            )

        events = []
        monthly_summary: Dict[int, Decimal] = {}
        cumulative_balance = Decimal("0")

        # Generate production spend events
        for month in range(production_schedule_months):
            monthly_spend = production_budget * spend_curve[month]

            event = CashFlowEvent(
                month=month,
                event_type="production_spend",
                description=f"Production spending - Month {month + 1}",
                amount=-monthly_spend,  # Negative = outflow
                cumulative_balance=cumulative_balance - monthly_spend
            )

            events.append(event)
            monthly_summary[month] = monthly_summary.get(month, Decimal("0")) - monthly_spend
            cumulative_balance -= monthly_spend

        # Add incentive receipt events
        production_completion_month = production_schedule_months - 1

        for result in incentive_results:
            receipt_month = production_completion_month + result.timing_months

            event = CashFlowEvent(
                month=receipt_month,
                event_type="incentive_receipt",
                description=f"{result.policy_name} - {result.jurisdiction}",
                amount=result.net_cash_benefit,  # Positive = inflow
                cumulative_balance=cumulative_balance + result.net_cash_benefit,
                policy_id=result.policy_id
            )

            events.append(event)
            monthly_summary[receipt_month] = monthly_summary.get(receipt_month, Decimal("0")) + result.net_cash_benefit
            cumulative_balance += result.net_cash_benefit

        # Sort events by month
        events.sort(key=lambda e: (e.month, e.event_type))

        # Recalculate cumulative balances in sorted order
        cumulative_balance = Decimal("0")
        cumulative_summary: Dict[int, Decimal] = {}

        for event in events:
            cumulative_balance += event.amount
            event.cumulative_balance = cumulative_balance
            cumulative_summary[event.month] = cumulative_balance

        # Calculate peak funding required (most negative balance)
        peak_funding = min(cumulative_summary.values()) if cumulative_summary else Decimal("0")
        if peak_funding > 0:
            peak_funding = Decimal("0")  # No funding required if always positive

        # Calculate total incentive receipts
        total_incentives = sum(
            e.amount for e in events
            if e.event_type == "incentive_receipt"
        )

        # Final balance
        final_balance = cumulative_balance

        logger.info(
            f"Projected cash flow: {len(events)} events over "
            f"{max(e.month for e in events) + 1} months, "
            f"peak funding ${abs(peak_funding):,.0f}"
        )

        return CashFlowProjection(
            project_start_month=0,
            production_period_months=production_schedule_months,
            events=events,
            monthly_summary=monthly_summary,
            cumulative_summary=cumulative_summary,
            peak_funding_required=abs(peak_funding),
            total_incentive_receipts=total_incentives,
            final_balance=final_balance
        )

    def _generate_s_curve(self, months: int) -> List[Decimal]:
        """
        Generate default S-curve spend profile.

        S-curve follows typical film production spending:
        - Slow ramp-up (pre-production)
        - Peak spending (principal photography)
        - Tail-off (post-production)

        Args:
            months: Number of months

        Returns:
            List of monthly spend percentages (sum = 1.0)
        """
        if months <= 0:
            raise ValueError("Production schedule must be at least 1 month")

        # Define S-curve shape based on production phases
        if months <= 3:
            # Very short production - even distribution
            return [Decimal("1.0") / Decimal(str(months))] * months

        # Allocate by phase
        pre_production_months = max(1, months // 6)  # ~15-20%
        principal_months = max(2, months // 2)       # ~50-60%
        post_production_months = months - pre_production_months - principal_months

        curve = []

        # Pre-production: 15% of budget, ramp up
        pre_prod_total = Decimal("0.15")
        for i in range(pre_production_months):
            # Linear ramp
            pct = pre_prod_total / Decimal(str(pre_production_months))
            curve.append(pct)

        # Principal photography: 60% of budget, peak spending
        principal_total = Decimal("0.60")
        for i in range(principal_months):
            pct = principal_total / Decimal(str(principal_months))
            curve.append(pct)

        # Post-production: 25% of budget, tail off
        post_prod_total = Decimal("0.25")
        for i in range(post_production_months):
            pct = post_prod_total / Decimal(str(post_production_months))
            curve.append(pct)

        # Normalize to ensure sum = 1.0
        curve_sum = sum(curve)
        curve = [c / curve_sum for c in curve]

        return curve

    def compare_timing_scenarios(
        self,
        base_projection: CashFlowProjection,
        loan_projection: CashFlowProjection
    ) -> Dict[str, any]:
        """
        Compare direct monetization vs. loan timing.

        Args:
            base_projection: Projection with direct monetization
            loan_projection: Projection with loan/transfer monetization

        Returns:
            Dict with comparison metrics:
            {
                "peak_funding_difference": Decimal,
                "months_earlier": int,
                "loan_cost": Decimal,
                "net_benefit_difference": Decimal
            }
        """
        # Calculate differences
        peak_diff = base_projection.peak_funding_required - loan_projection.peak_funding_required

        # Find earliest incentive receipt in each scenario
        base_earliest = min(
            (e.month for e in base_projection.events if e.event_type == "incentive_receipt"),
            default=999
        )
        loan_earliest = min(
            (e.month for e in loan_projection.events if e.event_type == "incentive_receipt"),
            default=999
        )

        months_earlier = base_earliest - loan_earliest

        # Calculate loan cost (difference in total receipts)
        loan_cost = base_projection.total_incentive_receipts - loan_projection.total_incentive_receipts

        # Net benefit difference
        net_diff = base_projection.final_balance - loan_projection.final_balance

        comparison = {
            "peak_funding_difference": peak_diff,
            "months_earlier": months_earlier,
            "loan_cost": loan_cost,
            "net_benefit_difference": net_diff,
            "base_peak_funding": base_projection.peak_funding_required,
            "loan_peak_funding": loan_projection.peak_funding_required
        }

        logger.info(
            f"Timing comparison: Loan reduces peak funding by ${peak_diff:,.0f}, "
            f"receipt {months_earlier} months earlier, cost ${loan_cost:,.0f}"
        )

        return comparison

    def monthly_view_dict(self, projection: CashFlowProjection) -> Dict[int, Dict[str, any]]:
        """
        Convert projection to monthly summary dict for analysis.

        Returns:
            Dict mapping month to:
            {
                "spend": Decimal,
                "incentive_receipts": Decimal,
                "net_cash_flow": Decimal,
                "cumulative_balance": Decimal,
                "events": List[str]
            }
        """
        monthly_view = {}

        # Initialize all months
        max_month = max(e.month for e in projection.events) if projection.events else 0
        for month in range(max_month + 1):
            monthly_view[month] = {
                "spend": Decimal("0"),
                "incentive_receipts": Decimal("0"),
                "net_cash_flow": Decimal("0"),
                "cumulative_balance": Decimal("0"),
                "events": []
            }

        # Populate from events
        for event in projection.events:
            month = event.month
            view = monthly_view[month]

            if event.event_type == "production_spend":
                view["spend"] += abs(event.amount)
            elif event.event_type == "incentive_receipt":
                view["incentive_receipts"] += event.amount

            view["events"].append(event.description)

        # Calculate net and cumulative
        for month in sorted(monthly_view.keys()):
            view = monthly_view[month]
            view["net_cash_flow"] = view["incentive_receipts"] - view["spend"]
            view["cumulative_balance"] = projection.cumulative_summary.get(month, Decimal("0"))

        return monthly_view
