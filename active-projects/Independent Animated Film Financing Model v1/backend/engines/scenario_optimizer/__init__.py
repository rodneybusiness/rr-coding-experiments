"""
Engine 3: Scenario Generator & Optimizer

Generates and evaluates diverse financing scenarios, identifying optimal
capital stack structures based on investor constraints and project requirements.
"""

from .scenario_generator import (
    FinancingTemplate,
    ScenarioConfig,
    ScenarioGenerator,
    DEFAULT_TEMPLATES
)

from .constraint_manager import (
    Constraint,
    HardConstraint,
    SoftConstraint,
    ConstraintType,
    ConstraintCategory,
    ConstraintManager,
    ConstraintViolation,
    ConstraintValidationResult
)

from .capital_stack_optimizer import (
    OptimizationObjective,
    OptimizationResult,
    CapitalStackOptimizer
)

from .scenario_evaluator import (
    ScenarioEvaluation,
    ScenarioEvaluator
)

from .scenario_comparator import (
    RankingCriterion,
    ScenarioRanking,
    ScenarioComparator
)

from .tradeoff_analyzer import (
    TradeOffPoint,
    ParetoFrontier,
    TradeOffAnalyzer
)

from .ownership_control_scorer import (
    ControlImpact,
    OwnershipControlResult,
    OwnershipControlScorer
)

__all__ = [
    # Scenario Generation
    "FinancingTemplate",
    "ScenarioConfig",
    "ScenarioGenerator",
    "DEFAULT_TEMPLATES",

    # Constraint Management
    "Constraint",
    "HardConstraint",
    "SoftConstraint",
    "ConstraintType",
    "ConstraintCategory",
    "ConstraintManager",
    "ConstraintViolation",
    "ConstraintValidationResult",

    # Optimization
    "OptimizationObjective",
    "OptimizationResult",
    "CapitalStackOptimizer",

    # Evaluation
    "ScenarioEvaluation",
    "ScenarioEvaluator",

    # Comparison
    "RankingCriterion",
    "ScenarioRanking",
    "ScenarioComparator",

    # Trade-off Analysis
    "TradeOffPoint",
    "ParetoFrontier",
    "TradeOffAnalyzer",

    # Ownership & Control Scoring
    "ControlImpact",
    "OwnershipControlResult",
    "OwnershipControlScorer",
]
