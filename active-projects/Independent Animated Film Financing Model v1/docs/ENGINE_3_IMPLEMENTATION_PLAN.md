# Engine 3: Scenario Generator & Optimizer - Implementation Plan

**Version:** 1.0
**Date:** 2025-10-31
**Status:** Planning Complete → Ready for Implementation

---

## Executive Summary

Engine 3 is the **"Pathway Architect"** - an intelligent system that automatically generates and optimizes financing scenarios for animation projects. It takes a project profile and constraints as input, generates multiple diverse financing strategies, optimizes each using OR-Tools, evaluates them using Engines 1 & 2, and presents ranked scenarios with comprehensive trade-off analysis.

**Why Engine 3?**
- Producers need to explore financing options but lack expertise to structure deals optimally
- The solution space is enormous (combinations of debt, equity, pre-sales, incentives, etc.)
- Stakeholders have competing priorities (creative control, financial return, risk mitigation)
- Manual scenario creation is time-consuming and misses opportunities
- Optimization can find non-obvious solutions that satisfy multiple constraints

**Key Capabilities:**
1. **Intelligent Scenario Generation** - Creates 5-10 diverse financing structures automatically
2. **Multi-Objective Optimization** - Uses OR-Tools to optimize capital stacks balancing priorities
3. **Comprehensive Evaluation** - Integrates Engine 1 (incentives) and Engine 2 (waterfall/IRR)
4. **Scenario Comparison** - Compares scenarios across 15+ dimensions
5. **Trade-off Analysis** - Identifies Pareto-optimal solutions and explains trade-offs
6. **Stakeholder Prioritization** - Weights objectives based on stakeholder preferences

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│           Engine 3: Scenario Generator & Optimizer                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────┐         ┌──────────────────────────────┐  │
│  │ ScenarioGenerator  │────────▶│  FinancingTemplate           │  │
│  │ - generate()       │         │  (debt_heavy, equity_heavy,  │  │
│  │ - templates        │         │   balanced, pre_sale_focused)│  │
│  │ - diversify()      │         └──────────────────────────────┘  │
│  └────────────────────┘                      │                     │
│           │                                   │                     │
│           ▼                                   ▼                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │           ConstraintManager                                 │   │
│  │  - validate_constraints()                                   │   │
│  │  - hard_constraints: min_equity, max_debt_ratio            │   │
│  │  - soft_constraints: target_IRR, creative_control          │   │
│  └────────────────────────────────────────────────────────────┘   │
│           │                                                         │
│           ▼                                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │     CapitalStackOptimizer (OR-Tools)                        │   │
│  │  - optimize_stack()                                         │   │
│  │  - objective: weighted_score()                              │   │
│  │  - variables: debt_amount, equity_amount, etc.              │   │
│  │  - constraints: budget, ratios, minimums                    │   │
│  └────────────────────────────────────────────────────────────┘   │
│           │                                                         │
│           ▼                                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │          ScenarioEvaluator                                  │   │
│  │  - evaluate()                                               │   │
│  │  - Uses Engine 1: calculate incentives                      │   │
│  │  - Uses Engine 2: project waterfall, calculate IRR/NPV      │   │
│  │  - Calculates: total_score, risk_score, feasibility        │   │
│  └────────────────────────────────────────────────────────────┘   │
│           │                                                         │
│           ▼                                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │          ScenarioComparator                                 │   │
│  │  - compare_scenarios()                                      │   │
│  │  - rank_scenarios()                                         │   │
│  │  - generate_comparison_matrix()                             │   │
│  └────────────────────────────────────────────────────────────┘   │
│           │                                                         │
│           ▼                                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │         TradeOffAnalyzer                                    │   │
│  │  - identify_pareto_frontier()                               │   │
│  │  - explain_tradeoffs()                                      │   │
│  │  - recommend_scenario()                                     │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         │                              │                    │
         ▼                              ▼                    ▼
   ┌──────────┐                  ┌──────────┐        ┌──────────┐
   │ Engine 1 │                  │ Engine 2 │        │ Phase 2A │
   │(Incentive│                  │(Waterfall│        │  Models  │
   │Calculator│                  │IRR/NPV)  │        └──────────┘
   └──────────┘                  └──────────┘
```

---

## Component 1: ScenarioGenerator

**Purpose:** Generate diverse financing scenarios using templates and randomization strategies.

**File:** `backend/engines/scenario_optimizer/scenario_generator.py`

### Key Classes

```python
@dataclass
class FinancingTemplate:
    """
    Template for a financing strategy.

    Attributes:
        template_name: Name (e.g., "Debt-Heavy", "Equity-Heavy")
        debt_percentage: Target % of budget from debt (0-100)
        equity_percentage: Target % of budget from equity (0-100)
        presale_percentage: Target % from pre-sales/MGs
        incentive_percentage: Target % from tax incentives
        description: Human-readable description
        typical_use_case: When this template is appropriate
    """
    template_name: str
    debt_percentage: Decimal
    equity_percentage: Decimal
    presale_percentage: Decimal
    incentive_percentage: Decimal
    description: str
    typical_use_case: str


@dataclass
class ScenarioConfig:
    """
    Configuration for generating a scenario.

    Attributes:
        project_profile: ProjectProfile from Phase 2A
        template: FinancingTemplate to use
        constraints: FinancingConstraints
        randomization_factor: How much to randomize (0.0-1.0)
    """
    project_profile: 'ProjectProfile'
    template: FinancingTemplate
    constraints: 'FinancingConstraints'
    randomization_factor: Decimal = Decimal("0.1")


class ScenarioGenerator:
    """
    Generate diverse financing scenarios.

    Creates multiple capital stack scenarios using templates and
    intelligent diversification strategies.
    """

    def __init__(self):
        """Initialize with default templates"""
        self.templates = self._load_default_templates()

    def generate(
        self,
        project_profile: 'ProjectProfile',
        constraints: 'FinancingConstraints',
        num_scenarios: int = 5
    ) -> List['CapitalStack']:
        """
        Generate multiple diverse financing scenarios.

        Args:
            project_profile: Project to finance
            constraints: Financing constraints
            num_scenarios: Number of scenarios to generate (3-10)

        Logic:
        1. Select diverse templates (debt-heavy, equity-heavy, balanced, etc.)
        2. For each template:
           a. Calculate target amounts for each instrument type
           b. Select specific instruments (senior debt, equity, pre-sales, etc.)
           c. Apply randomization for diversity
           d. Validate against constraints
        3. Add one "optimal" scenario using optimizer
        4. Return list of capital stacks

        Returns:
            List of CapitalStack objects
        """

    def _load_default_templates(self) -> List[FinancingTemplate]:
        """
        Load default financing templates.

        Returns:
            List of templates covering common strategies
        """
        # Templates defined below

    def _create_capital_stack_from_template(
        self,
        project_profile: 'ProjectProfile',
        template: FinancingTemplate,
        constraints: 'FinancingConstraints'
    ) -> 'CapitalStack':
        """
        Create a capital stack from a template.

        Args:
            project_profile: Project details
            template: Template to use
            constraints: Constraints to satisfy

        Returns:
            CapitalStack instance
        """

    def _select_debt_instruments(
        self,
        total_debt: Decimal,
        constraints: 'FinancingConstraints'
    ) -> List['FinancialInstrument']:
        """
        Select and configure debt instruments.

        Typically includes:
        - Senior debt (60-70% of total debt)
        - Gap debt (20-30%)
        - Mezzanine (0-10% if needed)

        Args:
            total_debt: Total debt amount needed
            constraints: Financing constraints

        Returns:
            List of configured debt instruments
        """

    def _select_equity_instruments(
        self,
        total_equity: Decimal,
        constraints: 'FinancingConstraints'
    ) -> List['FinancialInstrument']:
        """
        Select and configure equity instruments.

        Args:
            total_equity: Total equity amount needed
            constraints: Constraints

        Returns:
            List of equity instruments
        """
```

### Default Financing Templates

```python
DEFAULT_TEMPLATES = [
    FinancingTemplate(
        template_name="Debt-Heavy (Bank Financing)",
        debt_percentage=Decimal("70.0"),
        equity_percentage=Decimal("20.0"),
        presale_percentage=Decimal("5.0"),
        incentive_percentage=Decimal("5.0"),
        description="Maximum leverage with senior and gap debt",
        typical_use_case="Established producers with strong pre-sales"
    ),

    FinancingTemplate(
        template_name="Equity-Heavy (Independent)",
        debt_percentage=Decimal("20.0"),
        equity_percentage=Decimal("60.0"),
        presale_percentage=Decimal("10.0"),
        incentive_percentage=Decimal("10.0"),
        description="Minimal debt, relying on equity investors",
        typical_use_case="First-time producers or risky projects"
    ),

    FinancingTemplate(
        template_name="Balanced (Hybrid)",
        debt_percentage=Decimal("45.0"),
        equity_percentage=Decimal("35.0"),
        presale_percentage=Decimal("10.0"),
        incentive_percentage=Decimal("10.0"),
        description="Balanced mix of debt and equity",
        typical_use_case="Moderate-budget projects with proven talent"
    ),

    FinancingTemplate(
        template_name="Pre-Sale Focused (Distributor-Backed)",
        debt_percentage=Decimal("30.0"),
        equity_percentage=Decimal("25.0"),
        presale_percentage=Decimal("35.0"),
        incentive_percentage=Decimal("10.0"),
        description="Heavy pre-sales and MGs from distributors",
        typical_use_case="Strong IP with international appeal"
    ),

    FinancingTemplate(
        template_name="Incentive-Maximized (Soft Money)",
        debt_percentage=Decimal("35.0"),
        equity_percentage=Decimal("30.0"),
        presale_percentage=Decimal("10.0"),
        incentive_percentage=Decimal("25.0"),
        description="Maximizes tax incentives via multi-jurisdiction",
        typical_use_case="Animation with flexible production locations"
    ),
]
```

---

## Component 2: ConstraintManager

**Purpose:** Manage and validate financing constraints (hard and soft).

**File:** `backend/engines/scenario_optimizer/constraint_manager.py`

### Key Classes

```python
@dataclass
class FinancingConstraints:
    """
    Financing constraints for scenario generation.

    Hard Constraints (must be satisfied):
        min_equity_percentage: Minimum equity % (e.g., 20%)
        max_debt_ratio: Maximum debt-to-equity ratio (e.g., 3:1)
        max_single_investor_percentage: Max ownership by one investor (e.g., 49%)
        required_creative_control: Must retain creative approval rights

    Soft Constraints (preferences, weighted):
        target_equity_irr: Desired equity IRR (e.g., 20%)
        target_debt_recovery: Desired debt recovery rate (e.g., 100%)
        minimize_dilution: Preference to minimize equity dilution
        maximize_tax_incentives: Preference to maximize incentive benefits
    """
    # Hard constraints
    min_equity_percentage: Decimal = Decimal("15.0")
    max_debt_ratio: Decimal = Decimal("3.0")  # 3:1
    max_single_investor_percentage: Decimal = Decimal("49.0")
    required_creative_control: bool = True

    # Soft constraints (preferences)
    target_equity_irr: Optional[Decimal] = Decimal("20.0")
    target_debt_recovery_rate: Optional[Decimal] = Decimal("100.0")
    minimize_dilution: bool = True
    maximize_tax_incentives: bool = True

    # Stakeholder priority weights
    creative_control_weight: Decimal = Decimal("0.3")
    financial_return_weight: Decimal = Decimal("0.5")
    risk_mitigation_weight: Decimal = Decimal("0.2")


class ConstraintManager:
    """
    Manage and validate financing constraints.

    Handles both hard constraints (must satisfy) and soft constraints
    (preferences that are weighted in optimization).
    """

    def __init__(self, constraints: FinancingConstraints):
        """
        Initialize with constraints.

        Args:
            constraints: FinancingConstraints instance
        """
        self.constraints = constraints

    def validate_hard_constraints(
        self,
        capital_stack: 'CapitalStack'
    ) -> tuple[bool, List[str]]:
        """
        Validate hard constraints.

        Args:
            capital_stack: CapitalStack to validate

        Returns:
            (is_valid, list_of_violations)
        """
        violations = []

        # Check minimum equity
        equity_pct = (capital_stack.total_equity() / capital_stack.project_budget) * Decimal("100")
        if equity_pct < self.constraints.min_equity_percentage:
            violations.append(
                f"Equity {equity_pct:.1f}% below minimum {self.constraints.min_equity_percentage}%"
            )

        # Check debt-to-equity ratio
        if capital_stack.total_equity() > 0:
            debt_ratio = capital_stack.debt_to_equity_ratio()
            if debt_ratio > self.constraints.max_debt_ratio:
                violations.append(
                    f"Debt-to-equity ratio {debt_ratio:.2f}:1 exceeds max {self.constraints.max_debt_ratio}:1"
                )

        # Check single investor concentration
        # (would need ownership tracking in capital stack)

        is_valid = len(violations) == 0
        return (is_valid, violations)

    def calculate_soft_score(
        self,
        capital_stack: 'CapitalStack',
        scenario_evaluation: 'ScenarioEvaluation'
    ) -> Decimal:
        """
        Calculate soft constraint satisfaction score (0-100).

        Args:
            capital_stack: CapitalStack instance
            scenario_evaluation: Evaluation results from ScenarioEvaluator

        Returns:
            Score from 0-100 (higher is better)
        """
        score = Decimal("0")

        # IRR score
        if self.constraints.target_equity_irr and scenario_evaluation.equity_irr:
            irr_ratio = min(scenario_evaluation.equity_irr / self.constraints.target_equity_irr, Decimal("1.5"))
            irr_score = irr_ratio * Decimal("100") / Decimal("1.5")
            score += irr_score * Decimal("0.4")  # 40% weight

        # Debt recovery score
        if self.constraints.target_debt_recovery_rate and scenario_evaluation.debt_recovery_rate:
            recovery_score = (scenario_evaluation.debt_recovery_rate / Decimal("100")) * Decimal("100")
            score += recovery_score * Decimal("0.3")  # 30% weight

        # Incentive maximization score
        if self.constraints.maximize_tax_incentives:
            incentive_pct = (scenario_evaluation.total_incentive_benefit / capital_stack.project_budget) * Decimal("100")
            incentive_score = min(incentive_pct / Decimal("30"), Decimal("1.0")) * Decimal("100")
            score += incentive_score * Decimal("0.3")  # 30% weight

        return score
```

---

## Component 3: CapitalStackOptimizer

**Purpose:** Use OR-Tools to optimize capital stacks for maximum weighted score.

**File:** `backend/engines/scenario_optimizer/capital_stack_optimizer.py`

### Key Classes

```python
class CapitalStackOptimizer:
    """
    Optimize capital stack using OR-Tools.

    Uses Google OR-Tools' CP-SAT solver to find optimal capital stack
    configurations that maximize a weighted objective function while
    satisfying hard constraints.
    """

    def __init__(self, constraints: FinancingConstraints):
        """
        Initialize optimizer.

        Args:
            constraints: FinancingConstraints
        """
        self.constraints = constraints

    def optimize(
        self,
        project_budget: Decimal,
        available_instruments: Dict[str, 'FinancialInstrument'],
        objective_weights: Dict[str, Decimal]
    ) -> 'CapitalStack':
        """
        Optimize capital stack.

        Args:
            project_budget: Total budget to raise
            available_instruments: Dict of instrument_id → instrument configuration
            objective_weights: Weights for objective function components

        Returns:
            Optimized CapitalStack

        Logic:
        1. Create OR-Tools CP-SAT model
        2. Define decision variables:
           - use_instrument[i]: binary (0 or 1)
           - instrument_amount[i]: integer (in $100k units for tractability)
        3. Add constraints:
           - Sum of amounts = project_budget
           - Min equity percentage
           - Max debt-to-equity ratio
           - Individual instrument limits
        4. Define objective function:
           - Maximize: weighted_score = Σ (weight[i] * score[i])
           - Components: IRR potential, risk score, flexibility
        5. Solve and return optimized stack
        """
        from ortools.sat.python import cp_model

        model = cp_model.CpModel()

        # Decision variables
        instrument_ids = list(available_instruments.keys())
        use_instrument = {}
        instrument_amount = {}

        for inst_id in instrument_ids:
            use_instrument[inst_id] = model.NewBoolVar(f'use_{inst_id}')
            # Amount in $100k units (for integer programming)
            max_amount_units = int(project_budget / Decimal("100000"))
            instrument_amount[inst_id] = model.NewIntVar(0, max_amount_units, f'amount_{inst_id}')

        # Constraint: total = budget
        budget_units = int(project_budget / Decimal("100000"))
        model.Add(sum(instrument_amount.values()) == budget_units)

        # Constraint: if not used, amount = 0
        for inst_id in instrument_ids:
            model.Add(instrument_amount[inst_id] <= max_amount_units * use_instrument[inst_id])

        # Constraint: min equity
        equity_instruments = [
            inst_id for inst_id, inst in available_instruments.items()
            if inst.instrument_type.value == "equity"
        ]
        min_equity_units = int((project_budget * self.constraints.min_equity_percentage / Decimal("100")) / Decimal("100000"))
        if equity_instruments:
            model.Add(sum(instrument_amount[eq_id] for eq_id in equity_instruments) >= min_equity_units)

        # Objective: maximize weighted score
        # (Simplified - in production would use more sophisticated scoring)
        objective_terms = []
        for inst_id in instrument_ids:
            # Score based on instrument attractiveness
            inst = available_instruments[inst_id]
            score = self._calculate_instrument_score(inst, objective_weights)
            objective_terms.append(int(score * 100) * instrument_amount[inst_id])

        model.Maximize(sum(objective_terms))

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            selected_instruments = []
            for inst_id in instrument_ids:
                if solver.Value(use_instrument[inst_id]) == 1:
                    amount = Decimal(str(solver.Value(instrument_amount[inst_id]))) * Decimal("100000")
                    inst = available_instruments[inst_id]
                    # Clone instrument with optimized amount
                    optimized_inst = self._clone_instrument_with_amount(inst, amount)
                    selected_instruments.append(optimized_inst)

            # Create capital stack
            components = [
                CapitalComponent(instrument=inst, position=i+1)
                for i, inst in enumerate(selected_instruments)
            ]

            capital_stack = CapitalStack(
                stack_name="Optimized Stack",
                project_budget=project_budget,
                components=components
            )

            return capital_stack

        else:
            raise ValueError("Optimization failed to find feasible solution")

    def _calculate_instrument_score(
        self,
        instrument: 'FinancialInstrument',
        weights: Dict[str, Decimal]
    ) -> Decimal:
        """
        Calculate attractiveness score for an instrument.

        Args:
            instrument: FinancialInstrument
            weights: Objective weights

        Returns:
            Score (0-1)
        """
        # Debt scores higher if minimizing dilution
        # Equity scores higher if maximizing flexibility
        # etc.
```

---

## Component 4: ScenarioEvaluator

**Purpose:** Evaluate scenarios using Engines 1 & 2, calculate comprehensive metrics.

**File:** `backend/engines/scenario_optimizer/scenario_evaluator.py`

### Key Classes

```python
@dataclass
class ScenarioEvaluation:
    """
    Complete evaluation of a financing scenario.

    Attributes:
        scenario_id: Unique identifier
        capital_stack: The capital stack being evaluated

        # From Engine 1 (Incentives)
        total_incentive_benefit: Total net incentive benefits
        incentive_by_jurisdiction: Dict of jurisdiction → benefit

        # From Engine 2 (Waterfall/IRR)
        equity_irr: Equity investor IRR
        equity_cash_on_cash: Equity cash-on-cash multiple
        equity_payback_years: Equity payback period
        debt_recovery_rate: Debt recovery rate (%)

        # Aggregate metrics
        total_score: Weighted score (0-100)
        risk_score: Risk score (0-100, higher = riskier)
        feasibility_score: Feasibility score (0-100)

        # Qualitative
        strengths: List of strengths
        weaknesses: List of weaknesses
    """
    scenario_id: str
    capital_stack: 'CapitalStack'

    total_incentive_benefit: Decimal
    incentive_by_jurisdiction: Dict[str, Decimal]

    equity_irr: Optional[Decimal]
    equity_cash_on_cash: Decimal
    equity_payback_years: Optional[Decimal]
    debt_recovery_rate: Decimal

    total_score: Decimal
    risk_score: Decimal
    feasibility_score: Decimal

    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


class ScenarioEvaluator:
    """
    Evaluate financing scenarios using Engines 1 & 2.

    Integrates with IncentiveCalculator (Engine 1) and WaterfallExecutor/
    StakeholderAnalyzer (Engine 2) to comprehensively evaluate scenarios.
    """

    def __init__(
        self,
        project_profile: 'ProjectProfile',
        revenue_projection: 'RevenueProjection',
        waterfall_structure: 'WaterfallStructure'
    ):
        """
        Initialize evaluator.

        Args:
            project_profile: ProjectProfile with jurisdiction info
            revenue_projection: Base revenue projection
            waterfall_structure: Waterfall structure template
        """
        self.project_profile = project_profile
        self.revenue_projection = revenue_projection
        self.waterfall_structure = waterfall_structure

    def evaluate(
        self,
        capital_stack: 'CapitalStack',
        scenario_id: str
    ) -> ScenarioEvaluation:
        """
        Evaluate a scenario.

        Args:
            capital_stack: Capital stack to evaluate
            scenario_id: Unique identifier

        Returns:
            ScenarioEvaluation with comprehensive metrics
        """
        # 1. Calculate incentives using Engine 1
        incentive_benefits = self._calculate_incentives(capital_stack)

        # 2. Execute waterfall and calculate returns using Engine 2
        returns = self._calculate_returns(capital_stack)

        # 3. Calculate aggregate scores
        total_score = self._calculate_total_score(incentive_benefits, returns)
        risk_score = self._calculate_risk_score(capital_stack, returns)
        feasibility_score = self._calculate_feasibility_score(capital_stack)

        # 4. Identify strengths and weaknesses
        strengths, weaknesses = self._analyze_qualitative(capital_stack, returns)

        evaluation = ScenarioEvaluation(
            scenario_id=scenario_id,
            capital_stack=capital_stack,
            total_incentive_benefit=incentive_benefits["total"],
            incentive_by_jurisdiction=incentive_benefits["by_jurisdiction"],
            equity_irr=returns.get("equity_irr"),
            equity_cash_on_cash=returns.get("equity_coc", Decimal("0")),
            equity_payback_years=returns.get("equity_payback"),
            debt_recovery_rate=returns.get("debt_recovery", Decimal("0")),
            total_score=total_score,
            risk_score=risk_score,
            feasibility_score=feasibility_score,
            strengths=strengths,
            weaknesses=weaknesses
        )

        return evaluation
```

---

## Component 5: ScenarioComparator

**Purpose:** Compare scenarios across multiple dimensions and rank them.

**File:** `backend/engines/scenario_optimizer/scenario_comparator.py`

### Key Classes

```python
@dataclass
class ComparisonDimension:
    """
    Single dimension for comparing scenarios.

    Attributes:
        dimension_name: Name (e.g., "Equity IRR", "Debt Load")
        metric_key: Key in evaluation (e.g., "equity_irr")
        weight: Importance weight (0-1)
        higher_is_better: True if higher values are better
    """
    dimension_name: str
    metric_key: str
    weight: Decimal
    higher_is_better: bool = True


class ScenarioComparator:
    """
    Compare and rank financing scenarios.

    Compares scenarios across 15+ dimensions and ranks them using
    weighted scoring.
    """

    def compare(
        self,
        evaluations: List[ScenarioEvaluation],
        dimensions: Optional[List[ComparisonDimension]] = None
    ) -> 'ComparisonResult':
        """
        Compare scenarios.

        Args:
            evaluations: List of scenario evaluations
            dimensions: Comparison dimensions (uses defaults if None)

        Returns:
            ComparisonResult with rankings
        """

    def rank_scenarios(
        self,
        evaluations: List[ScenarioEvaluation],
        stakeholder_priorities: Dict[str, Decimal]
    ) -> List[tuple[int, ScenarioEvaluation, Decimal]]:
        """
        Rank scenarios by weighted score.

        Args:
            evaluations: Scenario evaluations
            stakeholder_priorities: Weights for each priority

        Returns:
            List of (rank, evaluation, score) sorted by rank
        """
```

---

## Component 6: TradeOffAnalyzer

**Purpose:** Identify Pareto-optimal solutions and explain trade-offs.

**File:** `backend/engines/scenario_optimizer/tradeoff_analyzer.py`

### Key Classes

```python
class TradeOffAnalyzer:
    """
    Analyze trade-offs between scenarios.

    Identifies Pareto frontier and explains what you gain/lose
    when choosing one scenario over another.
    """

    def identify_pareto_frontier(
        self,
        evaluations: List[ScenarioEvaluation],
        objective1_key: str,
        objective2_key: str
    ) -> List[ScenarioEvaluation]:
        """
        Identify Pareto-optimal scenarios.

        A scenario is Pareto-optimal if no other scenario is better
        in both objectives simultaneously.

        Args:
            evaluations: Scenario evaluations
            objective1_key: First objective (e.g., "equity_irr")
            objective2_key: Second objective (e.g., "risk_score")

        Returns:
            List of Pareto-optimal scenarios
        """

    def explain_tradeoff(
        self,
        scenario_a: ScenarioEvaluation,
        scenario_b: ScenarioEvaluation
    ) -> Dict[str, Any]:
        """
        Explain trade-off between two scenarios.

        Args:
            scenario_a: First scenario
            scenario_b: Second scenario

        Returns:
            Dict with trade-off analysis:
            {
                "scenario_a_better_at": List[str],
                "scenario_b_better_at": List[str],
                "key_differences": List[str],
                "recommendation": str
            }
        """
```

---

## Integration with Engines 1 & 2

### Engine 1 Integration (Incentive Calculator)

```python
from backend.engines.incentive_calculator import (
    PolicyLoader,
    PolicyRegistry,
    IncentiveCalculator,
    JurisdictionSpend
)

# In ScenarioEvaluator._calculate_incentives()
loader = PolicyLoader(policies_dir)
registry = PolicyRegistry(loader)
calculator = IncentiveCalculator(registry)

# Calculate incentives for this capital stack's jurisdictions
result = calculator.calculate_multi_jurisdiction(
    total_budget=capital_stack.project_budget,
    jurisdiction_spends=jurisdiction_spends,
    monetization_preferences=monetization_prefs
)

total_benefit = result.total_net_benefits
```

### Engine 2 Integration (Waterfall/IRR)

```python
from backend.engines.waterfall_executor import (
    RevenueProjector,
    WaterfallExecutor,
    StakeholderAnalyzer
)

# In ScenarioEvaluator._calculate_returns()
executor = WaterfallExecutor(waterfall_structure)
waterfall_result = executor.execute_over_time(revenue_projection)

analyzer = StakeholderAnalyzer(capital_stack, discount_rate=Decimal("0.15"))
stakeholder_analysis = analyzer.analyze(waterfall_result)

equity_irr = stakeholder_analysis.stakeholders[equity_idx].irr
```

---

## Example Usage

```python
from backend.engines.scenario_optimizer import ScenarioOptimizer

# 1. Define project and constraints
project_profile = ProjectProfile(
    project_name="The Dragon's Quest",
    production_budget=Decimal("30000000"),
    # ... other fields
)

constraints = FinancingConstraints(
    min_equity_percentage=Decimal("20.0"),
    max_debt_ratio=Decimal("3.0"),
    target_equity_irr=Decimal("20.0"),
    creative_control_weight=Decimal("0.3"),
    financial_return_weight=Decimal("0.5"),
    risk_mitigation_weight=Decimal("0.2")
)

# 2. Create optimizer
optimizer = ScenarioOptimizer(
    project_profile=project_profile,
    constraints=constraints
)

# 3. Generate and evaluate scenarios
result = optimizer.generate_and_evaluate_scenarios(
    num_scenarios=5,
    revenue_projection=revenue_projection,
    waterfall_structure=waterfall_structure
)

# 4. Get ranked scenarios
for rank, scenario in enumerate(result.ranked_scenarios, 1):
    print(f"{rank}. {scenario.capital_stack.stack_name}")
    print(f"   Total Score: {scenario.total_score:.1f}/100")
    print(f"   Equity IRR: {scenario.equity_irr * 100:.1f}%")
    print(f"   Debt Recovery: {scenario.debt_recovery_rate:.1f}%")
    print(f"   Incentive Benefit: ${scenario.total_incentive_benefit:,.0f}")
    print()

# 5. Analyze trade-offs
pareto_scenarios = result.tradeoff_analysis.identify_pareto_frontier(
    result.evaluations,
    "equity_irr",
    "risk_score"
)

print(f"Pareto-optimal scenarios: {len(pareto_scenarios)}")
```

---

## Dependencies

### Required (New)
```toml
ortools>=9.7.0  # Google OR-Tools for optimization
```

### Already Have
- numpy, scipy (from Engine 2)
- All Phase 2A models
- Engines 1 & 2

---

## Success Criteria

Engine 3 is **complete** when:

✅ **Functional Requirements:**
1. Generates 5-10 diverse scenarios from templates
2. Validates all hard constraints
3. Optimizes capital stacks using OR-Tools
4. Integrates with Engine 1 for incentive calculations
5. Integrates with Engine 2 for waterfall/IRR analysis
6. Ranks scenarios by weighted score
7. Identifies Pareto-optimal scenarios
8. Explains trade-offs between scenarios

✅ **Quality Requirements:**
1. 90%+ test coverage
2. All tests pass
3. Type hints complete
4. Comprehensive examples

✅ **Integration Requirements:**
1. Works with Phase 2A ProjectProfile
2. Uses Engine 1 IncentiveCalculator
3. Uses Engine 2 WaterfallExecutor and StakeholderAnalyzer
4. Produces results ready for Phase 4 API

---

## Timeline Estimate

**Total:** ~10-12 hours

| Component | Time |
|-----------|------|
| ScenarioGenerator | 2h |
| ConstraintManager | 1.5h |
| CapitalStackOptimizer (OR-Tools) | 3h |
| ScenarioEvaluator | 2h |
| ScenarioComparator | 1h |
| TradeOffAnalyzer | 1h |
| Tests | 2h |
| Examples | 1.5h |

---

**End of Implementation Plan**

Ready to build the "Pathway Architect" that automatically generates optimal financing scenarios!
