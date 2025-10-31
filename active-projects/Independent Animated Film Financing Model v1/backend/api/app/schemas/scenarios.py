"""
API Schemas for Scenario Optimizer (Engine 3)
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class ObjectiveWeights(BaseModel):
    """Optimization objective weights."""
    equity_irr: Decimal = Field(default=Decimal("30.0"), ge=0, le=100)
    cost_of_capital: Decimal = Field(default=Decimal("25.0"), ge=0, le=100)
    tax_incentive_capture: Decimal = Field(default=Decimal("20.0"), ge=0, le=100)
    risk_minimization: Decimal = Field(default=Decimal("25.0"), ge=0, le=100)


class ScenarioGenerationRequest(BaseModel):
    """Request for scenario generation."""
    project_id: str = Field(..., description="Unique project identifier")
    project_name: str = Field(..., description="Project name")
    project_budget: Decimal = Field(..., gt=0, description="Total project budget")
    waterfall_id: str = Field(..., description="Waterfall structure ID")
    objective_weights: Optional[ObjectiveWeights] = Field(default=None)
    num_scenarios: int = Field(default=4, ge=1, le=10, description="Number of scenarios to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj_123",
                "project_name": "Animated Feature - Sky Warriors",
                "project_budget": 30000000,
                "waterfall_id": "waterfall_789",
                "objective_weights": {
                    "equity_irr": 30.0,
                    "cost_of_capital": 25.0,
                    "tax_incentive_capture": 20.0,
                    "risk_minimization": 25.0
                },
                "num_scenarios": 4
            }
        }


class CapitalStructure(BaseModel):
    """Capital structure breakdown."""
    senior_debt: Decimal = Field(default=Decimal("0"))
    gap_financing: Decimal = Field(default=Decimal("0"))
    mezzanine_debt: Decimal = Field(default=Decimal("0"))
    equity: Decimal = Field(default=Decimal("0"))
    tax_incentives: Decimal = Field(default=Decimal("0"))
    presales: Decimal = Field(default=Decimal("0"))
    grants: Decimal = Field(default=Decimal("0"))


class ScenarioMetrics(BaseModel):
    """Metrics for a scenario."""
    equity_irr: Decimal
    cost_of_capital: Decimal
    tax_incentive_rate: Decimal
    risk_score: Decimal
    debt_coverage_ratio: Decimal
    probability_of_recoupment: Decimal
    total_debt: Decimal
    total_equity: Decimal
    debt_to_equity_ratio: Optional[Decimal]


class Scenario(BaseModel):
    """Complete scenario with structure and metrics."""
    scenario_id: str
    scenario_name: str
    optimization_score: Decimal
    capital_structure: CapitalStructure
    metrics: ScenarioMetrics
    strengths: List[str]
    weaknesses: List[str]
    validation_passed: bool
    validation_errors: List[str] = Field(default_factory=list)


class ScenarioGenerationResponse(BaseModel):
    """Response from scenario generation."""
    project_id: str
    project_name: str
    project_budget: Decimal
    scenarios: List[Scenario]
    best_scenario_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj_123",
                "project_name": "Animated Feature - Sky Warriors",
                "project_budget": 30000000,
                "scenarios": [
                    {
                        "scenario_id": "scenario_tax_optimized",
                        "scenario_name": "Tax Optimized",
                        "optimization_score": 88.2,
                        "capital_structure": {
                            "senior_debt": 9000000,
                            "gap_financing": 3000000,
                            "mezzanine_debt": 2000000,
                            "equity": 10000000,
                            "tax_incentives": 6000000,
                            "presales": 0,
                            "grants": 0
                        },
                        "metrics": {
                            "equity_irr": 32.1,
                            "cost_of_capital": 10.5,
                            "tax_incentive_rate": 20.0,
                            "risk_score": 55.0,
                            "debt_coverage_ratio": 2.2,
                            "probability_of_recoupment": 85.5,
                            "total_debt": 14000000,
                            "total_equity": 10000000,
                            "debt_to_equity_ratio": 1.4
                        },
                        "strengths": [
                            "Exceptional tax incentive capture (20%)",
                            "Highest equity returns (32.1% IRR)",
                            "Low risk profile"
                        ],
                        "weaknesses": [
                            "Requires more equity capital"
                        ],
                        "validation_passed": True,
                        "validation_errors": []
                    }
                ],
                "best_scenario_id": "scenario_tax_optimized"
            }
        }


class ScenarioComparisonRequest(BaseModel):
    """Request to compare specific scenarios."""
    project_id: str
    scenario_ids: List[str] = Field(..., min_length=2, max_length=5)


class TradeOffPoint(BaseModel):
    """Point on trade-off frontier."""
    scenario_id: str
    scenario_name: str
    x_value: Decimal
    y_value: Decimal
    optimization_score: Decimal


class TradeOffAnalysis(BaseModel):
    """Trade-off analysis between two objectives."""
    x_axis: str
    y_axis: str
    points: List[TradeOffPoint]
    insights: List[str]


class ScenarioComparisonResponse(BaseModel):
    """Response from scenario comparison."""
    project_id: str
    scenarios: List[Scenario]
    trade_off_analyses: List[TradeOffAnalysis]
    recommendation: str
