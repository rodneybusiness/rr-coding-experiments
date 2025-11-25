# Endpoint Code Summary

## New API Endpoints - Code Reference

This document provides a quick reference to the three new optimizer endpoints added to the Film Financing Navigator API.

---

## 1. Validate Constraints Endpoint

**Location:** `/home/user/rr-coding-experiments/active-projects/Independent Animated Film Financing Model v1/backend/api/app/api/v1/endpoints/scenarios.py`

**Route:** `POST /api/v1/scenarios/validate-constraints`

**Key Components:**
- Converts `CapitalStructure` (API schema) to `CapitalStack` (engine model)
- Uses `ConstraintManager` from `engines/scenario_optimizer/constraint_manager.py`
- Applies default hard and soft constraints
- Returns validation results with violations and penalties

**Implementation Highlights:**
```python
# Initialize constraint manager with default constraints
manager = ConstraintManager()

# Validate capital stack
validation = manager.validate(capital_stack)

# Convert violations to API output format
hard_violations = [
    ConstraintViolationOutput(
        constraint_id=v.constraint.constraint_id,
        constraint_type=v.constraint.constraint_type.value,
        description=v.constraint.description,
        severity=v.severity,
        details=v.details
    )
    for v in validation.hard_violations
]
```

**Response Schema:** `ValidateConstraintsResponse`
- `is_valid`: bool
- `hard_violations`: List[ConstraintViolationOutput]
- `soft_violations`: List[ConstraintViolationOutput]
- `total_penalty`: Decimal
- `summary`: str

---

## 2. Optimize Capital Stack Endpoint

**Location:** `/home/user/rr-coding-experiments/active-projects/Independent Animated Film Financing Model v1/backend/api/app/api/v1/endpoints/scenarios.py`

**Route:** `POST /api/v1/scenarios/optimize-capital-stack`

**Key Components:**
- Uses `CapitalStackOptimizer` from `engines/scenario_optimizer/capital_stack_optimizer.py`
- Supports single-start or multi-start (convergence) optimization
- Uses scipy.optimize SLSQP method
- Converts objective weights and bounds to optimizer format

**Implementation Highlights:**
```python
# Initialize optimizer
constraint_manager = ConstraintManager()
optimizer = CapitalStackOptimizer(constraint_manager=constraint_manager)

# Convert objective weights to dict
objective_weights = {
    "equity_irr": request.objective_weights.equity_irr / Decimal("100"),
    "cost_of_capital": request.objective_weights.cost_of_capital / Decimal("100"),
    "tax_incentives": request.objective_weights.tax_incentive_capture / Decimal("100"),
    "risk": request.objective_weights.risk_minimization / Decimal("100"),
}

# Run optimization (single or convergence mode)
if request.use_convergence:
    result = optimizer.optimize_with_convergence(
        template_stack=template_stack,
        project_budget=request.project_budget,
        objective_weights=objective_weights,
        bounds=bounds_dict,
        num_starts=3
    )
else:
    result = optimizer.optimize(
        template_stack=template_stack,
        project_budget=request.project_budget,
        objective_weights=objective_weights,
        bounds=bounds_dict
    )
```

**Request Schema:** `OptimizeCapitalStackRequest`
- `project_budget`: Decimal
- `template_structure`: CapitalStructure
- `objective_weights`: ObjectiveWeights
- `bounds`: Optional[OptimizationBounds]
- `use_convergence`: bool

**Response Schema:** `OptimizeCapitalStackResponse`
- `objective_value`: Decimal
- `optimized_structure`: CapitalStructure
- `solver_status`: str
- `solve_time_seconds`: float
- `allocations`: Dict[str, Decimal]
- `num_iterations`: int
- `num_evaluations`: int
- `convergence_info`: Optional[Dict[str, float]]

---

## 3. Analyze Tradeoffs Endpoint

**Location:** `/home/user/rr-coding-experiments/active-projects/Independent Animated Film Financing Model v1/backend/api/app/api/v1/endpoints/scenarios.py`

**Route:** `POST /api/v1/scenarios/analyze-tradeoffs`

**Key Components:**
- Uses `TradeOffAnalyzer` from `engines/scenario_optimizer/tradeoff_analyzer.py`
- Converts input scenarios to `ScenarioEvaluation` objects
- Identifies Pareto-optimal scenarios
- Calculates trade-off slopes and generates insights

**Implementation Highlights:**
```python
# Convert scenarios to ScenarioEvaluation objects
evaluations = []
for scenario in request.scenarios:
    evaluation = ScenarioEvaluation(
        scenario_name=scenario.scenario_name,
        capital_stack=None
    )

    # Set metrics from input
    evaluation.equity_irr = scenario.metrics.equity_irr
    evaluation.weighted_cost_of_capital = scenario.metrics.cost_of_capital
    evaluation.tax_incentive_effective_rate = scenario.metrics.tax_incentive_rate
    evaluation.risk_score = scenario.metrics.risk_score
    evaluation.debt_coverage_ratio = scenario.metrics.debt_coverage_ratio
    evaluation.probability_of_equity_recoupment = scenario.metrics.probability_of_recoupment

    evaluations.append(evaluation)

# Initialize analyzer
analyzer = TradeOffAnalyzer()

# Run analysis
analysis = analyzer.analyze(
    evaluations=evaluations,
    objective_pairs=objective_pairs
)
```

**Request Schema:** `AnalyzeTradeoffsRequest`
- `scenarios`: List[ScenarioForTradeoff] (min 2)
- `objective_pairs`: Optional[List[List[str]]]

**Response Schema:** `AnalyzeTradeoffsResponse`
- `pareto_frontiers`: List[ParetoFrontierOutput]
  - `frontier_points`: List[ParetoPoint]
  - `dominated_points`: List[ParetoPoint]
  - `trade_off_slope`: Optional[Decimal]
  - `insights`: List[str]
- `recommended_scenarios`: Dict[str, str]
- `trade_off_summary`: str

---

## Schema Additions

**Location:** `/home/user/rr-coding-experiments/active-projects/Independent Animated Film Financing Model v1/backend/api/app/schemas/scenarios.py`

### New Request Schemas

1. **ValidateConstraintsRequest**
   - `project_budget`: Decimal
   - `capital_structure`: CapitalStructure
   - `constraints`: List[ConstraintInput]

2. **OptimizeCapitalStackRequest**
   - `project_budget`: Decimal
   - `template_structure`: CapitalStructure
   - `objective_weights`: ObjectiveWeights
   - `bounds`: Optional[OptimizationBounds]
   - `constraints`: List[ConstraintInput]
   - `use_convergence`: bool

3. **AnalyzeTradeoffsRequest**
   - `scenarios`: List[ScenarioForTradeoff]
   - `objective_pairs`: Optional[List[List[str]]]

### New Response Schemas

1. **ValidateConstraintsResponse**
   - `is_valid`: bool
   - `hard_violations`: List[ConstraintViolationOutput]
   - `soft_violations`: List[ConstraintViolationOutput]
   - `total_penalty`: Decimal
   - `summary`: str

2. **OptimizeCapitalStackResponse**
   - `objective_value`: Decimal
   - `optimized_structure`: CapitalStructure
   - `solver_status`: str
   - `solve_time_seconds`: float
   - `allocations`: Dict[str, Decimal]
   - `num_iterations`: int
   - `num_evaluations`: int
   - `convergence_info`: Optional[Dict[str, float]]

3. **AnalyzeTradeoffsResponse**
   - `pareto_frontiers`: List[ParetoFrontierOutput]
   - `recommended_scenarios`: Dict[str, str]
   - `trade_off_summary`: str

### Supporting Schemas

- `ConstraintInput` - Constraint definition
- `ConstraintViolationOutput` - Violation details
- `OptimizationBounds` - Min/max bounds per instrument
- `ScenarioForTradeoff` - Scenario with metrics
- `ParetoPoint` - Point on Pareto frontier
- `ParetoFrontierOutput` - Complete frontier analysis

---

## Import Fixes Applied

### File: `constraint_manager.py`

**Before:**
```python
from backend.models.financial_instruments import TaxIncentive
```

**After:**
```python
from models.financial_instruments import TaxIncentive
```

### File: `capital_stack_optimizer.py`

**Before:**
```python
from backend.engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluation
```

**After:**
```python
from engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluation
```

**Reason:** Fixed module import paths to work correctly when API runs from `backend/api` directory.

---

## Helper Functions

### `_extract_capital_structure(capital_stack: CapitalStack) -> CapitalStructure`

Converts engine `CapitalStack` model to API `CapitalStructure` schema:

```python
def _extract_capital_structure(capital_stack: CapitalStack) -> CapitalStructure:
    """Extract CapitalStructure from CapitalStack."""
    senior_debt = Decimal("0")
    gap_financing = Decimal("0")
    mezzanine_debt = Decimal("0")
    equity = Decimal("0")
    tax_incentives = Decimal("0")
    presales = Decimal("0")
    grants = Decimal("0")

    for component in capital_stack.components:
        inst = component.instrument
        if isinstance(inst, SeniorDebt):
            senior_debt += inst.amount
        elif isinstance(inst, GapFinancing):
            gap_financing += inst.amount
        # ... (similar for other instrument types)

    return CapitalStructure(
        senior_debt=senior_debt,
        gap_financing=gap_financing,
        mezzanine_debt=mezzanine_debt,
        equity=equity,
        tax_incentives=tax_incentives,
        presales=presales,
        grants=grants,
    )
```

**Purpose:** Aggregates instrument amounts by type for API response.

---

## Validation Results

### API Load Test
```bash
cd backend && python -c "from api.app.main import app; print('API loaded successfully')"
```
**Result:** ✅ API loaded successfully

### Route Registration Test
```
Total scenario endpoints: 5
  POST /api/v1/scenarios/generate
  POST /api/v1/scenarios/compare
  POST /api/v1/scenarios/validate-constraints
  POST /api/v1/scenarios/optimize-capital-stack
  POST /api/v1/scenarios/analyze-tradeoffs

New optimizer endpoints: 3/3 ✓
```

### Integration Test Results
```
1. POST /api/v1/scenarios/validate-constraints
   Status: 200 ✓
   Valid: True
   Hard Violations: 0
   Soft Violations: 0

2. POST /api/v1/scenarios/optimize-capital-stack
   Status: 200 ✓
   Objective Value: 72.5
   Solver Status: SUCCESS
   Solve Time: 0.00s

3. POST /api/v1/scenarios/analyze-tradeoffs
   Status: 200 ✓
   Pareto Frontiers: 2
   Recommended Scenarios: 5
```

---

## Engine Integration

### Constraint Manager (Engine 3.1)

**File:** `engines/scenario_optimizer/constraint_manager.py`

**Default Constraints:**

**Hard Constraints:**
1. `min_equity_15pct` - Minimum 15% equity financing
2. `max_debt_ratio_75pct` - Maximum 75% debt ratio
3. `budget_sum_matches` - Component amounts must sum to budget (±1%)

**Soft Constraints:**
1. `target_irr_20pct` - Target 20% IRR (weight: 0.8)
2. `minimize_dilution` - Producer retains >50% ownership (weight: 0.7)
3. `maximize_incentives` - >15% from tax incentives (weight: 0.6)
4. `balanced_risk` - Debt ≤60%, equity ≤70% (weight: 0.5)

**Usage in endpoint:**
```python
manager = ConstraintManager()  # Auto-loads defaults
validation = manager.validate(capital_stack)
```

### Capital Stack Optimizer (Engine 3.2)

**File:** `engines/scenario_optimizer/capital_stack_optimizer.py`

**Optimization Method:** Sequential Least Squares Programming (SLSQP)

**Constraints:**
- Linear equality: Sum of allocations = 100%
- Box bounds: Min/max percentage per instrument
- Hard constraints: From ConstraintManager

**Objective Function:**
- Weighted composite of 5 components:
  1. Equity IRR (normalized to 20% target)
  2. Tax incentives (normalized to 20% target)
  3. Risk (recoupment probability, target 80%)
  4. Cost of capital (WACC, target 12%)
  5. Debt recovery (target 100%)

**Usage in endpoint:**
```python
optimizer = CapitalStackOptimizer(constraint_manager=ConstraintManager())

# Single-start optimization
result = optimizer.optimize(template_stack, budget, objective_weights, bounds)

# Multi-start for convergence
result = optimizer.optimize_with_convergence(
    template_stack, budget, objective_weights, bounds, num_starts=3
)
```

### Tradeoff Analyzer (Engine 3.3)

**File:** `engines/scenario_optimizer/tradeoff_analyzer.py`

**Algorithm:** Pareto dominance analysis

**Default Objective Pairs:**
1. `equity_irr` vs `probability_of_recoupment` (Returns vs. Risk)
2. `equity_irr` vs `cost_of_capital` (Returns vs. Cost)
3. `tax_incentive_effective_rate` vs `equity_irr` (Incentives vs. Returns)
4. `tax_incentive_effective_rate` vs `weighted_cost_of_capital` (Incentives vs. Cost)
5. `senior_debt_recovery_rate` vs `equity_irr` (Debt safety vs. Equity)

**Pareto Optimality:**
- Scenario A dominates B if A is better on all objectives
- Pareto-optimal scenarios are non-dominated
- Forms the Pareto frontier

**Trade-off Slope:**
- Average ΔObj1 / ΔObj2 along frontier
- Indicates marginal rate of substitution

**Usage in endpoint:**
```python
analyzer = TradeOffAnalyzer()
analysis = analyzer.analyze(evaluations, objective_pairs)

# Access results
for frontier in analysis.pareto_frontiers:
    print(f"Frontier: {frontier.objective_1_name} vs {frontier.objective_2_name}")
    print(f"Optimal scenarios: {len(frontier.frontier_points)}")
    print(f"Trade-off slope: {frontier.trade_off_slope}")
```

---

## Testing Files

### 1. Route Registration Test

**File:** `test_new_endpoints.py`

**Purpose:** Verify endpoints are registered with FastAPI

**Output:**
```
Checking registered routes for /api/v1/scenarios
  POST            /api/v1/scenarios/analyze-tradeoffs
  POST            /api/v1/scenarios/compare
  POST            /api/v1/scenarios/generate
  POST            /api/v1/scenarios/optimize-capital-stack
  POST            /api/v1/scenarios/validate-constraints

New Optimizer Endpoints Check
  ✓ /api/v1/scenarios/validate-constraints
  ✓ /api/v1/scenarios/optimize-capital-stack
  ✓ /api/v1/scenarios/analyze-tradeoffs

Total scenario endpoints: 5
New optimizer endpoints: 3/3
```

### 2. Integration Test

**File:** `test_optimizer_endpoints.py`

**Purpose:** Test endpoints with realistic data

**Tests:**
1. Validate constraints with $30M balanced structure
2. Optimize capital stack with convergence mode
3. Analyze tradeoffs between 3 scenarios

**Results:** All tests passing ✅

---

## Summary

### Files Modified
1. `api/app/schemas/scenarios.py` - Added 12 new schemas
2. `api/app/api/v1/endpoints/scenarios.py` - Added 3 new endpoints
3. `engines/scenario_optimizer/constraint_manager.py` - Fixed import
4. `engines/scenario_optimizer/capital_stack_optimizer.py` - Fixed import

### Lines of Code Added
- Schemas: ~260 lines
- Endpoints: ~470 lines
- Total: ~730 lines

### API Routes Added
- `/api/v1/scenarios/validate-constraints` (POST)
- `/api/v1/scenarios/optimize-capital-stack` (POST)
- `/api/v1/scenarios/analyze-tradeoffs` (POST)

### Status
✅ All endpoints functional and tested
✅ API loads without errors
✅ Integration with existing scenario endpoints
✅ Comprehensive documentation provided

---

## Next Steps

1. **Frontend Integration:**
   - Create TypeScript interfaces for new schemas
   - Add API client methods
   - Build UI components for constraint validation, optimization, and trade-off visualization

2. **Testing:**
   - Add unit tests for endpoint functions
   - Add edge case tests (empty scenarios, infeasible constraints)
   - Performance testing with large scenario sets

3. **Documentation:**
   - Add examples to Swagger UI
   - Create video tutorials
   - Update user guide

4. **Enhancements:**
   - Custom constraint builder UI
   - Real-time optimization progress
   - Interactive Pareto frontier charts
   - Batch optimization API
