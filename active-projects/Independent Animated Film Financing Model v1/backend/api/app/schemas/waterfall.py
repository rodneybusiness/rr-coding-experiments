"""
API Schemas for Waterfall Analysis (Engine 2)
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
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

    model_config = ConfigDict(
        json_schema_extra={
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
    )


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

    model_config = ConfigDict(
        json_schema_extra={
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
    )


# ===== Sensitivity Analysis Schemas =====


class SensitivityVariableInput(BaseModel):
    """Input for a variable to analyze in sensitivity analysis."""
    variable_name: str = Field(..., description="Variable identifier (e.g., 'revenue_multiplier', 'interest_rate')")
    base_value: Decimal = Field(..., description="Base case value for this variable")
    low_value: Decimal = Field(..., description="Pessimistic/low case value")
    high_value: Decimal = Field(..., description="Optimistic/high case value")
    variable_type: str = Field(default="revenue", description="Type of variable (revenue, cost, rate)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "variable_name": "revenue_multiplier",
                "base_value": 75000000,
                "low_value": 60000000,
                "high_value": 90000000,
                "variable_type": "revenue"
            }
        }
    )


class SensitivityAnalysisRequest(BaseModel):
    """Request for sensitivity analysis."""
    project_id: str = Field(..., description="Unique project identifier")
    waterfall_id: str = Field(..., description="Waterfall structure ID")
    base_total_revenue: Decimal = Field(..., gt=0, description="Base case total ultimate revenue")
    release_strategy: str = Field(default="wide_theatrical", description="Release strategy type")
    variation_percentage: Optional[Decimal] = Field(
        default=Decimal("20"),
        ge=0,
        le=100,
        description="Percentage variation for auto-generated ranges (e.g., 20 = +/-20%)"
    )
    custom_variables: Optional[List[SensitivityVariableInput]] = Field(
        default=None,
        description="Custom variables with explicit ranges (overrides auto-generated)"
    )
    target_metrics: List[str] = Field(
        default=["equity_irr", "overall_recovery_rate"],
        description="Metrics to analyze (e.g., equity_irr, overall_recovery_rate)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "proj_123",
                "waterfall_id": "waterfall_789",
                "base_total_revenue": 75000000,
                "release_strategy": "wide_theatrical",
                "variation_percentage": 20,
                "custom_variables": None,
                "target_metrics": ["equity_irr", "overall_recovery_rate"]
            }
        }
    )


class SensitivityResultData(BaseModel):
    """Sensitivity result for a single variable."""
    variable_name: str
    variable_type: str
    base_value: Decimal
    low_value: Decimal
    high_value: Decimal
    base_case_metric: Decimal
    low_case_metric: Decimal
    high_case_metric: Decimal
    delta_low: Decimal
    delta_high: Decimal
    impact_score: Decimal


class TornadoChartDataSchema(BaseModel):
    """Tornado chart data for visualization."""
    target_metric: str = Field(..., description="The metric being analyzed (e.g., equity_irr)")
    variables: List[str] = Field(..., description="Variable names sorted by impact (descending)")
    base_value: Decimal = Field(..., description="Base case value of the metric")
    low_deltas: List[Decimal] = Field(..., description="Negative deltas from base (for low scenarios)")
    high_deltas: List[Decimal] = Field(..., description="Positive deltas from base (for high scenarios)")


class SensitivityAnalysisResponse(BaseModel):
    """Response from sensitivity analysis."""
    project_id: str
    base_total_revenue: Decimal
    target_metrics: List[str]
    results_by_metric: Dict[str, List[SensitivityResultData]] = Field(
        ...,
        description="Sensitivity results grouped by target metric, sorted by impact"
    )
    tornado_charts: Dict[str, TornadoChartDataSchema] = Field(
        ...,
        description="Tornado chart data for each target metric"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "proj_123",
                "base_total_revenue": 75000000,
                "target_metrics": ["equity_irr"],
                "results_by_metric": {
                    "equity_irr": [
                        {
                            "variable_name": "revenue_multiplier",
                            "variable_type": "revenue",
                            "base_value": 75000000,
                            "low_value": 60000000,
                            "high_value": 90000000,
                            "base_case_metric": 28.5,
                            "low_case_metric": 15.2,
                            "high_case_metric": 42.8,
                            "delta_low": 13.3,
                            "delta_high": 14.3,
                            "impact_score": 14.3
                        }
                    ]
                },
                "tornado_charts": {
                    "equity_irr": {
                        "target_metric": "equity_irr",
                        "variables": ["revenue_multiplier", "interest_rate"],
                        "base_value": 28.5,
                        "low_deltas": [-13.3, -5.2],
                        "high_deltas": [14.3, 6.1]
                    }
                }
            }
        }
    )
