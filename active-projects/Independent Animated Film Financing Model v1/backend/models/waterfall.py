"""
Waterfall Models - Revenue recoupment and distribution logic

This module defines the recoupment waterfall structure that determines
how gross receipts flow to various stakeholders (IPA/CAMA logic).
"""

from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class RecoupmentPriority(int, Enum):
    """Priority levels in the waterfall (lower = higher priority)"""
    DISTRIBUTION_FEES = 1
    PA_EXPENSES = 2  # Prints & Advertising
    SALES_AGENT_COMMISSION = 3
    SALES_AGENT_EXPENSES = 4
    SENIOR_DEBT_INTEREST = 5
    SENIOR_DEBT_PRINCIPAL = 6
    SENIOR_DEBT = 6  # Alias for compatibility with simplified priority definitions
    MEZZANINE_DEBT = 7
    EQUITY_RECOUPMENT = 8
    EQUITY = 8  # Alias for legacy instrument defaults
    EQUITY_PREMIUM = 9
    DEFERRED_PRODUCER_FEE = 10
    DEFERRED_TALENT = 11
    BACKEND_PARTICIPATION = 12
    NET_PROFITS = 13


class PayeeType(str, Enum):
    """Type of payee in the waterfall"""
    DISTRIBUTOR = "distributor"
    SALES_AGENT = "sales_agent"
    LENDER = "lender"
    INVESTOR = "investor"
    PRODUCER = "producer"
    TALENT = "talent"
    PROFIT_PARTICIPANT = "profit_participant"


class RecoupmentBasis(str, Enum):
    """What the recoupment is calculated on"""
    GROSS_RECEIPTS = "gross_receipts"
    NET_AFTER_FEES = "net_after_fees"
    NET_AFTER_DISTRIBUTION = "net_after_distribution"
    REMAINING_POOL = "remaining_pool"  # After all prior deductions


class WaterfallNode(BaseModel):
    """A single node/tier in the recoupment waterfall"""

    model_config = ConfigDict(populate_by_name=True)

    node_id: Optional[str] = Field(default=None, description="Unique node identifier")
    priority: RecoupmentPriority
    description: str = Field(default="", description="Description of this tier")

    # Payee
    payee_type: PayeeType = PayeeType.INVESTOR
    payee_name: str = Field(..., description="Name of entity/person receiving payment")
    payee_reference_id: Optional[str] = Field(default=None, description="Reference to CapitalComponent or other entity")

    # Calculation basis
    recoupment_basis: RecoupmentBasis = RecoupmentBasis.REMAINING_POOL

    # Amount specification (use ONE of these)
    fixed_amount: Optional[Decimal] = Field(default=None, description="Fixed dollar amount")
    percentage_of_receipts: Optional[Decimal] = Field(default=None, ge=0, le=100, description="% of the basis")

    # Cap
    capped_at: Optional[Decimal] = Field(default=None, description="Maximum amount payable")

    # Participation split (for profit pools)
    participation_splits: Optional[Dict[str, Decimal]] = Field(
        default=None,
        description="For profit pools: dict of participant -> percentage"
    )

    # Corridor/Threshold
    minimum_threshold: Optional[Decimal] = Field(
        default=None,
        description="Minimum amount that must be in pool before this node pays"
    )

    # Status tracking
    amount_recouped_to_date: Decimal = Field(default=Decimal("0"), ge=0)
    is_fully_recouped: bool = Field(default=False)

    notes: Optional[str] = None

    @model_validator(mode="before")
    def populate_defaults(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Provide sensible defaults and aliases for simplified test fixtures."""
        payee = values.get("payee") or values.get("payee_name")
        priority = values.get("priority")

        if values.get("amount") is not None and values.get("fixed_amount") is None:
            values["fixed_amount"] = values["amount"]

        if values.get("percentage") is not None and values.get("percentage_of_receipts") is None:
            values["percentage_of_receipts"] = values["percentage"]

        if payee and not values.get("payee_name"):
            values["payee_name"] = payee

        if not values.get("description") and payee:
            values["description"] = str(payee)

        if not values.get("node_id") and payee and priority:
            values["node_id"] = f"{priority.value}_{payee}"

        return values

    def calculate_payment(
        self,
        available_pool: Decimal,
        basis_amount: Optional[Decimal] = None
    ) -> Decimal:
        """
        Calculate the payment for this node given available funds

        Args:
            available_pool: Amount available in the pool at this priority level
            basis_amount: The amount to calculate percentage on (if using percentage)

        Returns:
            Amount to be paid to this payee
        """

        # Check minimum threshold
        if self.minimum_threshold and available_pool < self.minimum_threshold:
            return Decimal("0")

        # Calculate entitlement
        if self.fixed_amount is not None:
            entitlement = self.fixed_amount
        elif self.percentage_of_receipts is not None:
            if basis_amount is None:
                raise ValueError(f"basis_amount required for percentage calculation on node {self.node_id}")
            entitlement = basis_amount * (self.percentage_of_receipts / 100)
        else:
            raise ValueError(f"Node {self.node_id} must specify either fixed_amount or percentage_of_receipts")

        # Apply cap if exists
        if self.capped_at and entitlement > self.capped_at:
            entitlement = self.capped_at

        # Calculate remaining to recoup
        remaining_to_recoup = entitlement - self.amount_recouped_to_date

        # Can't recoup more than available or more than entitled
        payment = min(available_pool, remaining_to_recoup)

        return max(payment, Decimal("0"))  # Never negative


class WaterfallStructure(BaseModel):
    """Complete recoupment waterfall structure"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "waterfall_id": "WATERFALL-001",
                "project_id": "PROJ-001",
                "gross_receipts_definition": "All revenues from all sources worldwide",
                "nodes": [
                    {
                        "node_id": "NODE-001",
                        "priority": 1,
                        "description": "Distribution Fees",
                        "payee_type": "distributor",
                        "payee_name": "XYZ Distribution",
                        "recoupment_basis": "gross_receipts",
                        "percentage_of_receipts": "25"
                    }
                ]
            }
        }
    )

    waterfall_id: str = Field(default="WF-UNSPECIFIED")
    project_id: str = Field(default="PROJECT-UNKNOWN", description="Reference to ProjectProfile")

    # Engine 2 & 3 compatibility
    waterfall_name: str = Field(default="Unnamed Waterfall", description="Human-readable name")
    default_distribution_fee_rate: Decimal = Field(default=Decimal("30.0"), ge=0, le=100, description="Default distribution fee %")

    nodes: List[WaterfallNode] = Field(..., min_length=1, description="Ordered list of waterfall tiers")

    # Definitions for clarity
    gross_receipts_definition: str = Field(
        default="All revenues from all sources",
        description="What constitutes Gross Receipts"
    )

    net_receipts_definition: str = Field(
        default="Gross Receipts less Distribution Fees and Expenses",
        description="Definition of Net Receipts or Producer's Share"
    )

    # Metadata
    effective_date: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="before")
    def populate_structure_defaults(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Allow construction with minimal inputs (e.g., tests)."""
        if not values.get("waterfall_id"):
            values["waterfall_id"] = "WF-AUTO"
        if not values.get("project_id"):
            values["project_id"] = values.get("waterfall_name") or "PROJECT-AUTO"
        return values

    def get_nodes_by_priority(self) -> List[WaterfallNode]:
        """Get nodes sorted by priority (ascending)"""
        return sorted(self.nodes, key=lambda x: x.priority.value)

    def get_nodes_for_payee(self, payee_name: str) -> List[WaterfallNode]:
        """Get all nodes for a specific payee"""
        return [node for node in self.nodes if node.payee_name == payee_name]

    def calculate_waterfall(
        self,
        gross_receipts: Decimal,
        distribution_fees_rate: Optional[Decimal] = None,
        pa_expenses: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Execute the waterfall calculation

        Args:
            gross_receipts: Total gross receipts to distribute
            distribution_fees_rate: Distribution fee % (if applicable)
            pa_expenses: P&A expenses to recoup (if applicable)

        Returns:
            Dictionary with detailed waterfall results
        """

        results = {
            "gross_receipts": gross_receipts,
            "nodes_processed": [],
            "payee_totals": {},
            "remaining_pool": gross_receipts,
            "total_distributed": Decimal("0")
        }

        # Track the pool as we go down the waterfall
        remaining_pool = gross_receipts
        net_after_distribution = gross_receipts

        # Process nodes in priority order
        for node in self.get_nodes_by_priority():

            # Determine basis amount based on node's recoupment basis
            if node.recoupment_basis == RecoupmentBasis.GROSS_RECEIPTS:
                basis_amount = gross_receipts
            elif node.recoupment_basis == RecoupmentBasis.NET_AFTER_DISTRIBUTION:
                basis_amount = net_after_distribution
            elif node.recoupment_basis == RecoupmentBasis.REMAINING_POOL:
                basis_amount = remaining_pool
            else:
                basis_amount = remaining_pool

            # Calculate payment for this node
            payment = node.calculate_payment(
                available_pool=remaining_pool,
                basis_amount=basis_amount
            )

            # Record results
            node_result = {
                "node_id": node.node_id,
                "priority": node.priority.value,
                "payee_name": node.payee_name,
                "description": node.description,
                "payment": payment,
                "remaining_pool_before": remaining_pool,
                "remaining_pool_after": remaining_pool - payment
            }
            results["nodes_processed"].append(node_result)

            # Update payee totals
            if node.payee_name not in results["payee_totals"]:
                results["payee_totals"][node.payee_name] = Decimal("0")
            results["payee_totals"][node.payee_name] += payment

            # Update pools
            remaining_pool -= payment
            results["total_distributed"] += payment

            # Track net after distribution costs (for downstream calculations)
            if node.priority in [RecoupmentPriority.DISTRIBUTION_FEES, RecoupmentPriority.PA_EXPENSES]:
                net_after_distribution -= payment

        results["remaining_pool"] = remaining_pool

        # Calculate key metrics
        results["total_to_financiers"] = sum(
            payment
            for node_result in results["nodes_processed"]
            if self._get_node_by_id(node_result["node_id"]).payee_type in [PayeeType.LENDER, PayeeType.INVESTOR]
            for payment in [node_result["payment"]]
        )

        results["total_to_producers_talent"] = sum(
            payment
            for node_result in results["nodes_processed"]
            if self._get_node_by_id(node_result["node_id"]).payee_type in [PayeeType.PRODUCER, PayeeType.TALENT]
            for payment in [node_result["payment"]]
        )

        return results

    def _get_node_by_id(self, node_id: str) -> WaterfallNode:
        """Helper to get node by ID"""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise ValueError(f"Node {node_id} not found")
