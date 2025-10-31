"""
Tax Incentive Calculator Endpoints (Engine 1)
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from decimal import Decimal

from app.schemas.incentives import (
    IncentiveCalculationRequest,
    IncentiveCalculationResponse,
    JurisdictionBreakdown,
    PolicyCredit,
    CashFlowQuarter,
)

# Import Engine 1
import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_root))

from engines.incentive_calculator.incentive_calculator import IncentiveCalculator
from data_curation.policy_loader import PolicyLoader

router = APIRouter()

# Initialize policy loader and calculator
policy_loader = PolicyLoader()
calculator = IncentiveCalculator(policy_loader)


@router.post(
    "/calculate",
    response_model=IncentiveCalculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Tax Incentives",
    description="Calculate tax credits and incentives for a film project across multiple jurisdictions",
)
async def calculate_incentives(request: IncentiveCalculationRequest):
    """
    Calculate tax incentives for a film project.

    This endpoint:
    1. Analyzes spending across multiple jurisdictions
    2. Matches spending to applicable tax policies
    3. Calculates gross credits and net benefits
    4. Projects cash flow timing
    5. Provides monetization options

    Args:
        request: Project details and jurisdiction spends

    Returns:
        Complete tax incentive analysis with breakdowns and projections

    Raises:
        HTTPException: If calculation fails or validation errors occur
    """
    try:
        # Convert request to calculator format
        jurisdiction_spends = {
            js.jurisdiction: {
                "qualified_spend": js.qualified_spend,
                "labor_spend": js.labor_spend,
            }
            for js in request.jurisdiction_spends
        }

        # Calculate incentives
        result = calculator.calculate_incentives(
            project_id=request.project_id,
            jurisdiction_spends=jurisdiction_spends,
            total_budget=request.total_budget,
        )

        # Build jurisdiction breakdown
        jurisdiction_breakdown = []
        for jurisdiction, data in result["jurisdiction_breakdown"].items():
            # Build policy credits
            policy_credits = [
                PolicyCredit(
                    policy_id=policy["policy_id"],
                    name=policy["policy_name"],
                    credit_amount=policy["credit_amount"],
                    credit_rate=policy["credit_rate"],
                    qualified_base=policy["qualified_base"],
                )
                for policy in data["applicable_policies"]
            ]

            jurisdiction_breakdown.append(
                JurisdictionBreakdown(
                    jurisdiction=jurisdiction,
                    gross_credit=data["gross_credit"],
                    net_benefit=data["net_benefit"],
                    effective_rate=data["effective_rate"],
                    policies=policy_credits,
                )
            )

        # Build cash flow projection
        cash_flow_projection = [
            CashFlowQuarter(quarter=cf["quarter"], amount=cf["amount"])
            for cf in result["cash_flow_projection"]
        ]

        # Calculate monetization options
        total_gross = result["total_gross_credit"]
        monetization_options = {
            "direct_receipt": total_gross,  # 100% value, wait 18-24 months
            "bank_loan": total_gross * Decimal("0.85"),  # 15% cost (interest)
            "broker_sale": total_gross * Decimal("0.80"),  # 20% discount
        }

        return IncentiveCalculationResponse(
            project_id=request.project_id,
            project_name=request.project_name,
            total_budget=request.total_budget,
            total_gross_credit=result["total_gross_credit"],
            total_net_benefit=result["total_net_benefit"],
            effective_rate=result["effective_rate"],
            jurisdiction_breakdown=jurisdiction_breakdown,
            cash_flow_projection=cash_flow_projection,
            monetization_options=monetization_options,
        )

    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required field: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}",
        )


@router.get(
    "/jurisdictions",
    response_model=List[str],
    summary="List Available Jurisdictions",
    description="Get list of jurisdictions with available tax incentive policies",
)
async def list_jurisdictions():
    """
    List all jurisdictions with tax incentive policies.

    Returns:
        List of jurisdiction names
    """
    try:
        # Get all policies and extract unique jurisdictions
        all_policies = policy_loader.get_all_policies()
        jurisdictions = sorted(set(policy.jurisdiction for policy in all_policies))
        return jurisdictions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load jurisdictions: {str(e)}",
        )


@router.get(
    "/jurisdictions/{jurisdiction}/policies",
    summary="Get Policies for Jurisdiction",
    description="Get all tax incentive policies available in a specific jurisdiction",
)
async def get_jurisdiction_policies(jurisdiction: str):
    """
    Get all policies for a specific jurisdiction.

    Args:
        jurisdiction: Jurisdiction name (e.g., "Quebec, Canada")

    Returns:
        List of policies with details

    Raises:
        HTTPException: If jurisdiction not found
    """
    try:
        policies = policy_loader.get_policies_by_jurisdiction(jurisdiction)

        if not policies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No policies found for jurisdiction: {jurisdiction}",
            )

        return [
            {
                "policy_id": policy.policy_id,
                "name": policy.policy_name,
                "jurisdiction": policy.jurisdiction,
                "credit_type": policy.credit_type,
                "base_rate": float(policy.base_rate),
                "labor_rate": float(policy.labor_rate) if policy.labor_rate else None,
                "caps": {
                    "per_project_cap": (
                        float(policy.per_project_cap) if policy.per_project_cap else None
                    ),
                    "annual_budget": (
                        float(policy.annual_budget) if policy.annual_budget else None
                    ),
                },
                "requirements": {
                    "min_spend": (
                        float(policy.min_spend_requirement)
                        if policy.min_spend_requirement
                        else None
                    ),
                    "min_local_spend_pct": (
                        float(policy.min_local_spend_pct)
                        if policy.min_local_spend_pct
                        else None
                    ),
                    "cultural_test_required": policy.cultural_test_required,
                },
            }
            for policy in policies
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load policies: {str(e)}",
        )
