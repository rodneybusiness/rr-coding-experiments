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

# Add backend root to path (6 levels up from endpoints/incentives.py)
backend_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_root))

from engines.incentive_calculator.calculator import IncentiveCalculator, JurisdictionSpend
from engines.incentive_calculator.policy_loader import PolicyLoader
from engines.incentive_calculator.policy_registry import PolicyRegistry
from models.incentive_policy import MonetizationMethod

router = APIRouter()

# Initialize policy loader, registry, and calculator
policies_dir = backend_root / "data" / "policies"
policy_loader = PolicyLoader(policies_dir)
policy_registry = PolicyRegistry(policy_loader)
calculator = IncentiveCalculator(policy_registry)


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
        # Build JurisdictionSpend objects with policy lookups
        jurisdiction_spends_list = []
        monetization_preferences = {}

        for js in request.jurisdiction_spends:
            # Find applicable policies for this jurisdiction
            policies = policy_registry.get_by_jurisdiction(js.jurisdiction)

            if not policies:
                # Skip jurisdictions without policies
                continue

            policy_ids = [p.policy_id for p in policies]

            # Create JurisdictionSpend object
            spend = JurisdictionSpend(
                jurisdiction=js.jurisdiction,
                policy_ids=policy_ids,
                qualified_spend=Decimal(str(js.qualified_spend)),
                total_spend=Decimal(str(js.qualified_spend)),  # Use qualified as total for now
                labor_spend=Decimal(str(js.labor_spend)),
            )
            jurisdiction_spends_list.append(spend)

            # Set default monetization to DIRECT_CASH for all policies
            for policy_id in policy_ids:
                monetization_preferences[policy_id] = MonetizationMethod.DIRECT_CASH

        if not jurisdiction_spends_list:
            # No valid jurisdictions with policies found
            return IncentiveCalculationResponse(
                project_id=request.project_id,
                project_name=request.project_name,
                total_budget=request.total_budget,
                total_gross_credit=Decimal("0"),
                total_net_benefit=Decimal("0"),
                effective_rate=Decimal("0"),
                jurisdiction_breakdown=[],
                cash_flow_projection=[],
                monetization_options={
                    "direct_receipt": Decimal("0"),
                    "bank_loan": Decimal("0"),
                    "broker_sale": Decimal("0"),
                },
            )

        # Calculate incentives using the multi-jurisdiction method
        result = calculator.calculate_multi_jurisdiction(
            total_budget=Decimal(str(request.total_budget)),
            jurisdiction_spends=jurisdiction_spends_list,
            monetization_preferences=monetization_preferences,
        )

        # Build jurisdiction breakdown from results
        # Group results by jurisdiction
        jurisdiction_results = {}
        for jr in result.jurisdiction_results:
            jur = jr.jurisdiction
            if jur not in jurisdiction_results:
                jurisdiction_results[jur] = {
                    "policies": [],
                    "gross_credit": Decimal("0"),
                    "net_benefit": Decimal("0"),
                }
            jurisdiction_results[jur]["policies"].append(jr)
            jurisdiction_results[jur]["gross_credit"] += jr.gross_credit
            jurisdiction_results[jur]["net_benefit"] += jr.net_cash_benefit

        jurisdiction_breakdown = []
        for jurisdiction, data in jurisdiction_results.items():
            # Build policy credits
            policy_credits = [
                PolicyCredit(
                    policy_id=p.policy_id,
                    name=p.policy_name,
                    credit_amount=p.gross_credit,
                    credit_rate=p.effective_rate,
                    qualified_base=p.qualified_spend,
                )
                for p in data["policies"]
            ]

            # Calculate effective rate for this jurisdiction
            total_qualified = sum(p.qualified_spend for p in data["policies"])
            effective_rate = (
                (data["net_benefit"] / total_qualified * Decimal("100"))
                if total_qualified > 0 else Decimal("0")
            )

            jurisdiction_breakdown.append(
                JurisdictionBreakdown(
                    jurisdiction=jurisdiction,
                    gross_credit=data["gross_credit"],
                    net_benefit=data["net_benefit"],
                    effective_rate=effective_rate,
                    policies=policy_credits,
                )
            )

        # Build cash flow projection (estimate based on timing)
        # Approximate quarterly distribution over 2 years
        total_net = result.total_net_benefits
        avg_timing_months = float(result.total_timing_weighted_months or 12)
        avg_timing_quarters = max(1, int(avg_timing_months / 3))

        cash_flow_projection = []
        for q in range(1, min(9, avg_timing_quarters + 2)):  # Up to 8 quarters
            if q < avg_timing_quarters:
                amount = Decimal("0")
            elif q == avg_timing_quarters:
                amount = total_net * Decimal("0.6")  # 60% at expected timing
            elif q == avg_timing_quarters + 1:
                amount = total_net * Decimal("0.4")  # 40% in next quarter
            else:
                amount = Decimal("0")

            if amount > 0:
                cash_flow_projection.append(
                    CashFlowQuarter(quarter=q, amount=amount)
                )

        # Calculate monetization options
        total_gross = result.total_gross_credits
        monetization_options = {
            "direct_receipt": total_gross,  # 100% value, wait 18-24 months
            "bank_loan": total_gross * Decimal("0.85"),  # 15% cost (interest)
            "broker_sale": total_gross * Decimal("0.80"),  # 20% discount
        }

        return IncentiveCalculationResponse(
            project_id=request.project_id,
            project_name=request.project_name,
            total_budget=request.total_budget,
            total_gross_credit=result.total_gross_credits,
            total_net_benefit=result.total_net_benefits,
            effective_rate=result.blended_effective_rate,
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
        all_policies = policy_loader.load_all()
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
        jurisdiction: Jurisdiction name (e.g., "Canada", "United Kingdom")

    Returns:
        List of policies with details

    Raises:
        HTTPException: If jurisdiction not found
    """
    try:
        policies = policy_registry.get_by_jurisdiction(jurisdiction)

        if not policies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No policies found for jurisdiction: {jurisdiction}",
            )

        return [
            {
                "policy_id": policy.policy_id,
                "name": policy.program_name,
                "jurisdiction": policy.jurisdiction,
                "credit_type": policy.incentive_type.value,
                "base_rate": float(policy.headline_rate),
                "labor_rate": float(policy.labor_rate) if hasattr(policy, 'labor_rate') and policy.labor_rate else None,
                "caps": {
                    "per_project_cap": (
                        float(policy.per_project_cap) if policy.per_project_cap else None
                    ),
                    "annual_budget": (
                        float(policy.annual_program_budget) if policy.annual_program_budget else None
                    ),
                },
                "requirements": {
                    "min_spend": (
                        float(policy.minimum_total_spend)
                        if policy.minimum_total_spend
                        else None
                    ),
                    "min_local_spend_pct": (
                        float(policy.minimum_local_spend)
                        if policy.minimum_local_spend
                        else None
                    ),
                    "cultural_test_required": policy.cultural_test.requires_cultural_test,
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
