"""
API Schemas for Waterfall Analysis (Engine 2)
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class WaterfallExecutionRequest(BaseModel):
    """Request for waterfall execution."""
    project_id: str = Field(..., description="Unique project identifier")
    capital_stack_id: str = Field(..., description="Capital stack ID to analyze")
    waterfall_id: str = Field(..., description="Waterfall structure ID")
    total_revenue: Decimal = Field(..., gt=0, description="Total ultimate revenue projection")
    release_strategy: str = Field(default="wide_theatrical", description="Release strategy type")
    run_monte_carlo: bool = Field(default=True, description="Whether to run Monte Carlo simulation")
    monte_carlo_iterations: int = Field(default=1000, ge=100, le=10000)

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj_123",
                "capital_stack_id": "stack_456",
                "waterfall_id": "waterfall_789",
                "total_revenue": 75000000,
                "release_strategy": "wide_theatrical",
                "run_monte_carlo": True,
                "monte_carlo_iterations": 1000
            }
        }


class StakeholderReturn(BaseModel):
    """Returns for a single stakeholder."""
    stakeholder_id: str
    stakeholder_name: str
    stakeholder_type: str
    invested: Decimal
    received: Decimal
    profit: Decimal
    cash_on_cash: Optional[Decimal]
    irr: Optional[Decimal]


class QuarterlyDistribution(BaseModel):
    """Distribution amounts by stakeholder for a quarter."""
    quarter: int
    distributions: Dict[str, Decimal]


class RevenueWindow(BaseModel):
    """Revenue from a specific distribution window."""
    window: str
    revenue: Decimal
    percentage: Decimal


class MonteCarloPercentiles(BaseModel):
    """Percentile results from Monte Carlo simulation."""
    p10: Decimal
    p50: Decimal
    p90: Decimal


class MonteCarloResults(BaseModel):
    """Monte Carlo simulation results."""
    equity_irr: MonteCarloPercentiles
    probability_of_recoupment: Dict[str, Decimal]


class WaterfallExecutionResponse(BaseModel):
    """Response from waterfall execution."""
    project_id: str
    total_revenue: Decimal
    total_distributed: Decimal
    total_recouped: Decimal
    stakeholder_returns: List[StakeholderReturn]
    distribution_timeline: List[QuarterlyDistribution]
    revenue_by_window: List[RevenueWindow]
    monte_carlo_results: Optional[MonteCarloResults]

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj_123",
                "total_revenue": 75000000,
                "total_distributed": 68250000,
                "total_recouped": 45000000,
                "stakeholder_returns": [
                    {
                        "stakeholder_id": "senior-debt",
                        "stakeholder_name": "Senior Debt",
                        "stakeholder_type": "Debt",
                        "invested": 12000000,
                        "received": 13440000,
                        "profit": 1440000,
                        "cash_on_cash": 1.12,
                        "irr": 15.5
                    }
                ],
                "distribution_timeline": [
                    {
                        "quarter": 1,
                        "distributions": {
                            "senior-debt": 3000000,
                            "gap-financing": 0
                        }
                    }
                ],
                "revenue_by_window": [
                    {
                        "window": "Theatrical",
                        "revenue": 30000000,
                        "percentage": 40.0
                    }
                ],
                "monte_carlo_results": {
                    "equity_irr": {
                        "p10": 12.5,
                        "p50": 28.5,
                        "p90": 45.2
                    },
                    "probability_of_recoupment": {
                        "senior-debt": 98.5,
                        "equity": 78.9
                    }
                }
            }
        }
