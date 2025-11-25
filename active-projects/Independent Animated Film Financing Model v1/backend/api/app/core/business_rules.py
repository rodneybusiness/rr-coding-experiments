"""
Business Rules Configuration - Centralized Business Assumptions

This module centralizes all hardcoded business values and assumptions
that appear throughout the API layer. By consolidating these values,
we make it easier to:

1. Update business logic without changing code
2. Document business assumptions in one place
3. Maintain consistency across endpoints
4. Enable future configuration via database or environment variables

All values use Decimal for financial precision.
"""

from decimal import Decimal
from typing import Dict, List


# =============================================================================
# REVENUE & PROJECTION ASSUMPTIONS
# =============================================================================

# Expected revenue multiplier vs. project budget
# Used for scenario generation when actual revenue projections unavailable
REVENUE_MULTIPLIER_DEFAULT = Decimal("2.5")  # 2.5x budget is conservative industry estimate

# Default project budget for testing/samples (USD)
DEFAULT_PROJECT_BUDGET = Decimal("30000000")  # $30M


# =============================================================================
# TAX INCENTIVE ASSUMPTIONS
# =============================================================================

# Default tax credit capture rate estimate
# Used when actual incentive calculation not available
TAX_CAPTURE_RATE_ESTIMATE = Decimal("20.0")  # 20% of budget


# =============================================================================
# MONETIZATION RATES & DISCOUNTS
# =============================================================================

# Tax credit monetization options
# Direct receipt - wait 18-24 months for full value
DIRECT_RECEIPT_RATE = Decimal("1.00")  # 100% value, but delayed

# Bank loan against tax credits - advance rate
# Lender advances ~85% of face value, charges interest
BANK_LOAN_ADVANCE_RATE = Decimal("0.85")  # 15% cost for immediate liquidity

# Broker sale - purchase price as % of face value
# Broker purchases credits at discount for immediate cash
BROKER_SALE_RATE = Decimal("0.80")  # 20% discount for immediate sale


# =============================================================================
# CASH FLOW TIMING ASSUMPTIONS
# =============================================================================

# Tax incentive cash flow distribution
# Percentage of total received at expected timing quarter
CASH_FLOW_PRIMARY_DISTRIBUTION_PCT = Decimal("0.6")  # 60% at primary timing
CASH_FLOW_SECONDARY_DISTRIBUTION_PCT = Decimal("0.4")  # 40% in next quarter


# =============================================================================
# S-CURVE INVESTMENT DRAWDOWN DEFAULTS
# =============================================================================

# Default steepness of S-curve (higher = more rapid midpoint transition)
SCURVE_DEFAULT_STEEPNESS = 8.0  # Standard film production curve

# Default midpoint of S-curve (0-1 scale, where peak spending occurs)
SCURVE_DEFAULT_MIDPOINT = 0.4  # Peak spending at 40% through timeline


# =============================================================================
# SCENARIO GENERATION RULES
# =============================================================================

# Number of scenarios to generate per project
SCENARIOS_PER_PROJECT = 4

# Available scenario templates in priority order
SCENARIO_TEMPLATES: List[str] = [
    "debt_heavy",
    "equity_heavy",
    "balanced",
    "presale_focused",
    "incentive_maximized",
]


# =============================================================================
# FINANCIAL PERFORMANCE THRESHOLDS
# =============================================================================

# Equity IRR thresholds for strength/weakness analysis
EQUITY_IRR_EXCELLENT_THRESHOLD = Decimal("30.0")  # >= 30% is excellent
EQUITY_IRR_LOW_THRESHOLD = Decimal("20.0")  # < 20% is below target

# Tax incentive capture rate thresholds
TAX_RATE_EXCEPTIONAL_THRESHOLD = Decimal("20.0")  # >= 20% is exceptional
TAX_RATE_GOOD_THRESHOLD = Decimal("10.0")  # >= 10% is good, < 10% is limited

# Risk score thresholds (0-100 scale)
RISK_SCORE_LOW_THRESHOLD = Decimal("50.0")  # < 50 is low risk
RISK_SCORE_HIGH_THRESHOLD = Decimal("70.0")  # > 70 is high risk

# Debt coverage ratio thresholds
DEBT_COVERAGE_STRONG_THRESHOLD = Decimal("2.0")  # >= 2.0x is strong
DEBT_COVERAGE_WEAK_THRESHOLD = Decimal("1.5")  # < 1.5x is weak

# Cost of capital thresholds
COST_OF_CAPITAL_LOW_THRESHOLD = Decimal("10.0")  # < 10% is low
COST_OF_CAPITAL_HIGH_THRESHOLD = Decimal("12.0")  # > 12% is high

# Probability of recoupment threshold
RECOUPMENT_PROBABILITY_VERY_HIGH_THRESHOLD = Decimal("85.0")  # >= 85% is very high


# =============================================================================
# DEFAULT METRICS FOR SCENARIO EVALUATION
# =============================================================================

# Default risk score when not calculated
DEFAULT_RISK_SCORE = Decimal("50.0")  # Medium risk

# Default cost of capital when not calculated
DEFAULT_COST_OF_CAPITAL = Decimal("10.0")  # 10% WACC

# Default debt coverage ratio
DEFAULT_DEBT_COVERAGE_RATIO = Decimal("2.0")  # 2.0x coverage

# Default probability of recoupment
DEFAULT_RECOUPMENT_PROBABILITY = Decimal("80.0")  # 80% probability

# Default optimization score when calculation fails
DEFAULT_OPTIMIZATION_SCORE = Decimal("70.0")  # 70/100


# =============================================================================
# WATERFALL & DISTRIBUTION SETTINGS
# =============================================================================

# Default distribution fee rate (percentage)
# Typical distributor fee for handling revenue collection
DEFAULT_DISTRIBUTION_FEE_RATE = Decimal("30.0")  # 30% distribution fee


# =============================================================================
# CAPITAL DEPLOYMENT ESTIMATES
# =============================================================================

# Default capital commitment rate vs. budget
CAPITAL_COMMITMENT_RATE_ESTIMATE = Decimal("0.7")  # 70% of budget typically committed


# =============================================================================
# STRATEGIC SCORING THRESHOLDS
# =============================================================================

# Strategic composite score thresholds
STRATEGIC_SCORE_STRONG_THRESHOLD = Decimal("70.0")  # >= 70 is strong position
STRATEGIC_SCORE_WEAK_THRESHOLD = Decimal("50.0")  # < 50 is weak position

# Ownership score thresholds
OWNERSHIP_SCORE_STRONG_THRESHOLD = Decimal("70.0")  # >= 70 is strong retention
OWNERSHIP_SCORE_WEAK_THRESHOLD = Decimal("50.0")  # < 50 is significant dilution

# Control score thresholds
CONTROL_SCORE_STRONG_THRESHOLD = Decimal("70.0")  # >= 70 is strong control
CONTROL_SCORE_WEAK_THRESHOLD = Decimal("50.0")  # < 50 is limited control


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_monetization_options(gross_credit_amount: Decimal) -> Dict[str, Decimal]:
    """
    Calculate all monetization options for a given gross credit amount.

    Args:
        gross_credit_amount: Gross tax credit amount

    Returns:
        Dictionary with three monetization option amounts
    """
    return {
        "direct_receipt": gross_credit_amount * DIRECT_RECEIPT_RATE,
        "bank_loan": gross_credit_amount * BANK_LOAN_ADVANCE_RATE,
        "broker_sale": gross_credit_amount * BROKER_SALE_RATE,
    }


def get_scenario_templates(num_scenarios: int) -> List[str]:
    """
    Get the appropriate number of scenario templates.

    Args:
        num_scenarios: Number of scenarios requested

    Returns:
        List of template names to use
    """
    return SCENARIO_TEMPLATES[:min(num_scenarios, len(SCENARIO_TEMPLATES))]


def estimate_tax_incentives(total_budget: Decimal) -> Decimal:
    """
    Estimate total tax incentives based on budget.

    Args:
        total_budget: Project total budget

    Returns:
        Estimated tax incentive amount
    """
    return total_budget * (TAX_CAPTURE_RATE_ESTIMATE / Decimal("100"))


def estimate_committed_capital(total_budget: Decimal) -> Decimal:
    """
    Estimate committed capital based on budget.

    Args:
        total_budget: Project total budget

    Returns:
        Estimated committed capital amount
    """
    return total_budget * CAPITAL_COMMITMENT_RATE_ESTIMATE
