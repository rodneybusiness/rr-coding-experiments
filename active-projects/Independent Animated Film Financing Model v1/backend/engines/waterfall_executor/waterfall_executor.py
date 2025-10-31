"""
Waterfall Executor

Executes waterfall structures over time-series revenue, tracking cumulative
recoupment and generating investor payout schedules.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal
from copy import deepcopy

from backend.models.waterfall import WaterfallStructure, RecoupmentPriority
from backend.engines.waterfall_executor.revenue_projector import RevenueProjection

logger = logging.getLogger(__name__)


@dataclass
class QuarterlyWaterfallExecution:
    """
    Waterfall execution for a single quarter.

    Attributes:
        quarter: Quarter number
        gross_receipts: Gross revenue this quarter
        distribution_fees: Distribution fees deducted
        pa_expenses: P&A expenses deducted
        remaining_pool: After fees/expenses, available for recoupment
        node_payouts: Node ID → payout this quarter
        payee_payouts: Payee → total payout this quarter
        cumulative_recouped: Node ID → cumulative recouped to date
        cumulative_paid: Payee → cumulative paid to date
        unrecouped_balances: Node ID → remaining to recoup
    """
    quarter: int
    gross_receipts: Decimal
    distribution_fees: Decimal
    pa_expenses: Decimal
    remaining_pool: Decimal

    node_payouts: Dict[str, Decimal] = field(default_factory=dict)
    payee_payouts: Dict[str, Decimal] = field(default_factory=dict)

    cumulative_recouped: Dict[str, Decimal] = field(default_factory=dict)
    cumulative_paid: Dict[str, Decimal] = field(default_factory=dict)

    unrecouped_balances: Dict[str, Decimal] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "quarter": self.quarter,
            "gross_receipts": str(self.gross_receipts),
            "distribution_fees": str(self.distribution_fees),
            "pa_expenses": str(self.pa_expenses),
            "remaining_pool": str(self.remaining_pool),
            "node_payouts": {k: str(v) for k, v in self.node_payouts.items()},
            "payee_payouts": {k: str(v) for k, v in self.payee_payouts.items()},
            "cumulative_recouped": {k: str(v) for k, v in self.cumulative_recouped.items()},
            "cumulative_paid": {k: str(v) for k, v in self.cumulative_paid.items()},
            "unrecouped_balances": {k: str(v) for k, v in self.unrecouped_balances.items()}
        }


@dataclass
class TimeSeriesWaterfallResult:
    """
    Complete waterfall execution over time.

    Attributes:
        project_name: Project identifier
        waterfall_structure: Reference to original waterfall
        revenue_projection: Revenue projection used
        quarterly_executions: List of quarterly results
        total_receipts: Total gross receipts
        total_fees: Total fees deducted
        total_recouped_by_node: Node ID → total recouped
        total_paid_by_payee: Payee → total paid
        final_unrecouped: What didn't recoup
        metadata: Execution notes
    """
    project_name: str
    waterfall_structure: WaterfallStructure
    revenue_projection: RevenueProjection

    quarterly_executions: List[QuarterlyWaterfallExecution]

    total_receipts: Decimal
    total_fees: Decimal
    total_recouped_by_node: Dict[str, Decimal]
    total_paid_by_payee: Dict[str, Decimal]

    final_unrecouped: Dict[str, Decimal]

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_name": self.project_name,
            "revenue_projection": self.revenue_projection.to_dict(),
            "quarterly_executions": [qe.to_dict() for qe in self.quarterly_executions],
            "total_receipts": str(self.total_receipts),
            "total_fees": str(self.total_fees),
            "total_recouped_by_node": {k: str(v) for k, v in self.total_recouped_by_node.items()},
            "total_paid_by_payee": {k: str(v) for k, v in self.total_paid_by_payee.items()},
            "final_unrecouped": {k: str(v) for k, v in self.final_unrecouped.items()},
            "metadata": self.metadata
        }


class WaterfallExecutor:
    """
    Execute waterfall structure over time-series revenue.

    Processes quarterly revenue through waterfall tiers, tracking cumulative
    recoupment and stopping nodes when fully recouped.
    """

    def __init__(self, waterfall_structure: WaterfallStructure):
        """
        Initialize with waterfall structure from Phase 2A.

        Args:
            waterfall_structure: WaterfallStructure from backend/models/waterfall.py
        """
        self.waterfall = waterfall_structure
        logger.info(f"WaterfallExecutor initialized with waterfall: {waterfall_structure.waterfall_name}")

    def execute_over_time(
        self,
        revenue_projection: RevenueProjection,
        distribution_fee_rate: Optional[Decimal] = None,
        pa_expenses_per_quarter: Optional[Dict[int, Decimal]] = None
    ) -> TimeSeriesWaterfallResult:
        """
        Execute waterfall quarter-by-quarter.

        Args:
            revenue_projection: Revenue projection from RevenueProjector
            distribution_fee_rate: Override default distribution fee (%)
            pa_expenses_per_quarter: Optional P&A expenses by quarter

        Returns:
            TimeSeriesWaterfallResult with quarterly detail
        """
        # Initialize cumulative state
        cumulative_recouped: Dict[str, Decimal] = {}
        for node in self.waterfall.nodes:
            node_id = f"{node.priority.value}_{node.payee}"
            cumulative_recouped[node_id] = Decimal("0")

        # Process each quarter
        quarterly_executions = []
        total_receipts = Decimal("0")
        total_fees_sum = Decimal("0")

        for quarter in sorted(revenue_projection.quarterly_revenue.keys()):
            gross_receipts = revenue_projection.quarterly_revenue[quarter]

            if gross_receipts == 0:
                continue

            # P&A expenses this quarter
            pa_expenses = Decimal("0")
            if pa_expenses_per_quarter and quarter in pa_expenses_per_quarter:
                pa_expenses = pa_expenses_per_quarter[quarter]

            # Process this quarter
            quarterly_execution = self.process_quarter(
                quarter=quarter,
                gross_receipts=gross_receipts,
                cumulative_state=cumulative_recouped,
                distribution_fee_rate=distribution_fee_rate,
                pa_expenses=pa_expenses
            )

            quarterly_executions.append(quarterly_execution)
            total_receipts += gross_receipts
            total_fees_sum += quarterly_execution.distribution_fees + quarterly_execution.pa_expenses

        # Aggregate totals
        total_recouped_by_node: Dict[str, Decimal] = {}
        total_paid_by_payee: Dict[str, Decimal] = {}

        if quarterly_executions:
            # Get final cumulative state
            final_execution = quarterly_executions[-1]
            total_recouped_by_node = final_execution.cumulative_recouped.copy()
            total_paid_by_payee = final_execution.cumulative_paid.copy()

        # Calculate final unrecouped
        final_unrecouped: Dict[str, Decimal] = {}
        for node in self.waterfall.nodes:
            node_id = f"{node.priority.value}_{node.payee}"
            target_amount = node.amount or Decimal("0")  # Use 0 if None (for percentage-based nodes)

            if node.amount:  # Only track unrecouped for fixed-amount nodes
                recouped = total_recouped_by_node.get(node_id, Decimal("0"))
                remaining = target_amount - recouped
                if remaining > 0:
                    final_unrecouped[node_id] = remaining

        result = TimeSeriesWaterfallResult(
            project_name=revenue_projection.project_name,
            waterfall_structure=self.waterfall,
            revenue_projection=revenue_projection,
            quarterly_executions=quarterly_executions,
            total_receipts=total_receipts,
            total_fees=total_fees_sum,
            total_recouped_by_node=total_recouped_by_node,
            total_paid_by_payee=total_paid_by_payee,
            final_unrecouped=final_unrecouped,
            metadata={
                "num_quarters": len(quarterly_executions),
                "distribution_fee_rate": str(distribution_fee_rate) if distribution_fee_rate else "default"
            }
        )

        logger.info(
            f"Executed waterfall over {len(quarterly_executions)} quarters: "
            f"${total_receipts:,.0f} total receipts, ${total_fees_sum:,.0f} fees"
        )

        return result

    def process_quarter(
        self,
        quarter: int,
        gross_receipts: Decimal,
        cumulative_state: Dict[str, Decimal],
        distribution_fee_rate: Optional[Decimal] = None,
        pa_expenses: Decimal = Decimal("0")
    ) -> QuarterlyWaterfallExecution:
        """
        Process waterfall for a single quarter.

        Args:
            quarter: Quarter number
            gross_receipts: Gross revenue this quarter
            cumulative_state: Cumulative recoupment state (node_id → amount)
            distribution_fee_rate: Distribution fee percentage
            pa_expenses: P&A expenses this quarter

        Returns:
            QuarterlyWaterfallExecution with this quarter's results
        """
        # Calculate distribution fees
        dist_fee_rate = distribution_fee_rate or self.waterfall.default_distribution_fee_rate or Decimal("0")
        distribution_fees = gross_receipts * (dist_fee_rate / Decimal("100"))

        # Remaining pool after fees
        remaining_pool = gross_receipts - distribution_fees - pa_expenses

        # Process waterfall nodes
        node_payouts: Dict[str, Decimal] = {}
        payee_payouts: Dict[str, Decimal] = {}

        # Get nodes sorted by priority
        sorted_nodes = sorted(self.waterfall.nodes, key=lambda n: n.priority.value)

        for node in sorted_nodes:
            if remaining_pool <= 0:
                break

            node_id = f"{node.priority.value}_{node.payee}"

            # Calculate remaining to recoup
            if node.amount:
                # Fixed amount node
                target_amount = node.amount
                already_recouped = cumulative_state.get(node_id, Decimal("0"))
                remaining_to_recoup = target_amount - already_recouped

                if remaining_to_recoup <= 0:
                    # Already fully recouped
                    continue

                # Pay lesser of (available_pool, remaining_to_recoup)
                payment = min(remaining_pool, remaining_to_recoup)

            else:
                # Percentage-based node (e.g., profit splits)
                if node.percentage:
                    payment = remaining_pool * (node.percentage / Decimal("100"))

                    # Apply cap if exists
                    if node.cap:
                        already_recouped = cumulative_state.get(node_id, Decimal("0"))
                        remaining_cap = node.cap - already_recouped
                        if remaining_cap <= 0:
                            continue
                        payment = min(payment, remaining_cap)
                else:
                    # No amount or percentage - skip
                    continue

            # Record payment
            node_payouts[node_id] = payment
            payee_payouts[node.payee] = payee_payouts.get(node.payee, Decimal("0")) + payment

            # Update cumulative state
            cumulative_state[node_id] = cumulative_state.get(node_id, Decimal("0")) + payment

            # Reduce available pool
            remaining_pool -= payment

        # Calculate unrecouped balances
        unrecouped_balances: Dict[str, Decimal] = {}
        for node in sorted_nodes:
            node_id = f"{node.priority.value}_{node.payee}"
            if node.amount:
                recouped = cumulative_state.get(node_id, Decimal("0"))
                remaining = node.amount - recouped
                if remaining > 0:
                    unrecouped_balances[node_id] = remaining

        # Calculate cumulative paid by payee
        cumulative_paid: Dict[str, Decimal] = {}
        for node in sorted_nodes:
            node_id = f"{node.priority.value}_{node.payee}"
            amount = cumulative_state.get(node_id, Decimal("0"))
            cumulative_paid[node.payee] = cumulative_paid.get(node.payee, Decimal("0")) + amount

        execution = QuarterlyWaterfallExecution(
            quarter=quarter,
            gross_receipts=gross_receipts,
            distribution_fees=distribution_fees,
            pa_expenses=pa_expenses,
            remaining_pool=remaining_pool,
            node_payouts=node_payouts,
            payee_payouts=payee_payouts,
            cumulative_recouped=cumulative_state.copy(),
            cumulative_paid=cumulative_paid,
            unrecouped_balances=unrecouped_balances
        )

        return execution
