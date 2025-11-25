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
