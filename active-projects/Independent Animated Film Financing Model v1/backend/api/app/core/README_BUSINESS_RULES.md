# Business Rules Configuration - Quick Reference

## Import and Use

```python
from app.core import business_rules
```

## Common Usage Patterns

### 1. Tax Credit Monetization Options

**Instead of:**
```python
# ❌ OLD WAY - Hardcoded values
monetization_options = {
    "direct_receipt": total_gross,
    "bank_loan": total_gross * Decimal("0.85"),
    "broker_sale": total_gross * Decimal("0.80"),
}
```

**Use:**
```python
# ✅ NEW WAY - Centralized configuration
monetization_options = business_rules.get_monetization_options(total_gross)
```

---

### 2. Scenario Generation

**Instead of:**
```python
# ❌ OLD WAY - Hardcoded template list
all_templates = ["debt_heavy", "equity_heavy", "balanced", "presale_focused", "incentive_maximized"]
templates = all_templates[:num_scenarios]
```

**Use:**
```python
# ✅ NEW WAY - Use helper function
templates = business_rules.get_scenario_templates(num_scenarios)
```

---

### 3. Revenue Projections

**Instead of:**
```python
# ❌ OLD WAY - Magic number
revenue_projection = budget * Decimal("2.5")
```

**Use:**
```python
# ✅ NEW WAY - Named constant with documentation
revenue_projection = budget * business_rules.REVENUE_MULTIPLIER_DEFAULT
```

---

### 4. Tax Incentive Estimates

**Instead of:**
```python
# ❌ OLD WAY - Hardcoded percentage
tax_estimate = budget * 0.20
```

**Use:**
```python
# ✅ NEW WAY - Helper function or constant
tax_estimate = business_rules.estimate_tax_incentives(budget)
# OR
tax_estimate = budget * (business_rules.TAX_CAPTURE_RATE_ESTIMATE / Decimal("100"))
```

---

### 5. Performance Thresholds

**Instead of:**
```python
# ❌ OLD WAY - Inline comparison with magic number
if metrics.equity_irr >= Decimal("30.0"):
    strengths.append("Excellent equity returns")
elif metrics.equity_irr < Decimal("20.0"):
    weaknesses.append("Lower equity returns")
```

**Use:**
```python
# ✅ NEW WAY - Named thresholds
if metrics.equity_irr >= business_rules.EQUITY_IRR_EXCELLENT_THRESHOLD:
    strengths.append("Excellent equity returns")
elif metrics.equity_irr < business_rules.EQUITY_IRR_LOW_THRESHOLD:
    weaknesses.append("Lower equity returns")
```

---

### 6. Default Values

**Instead of:**
```python
# ❌ OLD WAY - Hardcoded defaults
risk_score = Decimal("50")
cost_of_capital = Decimal("10")
debt_coverage = Decimal("2.0")
```

**Use:**
```python
# ✅ NEW WAY - Documented defaults
risk_score = business_rules.DEFAULT_RISK_SCORE
cost_of_capital = business_rules.DEFAULT_COST_OF_CAPITAL
debt_coverage = business_rules.DEFAULT_DEBT_COVERAGE_RATIO
```

---

### 7. S-Curve Parameters

**Instead of:**
```python
# ❌ OLD WAY - Hardcoded defaults
drawdown = InvestmentDrawdown.create(
    total_investment=amount,
    draw_periods=periods,
    steepness=request.steepness or 8.0,
    midpoint=request.midpoint or 0.4,
)
```

**Use:**
```python
# ✅ NEW WAY - Named constants
drawdown = InvestmentDrawdown.create(
    total_investment=amount,
    draw_periods=periods,
    steepness=request.steepness or business_rules.SCURVE_DEFAULT_STEEPNESS,
    midpoint=request.midpoint or business_rules.SCURVE_DEFAULT_MIDPOINT,
)
```

---

### 8. Cash Flow Distribution

**Instead of:**
```python
# ❌ OLD WAY - Magic percentages
primary = total * Decimal("0.6")
secondary = total * Decimal("0.4")
```

**Use:**
```python
# ✅ NEW WAY - Named distribution percentages
primary = total * business_rules.CASH_FLOW_PRIMARY_DISTRIBUTION_PCT
secondary = total * business_rules.CASH_FLOW_SECONDARY_DISTRIBUTION_PCT
```

---

## All Available Constants

### Revenue & Projections
- `REVENUE_MULTIPLIER_DEFAULT` - Expected revenue vs. budget (2.5x)
- `DEFAULT_PROJECT_BUDGET` - Default test budget ($30M)

### Tax Incentives
- `TAX_CAPTURE_RATE_ESTIMATE` - Default capture rate (20%)

### Monetization Rates
- `DIRECT_RECEIPT_RATE` - Full value, delayed (100%)
- `BANK_LOAN_ADVANCE_RATE` - Advance rate (85%)
- `BROKER_SALE_RATE` - Sale discount (80%)

### Cash Flow Timing
- `CASH_FLOW_PRIMARY_DISTRIBUTION_PCT` - Primary timing (60%)
- `CASH_FLOW_SECONDARY_DISTRIBUTION_PCT` - Secondary timing (40%)

### S-Curve Defaults
- `SCURVE_DEFAULT_STEEPNESS` - Curve steepness (8.0)
- `SCURVE_DEFAULT_MIDPOINT` - Peak spending point (0.4)

### Scenario Generation
- `SCENARIOS_PER_PROJECT` - Default count (4)
- `SCENARIO_TEMPLATES` - Available templates list

### Performance Thresholds
- `EQUITY_IRR_EXCELLENT_THRESHOLD` - Excellent IRR (30%)
- `EQUITY_IRR_LOW_THRESHOLD` - Low IRR (20%)
- `TAX_RATE_EXCEPTIONAL_THRESHOLD` - Exceptional tax (20%)
- `TAX_RATE_GOOD_THRESHOLD` - Good tax (10%)
- `RISK_SCORE_LOW_THRESHOLD` - Low risk (50)
- `RISK_SCORE_HIGH_THRESHOLD` - High risk (70)
- `DEBT_COVERAGE_STRONG_THRESHOLD` - Strong coverage (2.0x)
- `DEBT_COVERAGE_WEAK_THRESHOLD` - Weak coverage (1.5x)
- `COST_OF_CAPITAL_LOW_THRESHOLD` - Low cost (10%)
- `COST_OF_CAPITAL_HIGH_THRESHOLD` - High cost (12%)
- `RECOUPMENT_PROBABILITY_VERY_HIGH_THRESHOLD` - Very high (85%)

### Default Metrics
- `DEFAULT_RISK_SCORE` - Medium risk (50)
- `DEFAULT_COST_OF_CAPITAL` - Standard WACC (10%)
- `DEFAULT_DEBT_COVERAGE_RATIO` - Standard coverage (2.0x)
- `DEFAULT_RECOUPMENT_PROBABILITY` - Standard probability (80%)
- `DEFAULT_OPTIMIZATION_SCORE` - Fallback score (70/100)

### Waterfall & Distribution
- `DEFAULT_DISTRIBUTION_FEE_RATE` - Distributor fee (30%)

### Capital Deployment
- `CAPITAL_COMMITMENT_RATE_ESTIMATE` - Commitment rate (70%)

### Strategic Scoring
- `STRATEGIC_SCORE_STRONG_THRESHOLD` - Strong position (70)
- `STRATEGIC_SCORE_WEAK_THRESHOLD` - Weak position (50)
- `OWNERSHIP_SCORE_STRONG_THRESHOLD` - Strong retention (70)
- `OWNERSHIP_SCORE_WEAK_THRESHOLD` - Significant dilution (50)
- `CONTROL_SCORE_STRONG_THRESHOLD` - Strong control (70)
- `CONTROL_SCORE_WEAK_THRESHOLD` - Limited control (50)

---

## All Helper Functions

### `get_monetization_options(gross_credit_amount: Decimal) -> Dict[str, Decimal]`
Calculate all monetization options for a tax credit.

```python
options = business_rules.get_monetization_options(Decimal("5000000"))
# {"direct_receipt": 5000000, "bank_loan": 4250000, "broker_sale": 4000000}
```

### `get_scenario_templates(num_scenarios: int) -> List[str]`
Get the appropriate scenario templates.

```python
templates = business_rules.get_scenario_templates(3)
# ["debt_heavy", "equity_heavy", "balanced"]
```

### `estimate_tax_incentives(total_budget: Decimal) -> Decimal`
Estimate tax incentives from budget.

```python
tax = business_rules.estimate_tax_incentives(Decimal("30000000"))
# Decimal("6000000")  # 20% of budget
```

### `estimate_committed_capital(total_budget: Decimal) -> Decimal`
Estimate committed capital from budget.

```python
committed = business_rules.estimate_committed_capital(Decimal("30000000"))
# Decimal("21000000")  # 70% of budget
```

---

## Demo Script

Run the demo to see all business rules in action:

```bash
cd backend/api
python -m app.core.business_rules_demo
```

This displays:
- Tax credit monetization options
- Scenario template selection
- Performance evaluation thresholds
- Project estimates
- S-curve defaults
- Cash flow distribution

---

## Why Use This?

### Before (❌ Problems)
```python
# Scattered magic numbers
revenue = budget * Decimal("2.5")  # What does 2.5 mean?
tax = budget * 0.20  # Why 20%?
bank_loan = credit * Decimal("0.85")  # Is this consistent everywhere?

# Inconsistent assumptions
# File A uses 0.85, File B uses 0.86, File C uses 0.85 again
```

### After (✅ Benefits)
```python
# Clear, documented, consistent
from app.core import business_rules

revenue = budget * business_rules.REVENUE_MULTIPLIER_DEFAULT
tax = business_rules.estimate_tax_incentives(budget)
options = business_rules.get_monetization_options(credit)

# All files use same values from single source
```

---

## When to Update

Update business rules when:

1. **Business assumptions change**
   - Market conditions shift (e.g., bank loan rates change from 15% to 12%)
   - Industry standards evolve (e.g., distribution fees drop from 30% to 25%)

2. **Policy updates**
   - New tax incentive capture benchmarks
   - Updated financial performance thresholds

3. **Client customization**
   - Different clients may have different risk tolerance
   - Regional variations in financial metrics

4. **Model improvements**
   - Better data on revenue multiples
   - More accurate S-curve parameters

**How to update:**
1. Modify constant in `business_rules.py`
2. Update comment explaining rationale
3. Run full test suite to validate
4. Changes automatically propagate to all endpoints

---

## Migration Checklist

When refactoring an endpoint to use business rules:

- [ ] Identify all hardcoded numbers and percentages
- [ ] Check if constant exists in `business_rules.py`
- [ ] If not, add it with documentation
- [ ] Replace hardcoded value with constant
- [ ] Add import: `from app.core import business_rules`
- [ ] Run tests to verify no regressions
- [ ] Update comments to reference business rule

---

## Questions?

See:
- **Full documentation:** `backend/BUSINESS_RULES_REFACTORING.md`
- **Module source:** `backend/api/app/core/business_rules.py`
- **Demo script:** `backend/api/app/core/business_rules_demo.py`
- **Example integration:** `backend/api/app/api/v1/endpoints/incentives.py`
