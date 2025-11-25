"""
API Schemas for Tax Incentive Calculator (Engine 1)
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class JurisdictionSpendInput(BaseModel):
    """Jurisdiction spending input."""
    jurisdiction: str = Field(..., description="Jurisdiction name (e.g., 'Quebec, Canada')")
    qualified_spend: Decimal = Field(..., ge=0, description="Total qualified spend in jurisdiction")
    labor_spend: Decimal = Field(..., ge=0, description="Labor spend in jurisdiction")


class IncentiveCalculationRequest(BaseModel):
    """Request for tax incentive calculation."""
    project_id: str = Field(..., description="Unique project identifier")
    project_name: str = Field(..., description="Project name")
    total_budget: Decimal = Field(..., gt=0, description="Total project budget")
    jurisdiction_spends: List[JurisdictionSpendInput] = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "proj_123",
                "project_name": "Animated Feature - Sky Warriors",
                "total_budget": 30000000,
                "jurisdiction_spends": [
                    {
                        "jurisdiction": "Quebec, Canada",
                        "qualified_spend": 16500000,
                        "labor_spend": 12000000
                    }
                ]
            }
        }
    )


class PolicyCredit(BaseModel):
    """Individual policy credit detail."""
    policy_id: str
    name: str
    credit_amount: Decimal
    credit_rate: Decimal
    qualified_base: Decimal


class JurisdictionBreakdown(BaseModel):
    """Tax credit breakdown for a jurisdiction."""
    jurisdiction: str
    gross_credit: Decimal
    net_benefit: Decimal
    effective_rate: Decimal
    policies: List[PolicyCredit]


class CashFlowQuarter(BaseModel):
    """Cash flow for a single quarter."""
    quarter: int
    amount: Decimal


class IncentiveCalculationResponse(BaseModel):
    """Response from tax incentive calculation."""
    project_id: str
    project_name: str
    total_budget: Decimal
    total_gross_credit: Decimal
    total_net_benefit: Decimal
    effective_rate: Decimal
    jurisdiction_breakdown: List[JurisdictionBreakdown]
    cash_flow_projection: List[CashFlowQuarter]
    monetization_options: Dict[str, Decimal]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "proj_123",
                "project_name": "Animated Feature - Sky Warriors",
                "total_budget": 30000000,
                "total_gross_credit": 5790000,
                "total_net_benefit": 4632000,
                "effective_rate": 15.44,
                "jurisdiction_breakdown": [
                    {
                        "jurisdiction": "Quebec, Canada",
                        "gross_credit": 5790000,
                        "net_benefit": 4632000,
                        "effective_rate": 15.44,
                        "policies": [
                            {
                                "policy_id": "cptc_001",
                                "name": "Canadian Film or Video Production Tax Credit",
                                "credit_amount": 3000000,
                                "credit_rate": 25.0,
                                "qualified_base": 12000000
                            }
                        ]
                    }
                ],
                "cash_flow_projection": [
                    {"quarter": 1, "amount": 0},
                    {"quarter": 6, "amount": 2316000}
                ],
                "monetization_options": {
                    "direct_receipt": 5790000,
                    "bank_loan": 4921500,
                    "broker_sale": 4632000
                }
            }
        }
    )


# Labor Cap Enforcement Schemas

class LaborAdjustmentDetail(BaseModel):
    """Details of a labor cap adjustment."""
    type: str = Field(..., description="Type of adjustment (percent_cap, category_rate, labor_only, etc.)")
    original: Decimal = Field(..., description="Original amount before adjustment")
    adjusted: Decimal = Field(..., description="Amount after adjustment")
    reduction: Decimal = Field(..., description="Amount reduced (0 for uplifts)")
    description: str = Field(..., description="Human-readable description of adjustment")


class LaborCapCalculationRequest(BaseModel):
    """Request for labor cap enforcement calculation."""
    policy_id: str = Field(..., description="Tax incentive policy ID")
    qualified_spend: Decimal = Field(..., gt=0, description="Total qualified production expenditure")
    labor_spend: Decimal = Field(..., ge=0, description="Total labor spend (subset of qualified spend)")
    vfx_labor_spend: Optional[Decimal] = Field(None, ge=0, description="VFX/animation labor spend (subset of labor spend)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "policy_id": "cptc_001",
                "qualified_spend": 10000000,
                "labor_spend": 6000000,
                "vfx_labor_spend": 2000000
            }
        }
    )


class LaborCapCalculationResponse(BaseModel):
    """Response from labor cap enforcement calculation."""
    adjusted_qualified_spend: Decimal = Field(..., description="Qualified spend after labor caps applied")
    adjusted_labor_spend: Decimal = Field(..., description="Labor spend after caps applied")
    labor_credit_component: Decimal = Field(..., description="Credit from labor spend")
    non_labor_credit_component: Decimal = Field(..., description="Credit from non-labor spend")
    total_credit: Decimal = Field(..., description="Total tax credit after labor caps")
    effective_rate: Decimal = Field(..., description="Effective credit rate (percentage)")
    adjustments: List[LaborAdjustmentDetail] = Field(default_factory=list, description="List of adjustments applied")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    labor_cap_applied: bool = Field(..., description="Whether labor percentage cap was triggered")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "adjusted_qualified_spend": 10000000,
                "adjusted_labor_spend": 6000000,
                "labor_credit_component": 1500000,
                "non_labor_credit_component": 800000,
                "total_credit": 2300000,
                "effective_rate": 23.0,
                "adjustments": [
                    {
                        "type": "percent_cap",
                        "original": 7000000,
                        "adjusted": 6000000,
                        "reduction": 1000000,
                        "description": "Labor capped at 60% of qualified spend"
                    }
                ],
                "warnings": [],
                "labor_cap_applied": True
            }
        }
    )


# Investment Drawdown Schemas

class InvestmentDrawdownRequest(BaseModel):
    """Request for S-curve investment drawdown calculation."""
    total_investment: Decimal = Field(..., gt=0, description="Total investment amount to be drawn down")
    draw_periods: int = Field(..., gt=0, le=48, description="Number of periods (months or quarters)")
    steepness: Optional[float] = Field(8.0, gt=0, le=20, description="S-curve steepness (higher = sharper transition)")
    midpoint: Optional[float] = Field(0.4, ge=0, le=1, description="S-curve midpoint (0.0-1.0, where peak occurs)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_investment": 10000000,
                "draw_periods": 12,
                "steepness": 8.0,
                "midpoint": 0.4
            }
        }
    )


class InvestmentDrawdownResponse(BaseModel):
    """Response from S-curve investment drawdown calculation."""
    total_investment: Decimal = Field(..., description="Total investment amount")
    draw_periods: int = Field(..., description="Number of draw periods")
    quarterly_draws: List[Decimal] = Field(..., description="Draw amount for each period")
    cumulative_draws: List[Decimal] = Field(..., description="Cumulative drawn by end of each period")
    steepness: float = Field(..., description="S-curve steepness parameter used")
    midpoint: float = Field(..., description="S-curve midpoint parameter used")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_investment": 10000000,
                "draw_periods": 12,
                "quarterly_draws": [
                    125000, 187500, 312500, 625000,
                    1250000, 1875000, 1875000, 1250000,
                    625000, 312500, 187500, 125000
                ],
                "cumulative_draws": [
                    125000, 312500, 625000, 1250000,
                    2500000, 4375000, 6250000, 7500000,
                    8125000, 8437500, 8625000, 10000000
                ],
                "steepness": 8.0,
                "midpoint": 0.4
            }
        }
    )
