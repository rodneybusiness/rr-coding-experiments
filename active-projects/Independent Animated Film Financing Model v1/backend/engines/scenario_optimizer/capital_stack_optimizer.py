"""
Capital Stack Optimizer

Uses scipy.optimize to find optimal capital stack configurations that maximize
objective function while satisfying constraints. Integrates with Engines 1 & 2
through ScenarioEvaluator for accurate non-linear optimization.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from decimal import Decimal
from enum import Enum

import numpy as np
from scipy.optimize import minimize, Bounds, LinearConstraint

from models.capital_stack import CapitalStack, CapitalComponent
from models.financial_instruments import (
    Equity, SeniorDebt, MezzanineDebt, GapFinancing, PreSale, TaxIncentive, Debt
)
from .constraint_manager import ConstraintManager
from .scenario_evaluator import ScenarioEvaluator

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    """Optimization objective."""
    MAXIMIZE_EQUITY_OWNERSHIP = "maximize_equity_ownership"
    MINIMIZE_COST_OF_CAPITAL = "minimize_cost_of_capital"
    MAXIMIZE_TAX_INCENTIVES = "maximize_tax_incentives"
    BALANCED_STRUCTURE = "balanced_structure"
    MINIMIZE_DILUTION = "minimize_dilution"
    MAXIMIZE_OVERALL_SCORE = "maximize_overall_score"  # NEW: Use ScenarioEvaluator score


@dataclass
class OptimizationResult:
    """
    Result of capital stack optimization.

    Attributes:
        objective_value: Achieved objective value
        capital_stack: Optimized CapitalStack
        solver_status: Scipy solver status
        solve_time_seconds: Time taken to solve
        allocations: Percentage allocations by instrument type
        metadata: Additional optimization data
    """
    objective_value: Decimal
    capital_stack: CapitalStack
    solver_status: str
    solve_time_seconds: float
    allocations: Dict[str, Decimal]
    metadata: Dict[str, Any] = field(default_factory=dict)


class CapitalStackOptimizer:
    """
    Optimize capital stack using scipy.optimize.

    Finds optimal allocation of financing instruments to maximize objective
    while satisfying hard and soft constraints. Integrates with ScenarioEvaluator
    for accurate evaluation using Engines 1 & 2.
    """

    def __init__(
        self,
        constraint_manager: Optional[ConstraintManager] = None,
        evaluator: Optional[ScenarioEvaluator] = None
    ):
        """
        Initialize optimizer.

        Args:
            constraint_manager: ConstraintManager (creates default if None)
            evaluator: ScenarioEvaluator for objective function (creates default if None)
        """
        self.constraint_manager = constraint_manager or ConstraintManager()
        self.evaluator = evaluator or ScenarioEvaluator()
        self.evaluation_cache = {}
        logger.info("CapitalStackOptimizer initialized with scipy backend")

    def optimize(
        self,
        template_stack: CapitalStack,
        project_budget: Decimal,
        objective_weights: Optional[Dict[str, Decimal]] = None,
        bounds: Optional[Dict[str, Tuple[Decimal, Decimal]]] = None,
        scenario_name: str = "optimized_scenario",
        waterfall_structure: Optional[Any] = None
    ) -> OptimizationResult:
        """
        Optimize capital stack starting from template.

        Args:
            template_stack: Starting capital stack (provides structure)
            project_budget: Total project budget
            objective_weights: Weights for multi-objective optimization
            bounds: Optional (min%, max%) bounds per instrument type
            scenario_name: Name for resulting scenario
            waterfall_structure: WaterfallStructure for evaluation (uses default if None)

        Returns:
            OptimizationResult with optimal capital stack
        """
        logger.info(f"Starting scipy optimization for {scenario_name}")
        start_time = time.time()

        # Clear cache for fresh optimization
        self.evaluation_cache = {}

        # Extract instruments from template
        instruments = [c.instrument for c in template_stack.components]
        instrument_types = [type(inst).__name__.lower().replace("debt", "_debt") for inst in instruments]

        # Map instrument instances to their types
        instrument_map = {
            self._normalize_instrument_type(type(inst).__name__): inst
            for inst in instruments
        }

        # Get initial amounts
        initial_amounts = np.array([float(inst.amount) for inst in instruments])
        budget_float = float(project_budget)

        # Normalize to percentages (more numerically stable)
        initial_percentages = initial_amounts / budget_float * 100.0

        # Set up bounds for each instrument
        lower_bounds = []
        upper_bounds = []

        for inst, inst_type in zip(instruments, instrument_types):
            min_pct, max_pct = self._get_bounds(inst_type, bounds)
            lower_bounds.append(float(min_pct))
            upper_bounds.append(float(max_pct))

        bounds_obj = Bounds(lb=lower_bounds, ub=upper_bounds)

        # Constraint: allocations must sum to 100%
        A_eq = np.ones((1, len(instruments)))
        b_eq = np.array([100.0])
        equality_constraint = LinearConstraint(A_eq, b_eq, b_eq)

        # Define objective function
        weights = objective_weights or self._get_default_weights()

        def objective_function(percentages):
            """Objective to minimize (negative score to maximize)."""
            # Convert percentages back to amounts
            amounts = percentages / 100.0 * budget_float

            # Build capital stack
            stack = self._build_stack_from_amounts(
                instruments,
                amounts,
                project_budget,
                scenario_name
            )

            # Validate hard constraints (fast)
            validation = self.constraint_manager.validate(stack)
            if not validation.is_valid:
                return 1_000_000.0  # Penalty for constraint violation

            # Validate structural integrity
            if not self._validate_structure(stack):
                return 1_000_000.0  # Penalty for structural violation

            # Evaluate using ScenarioEvaluator (accurate but expensive)
            cache_key = self._get_cache_key(amounts)
            if cache_key in self.evaluation_cache:
                evaluation = self.evaluation_cache[cache_key]
            else:
                # Use evaluator with waterfall if provided
                if waterfall_structure:
                    evaluation = self.evaluator.evaluate(
                        stack,
                        waterfall_structure,
                        run_monte_carlo=False  # Skip Monte Carlo in optimization
                    )
                else:
                    # Fallback: use simple scoring without waterfall
                    evaluation = self._simple_evaluation(stack)

                self.evaluation_cache[cache_key] = evaluation

            # Calculate weighted score
            score = self._calculate_weighted_score(evaluation, weights)

            # Return negative (minimize negative = maximize positive)
            return -float(score)

        # Run optimization
        result = minimize(
            objective_function,
            x0=initial_percentages,
            method='SLSQP',
            bounds=bounds_obj,
            constraints=[equality_constraint],
            options={
                'maxiter': 100,
                'ftol': 1e-6,
                'disp': False
            }
        )

        solve_time = time.time() - start_time

        # Extract solution
        if result.success:
            optimal_percentages = result.x
            optimal_amounts = optimal_percentages / 100.0 * budget_float

            # Build optimal capital stack
            optimal_stack = self._build_stack_from_amounts(
                instruments,
                optimal_amounts,
                project_budget,
                scenario_name
            )

            # Calculate final allocations
            allocations = {
                self._normalize_instrument_type(type(inst).__name__): Decimal(str(pct))
                for inst, pct in zip(instruments, optimal_percentages)
            }

            optimization_result = OptimizationResult(
                objective_value=Decimal(str(-result.fun)),  # Negative back to positive
                capital_stack=optimal_stack,
                solver_status="SUCCESS",
                solve_time_seconds=solve_time,
                allocations=allocations,
                metadata={
                    "num_iterations": result.nit,
                    "num_evaluations": result.nfev,
                    "cache_hits": len(self.evaluation_cache),
                    "method": "SLSQP"
                }
            )

            logger.info(f"Optimization SUCCESS in {solve_time:.2f}s ({result.nfev} evaluations)")
            return optimization_result

        else:
            logger.error(f"Optimization failed: {result.message}")
            raise ValueError(f"Optimization failed: {result.message}")

    def optimize_with_convergence(
        self,
        template_stack: CapitalStack,
        project_budget: Decimal,
        objective_weights: Optional[Dict[str, Decimal]] = None,
        bounds: Optional[Dict[str, Tuple[Decimal, Decimal]]] = None,
        scenario_name: str = "optimized_scenario",
        waterfall_structure: Optional[Any] = None,
        num_starts: int = 3
    ) -> OptimizationResult:
        """
        Optimize with convergence validation from multiple random starts.

        Runs optimization from multiple initial points to avoid local optima
        and ensure robust convergence.

        Args:
            template_stack: Starting capital stack
            project_budget: Total project budget
            objective_weights: Weights for multi-objective
            bounds: Optional bounds per instrument
            scenario_name: Scenario name
            waterfall_structure: WaterfallStructure for evaluation
            num_starts: Number of random starts (default 3)

        Returns:
            Best OptimizationResult across all starts
        """
        logger.info(f"Running optimization with {num_starts} random starts for convergence")

        results = []

        # First run: from template
        try:
            result = self.optimize(
                template_stack,
                project_budget,
                objective_weights,
                bounds,
                f"{scenario_name}_start_0",
                waterfall_structure
            )
            results.append(result)
        except Exception as e:
            logger.warning(f"Start 0 (template) failed: {e}")

        # Additional runs: from random perturbations
        for i in range(1, num_starts):
            try:
                # Create perturbed starting point
                perturbed_stack = self._perturb_stack(template_stack, perturbation=0.15)

                result = self.optimize(
                    perturbed_stack,
                    project_budget,
                    objective_weights,
                    bounds,
                    f"{scenario_name}_start_{i}",
                    waterfall_structure
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Start {i} failed: {e}")

        if not results:
            raise ValueError("All optimization starts failed")

        # Select best result
        best_result = max(results, key=lambda r: r.objective_value)

        # Update metadata with convergence info
        scores = [r.objective_value for r in results]
        best_result.metadata.update({
            "num_starts": len(results),
            "convergence_scores": [float(s) for s in scores],
            "convergence_std": float(np.std([float(s) for s in scores])),
            "convergence_range": float(max(scores) - min(scores))
        })

        # Update scenario name
        best_result.capital_stack.stack_name = scenario_name

        logger.info(f"Convergence validation: {len(results)} successful starts, best score: {best_result.objective_value:.2f}")

        return best_result

    def _validate_structure(self, stack: CapitalStack) -> bool:
        """
        Validate structural integrity of capital stack.

        Business rules:
        1. Gap financing requires senior debt present
        2. Mezzanine debt should not exceed senior debt
        3. Tax credit loan requires tax incentive
        4. Equity premium requires equity base

        Args:
            stack: CapitalStack to validate

        Returns:
            True if structurally valid, False otherwise
        """
        # Extract instrument amounts by type
        amounts = {}
        for component in stack.components:
            inst_type = type(component.instrument).__name__
            amounts[inst_type] = component.instrument.amount

        # Rule 1: Gap financing requires senior debt
        if "GapFinancing" in amounts:
            if "SeniorDebt" not in amounts or amounts.get("SeniorDebt", Decimal("0")) == 0:
                logger.debug("Structural validation failed: Gap financing without senior debt")
                return False

        # Rule 2: Mezzanine should not exceed senior debt
        if "MezzanineDebt" in amounts and "SeniorDebt" in amounts:
            if amounts["MezzanineDebt"] > amounts["SeniorDebt"]:
                logger.debug("Structural validation failed: Mezzanine exceeds senior debt")
                return False

        # Rule 3: Total debt should not be extreme without equity cushion
        total_debt = sum(
            amount for inst_type, amount in amounts.items()
            if "Debt" in inst_type or inst_type == "GapFinancing"
        )
        total_equity = amounts.get("Equity", Decimal("0"))

        if total_debt > 0 and total_equity > 0:
            debt_to_equity = total_debt / total_equity
            if debt_to_equity > Decimal("5.0"):  # Max 5:1 leverage
                logger.debug(f"Structural validation failed: Debt/equity ratio {debt_to_equity:.2f} too high")
                return False

        return True

    def _get_bounds(
        self,
        instrument: str,
        bounds: Optional[Dict[str, Tuple[Decimal, Decimal]]]
    ) -> Tuple[Decimal, Decimal]:
        """
        Get min/max percentage bounds for instrument.

        Args:
            instrument: Instrument type
            bounds: Optional bounds dict

        Returns:
            (min_pct, max_pct) tuple
        """
        # Default bounds
        default_bounds = {
            "equity": (Decimal("15.0"), Decimal("80.0")),
            "senior_debt": (Decimal("0"), Decimal("60.0")),
            "mezzanine_debt": (Decimal("0"), Decimal("30.0")),
            "gap_financing": (Decimal("0"), Decimal("25.0")),
            "pre_sale": (Decimal("0"), Decimal("40.0")),
            "pre_sales": (Decimal("0"), Decimal("40.0")),
            "tax_incentive": (Decimal("0"), Decimal("35.0")),
            "tax_incentives": (Decimal("0"), Decimal("35.0"))
        }

        if bounds and instrument in bounds:
            return bounds[instrument]

        return default_bounds.get(instrument, (Decimal("0"), Decimal("50.0")))

    def _get_default_weights(self) -> Dict[str, Decimal]:
        """Get default objective weights."""
        return {
            "equity_irr": Decimal("0.30"),
            "tax_incentives": Decimal("0.20"),
            "risk": Decimal("0.20"),
            "cost_of_capital": Decimal("0.15"),
            "debt_recovery": Decimal("0.15")
        }

    def _calculate_weighted_score(
        self,
        evaluation: Any,
        weights: Dict[str, Decimal]
    ) -> Decimal:
        """
        Calculate weighted score from evaluation.

        Args:
            evaluation: ScenarioEvaluation object
            weights: Objective weights

        Returns:
            Weighted score (0-100)
        """
        score = Decimal("0")

        # Equity IRR component
        if evaluation.equity_irr and "equity_irr" in weights:
            # Normalize to 0-1 (target 20% IRR)
            irr_score = min(evaluation.equity_irr / Decimal("20.0"), Decimal("1.0"))
            score += irr_score * weights["equity_irr"] * Decimal("100")

        # Tax incentives component
        if "tax_incentives" in weights:
            # Normalize to 0-1 (target 20% of budget)
            incentive_score = min(
                evaluation.tax_incentive_effective_rate / Decimal("20.0"),
                Decimal("1.0")
            )
            score += incentive_score * weights["tax_incentives"] * Decimal("100")

        # Risk component
        if "risk" in weights:
            # Higher recoupment probability is better
            risk_score = min(
                evaluation.probability_of_equity_recoupment / Decimal("0.80"),
                Decimal("1.0")
            )
            score += risk_score * weights["risk"] * Decimal("100")

        # Cost of capital component
        if evaluation.weighted_cost_of_capital > 0 and "cost_of_capital" in weights:
            # Lower WACC is better (target 12%)
            cost_score = min(
                Decimal("12.0") / evaluation.weighted_cost_of_capital,
                Decimal("1.0")
            )
            score += cost_score * weights["cost_of_capital"] * Decimal("100")

        # Debt recovery component
        if "debt_recovery" in weights:
            # Higher recovery is better
            debt_score = min(
                evaluation.senior_debt_recovery_rate / Decimal("100.0"),
                Decimal("1.0")
            )
            score += debt_score * weights["debt_recovery"] * Decimal("100")

        return score

    def _simple_evaluation(self, stack: CapitalStack) -> Any:
        """
        Simple evaluation without waterfall (fallback).

        Creates a minimal evaluation for optimization when waterfall not provided.
        """
        from backend.engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluation

        evaluation = ScenarioEvaluation(
            scenario_name=stack.stack_name,
            capital_stack=stack
        )

        # Simple metrics calculation
        total = stack.project_budget

        # Tax incentives
        tax_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, TaxIncentive)
        )
        evaluation.tax_incentive_gross_credit = tax_amount
        evaluation.tax_incentive_effective_rate = (tax_amount / total) * Decimal("100")

        # Cost of capital estimate
        weighted_cost = Decimal("0")
        for component in stack.components:
            inst = component.instrument
            weight = inst.amount / total

            if isinstance(inst, Debt):
                weighted_cost += weight * inst.interest_rate
            elif isinstance(inst, Equity):
                weighted_cost += weight * Decimal("20.0")  # Assume 20% equity cost
            elif isinstance(inst, TaxIncentive):
                weighted_cost += weight * Decimal("-5.0")  # Negative cost (benefit)

        evaluation.weighted_cost_of_capital = weighted_cost

        # Equity IRR estimate (rough)
        equity_amount = sum(
            c.instrument.amount for c in stack.components
            if isinstance(c.instrument, Equity)
        )
        if equity_amount > 0:
            # Rough IRR estimate based on equity percentage
            equity_pct = (equity_amount / total) * Decimal("100")
            evaluation.equity_irr = Decimal("15.0") + (Decimal("50.0") - equity_pct) / Decimal("5.0")

        return evaluation

    def _build_stack_from_amounts(
        self,
        template_instruments: List[Any],
        amounts: np.ndarray,
        project_budget: Decimal,
        scenario_name: str
    ) -> CapitalStack:
        """
        Build CapitalStack from optimized amounts.

        Args:
            template_instruments: Template instrument instances
            amounts: Optimized amounts (numpy array)
            project_budget: Project budget
            scenario_name: Scenario name

        Returns:
            CapitalStack object
        """
        components = []

        for position, (template_inst, amount_float) in enumerate(zip(template_instruments, amounts), start=1):
            amount = Decimal(str(round(amount_float, 2)))

            if amount <= 0:
                continue  # Skip zero allocations

            # Create new instrument instance with updated amount
            inst_type = type(template_inst)

            if inst_type == SeniorDebt:
                instrument = SeniorDebt(
                    amount=amount,
                    interest_rate=template_inst.interest_rate,
                    term_months=template_inst.term_months,
                    origination_fee_percentage=template_inst.origination_fee_percentage
                )
            elif inst_type == MezzanineDebt:
                instrument = MezzanineDebt(
                    amount=amount,
                    interest_rate=template_inst.interest_rate,
                    term_months=template_inst.term_months,
                    equity_kicker_percentage=template_inst.equity_kicker_percentage
                )
            elif inst_type == GapFinancing:
                instrument = GapFinancing(
                    amount=amount,
                    interest_rate=template_inst.interest_rate,
                    term_months=template_inst.term_months,
                    minimum_presales_percentage=template_inst.minimum_presales_percentage
                )
            elif inst_type == PreSale:
                instrument = PreSale(
                    amount=amount,
                    territory=template_inst.territory,
                    rights_description=template_inst.rights_description,
                    mg_amount=amount,
                    payment_on_delivery=template_inst.payment_on_delivery
                )
            elif inst_type == TaxIncentive:
                # Recalculate qualified spend based on new amount
                qualified_spend = amount / (template_inst.credit_rate / Decimal("100"))
                instrument = TaxIncentive(
                    amount=amount,
                    jurisdiction=template_inst.jurisdiction,
                    qualified_spend=qualified_spend,
                    credit_rate=template_inst.credit_rate,
                    timing_months=template_inst.timing_months
                )
            elif inst_type == Equity:
                instrument = Equity(
                    amount=amount,
                    ownership_percentage=template_inst.ownership_percentage,
                    premium_percentage=template_inst.premium_percentage
                )
            else:
                logger.warning(f"Unknown instrument type: {inst_type}")
                continue

            components.append(CapitalComponent(instrument=instrument, position=position))

        return CapitalStack(
            stack_name=scenario_name,
            project_budget=project_budget,
            components=components
        )

    def _perturb_stack(self, stack: CapitalStack, perturbation: float = 0.1) -> CapitalStack:
        """
        Create perturbed version of capital stack for convergence testing.

        Args:
            stack: Original stack
            perturbation: Perturbation magnitude (0.1 = 10%)

        Returns:
            Perturbed CapitalStack
        """
        import random

        perturbed_components = []

        # Get amounts and perturb them
        amounts = [c.instrument.amount for c in stack.components]
        total = sum(amounts)

        # Add random noise
        perturbed_amounts = []
        for amount in amounts:
            pct = amount / total
            noise = random.uniform(-perturbation, perturbation)
            new_pct = max(0.01, pct + noise)  # Ensure positive
            perturbed_amounts.append(new_pct)

        # Renormalize to sum to 1.0
        total_pct = sum(perturbed_amounts)
        perturbed_amounts = [p / total_pct for p in perturbed_amounts]

        # Build perturbed stack
        for position, (component, pct) in enumerate(zip(stack.components, perturbed_amounts), start=1):
            new_amount = Decimal(str(round(float(total) * pct, 2)))

            # Create new instrument with perturbed amount
            inst_type = type(component.instrument)
            template_inst = component.instrument

            if inst_type == SeniorDebt:
                instrument = SeniorDebt(
                    amount=new_amount,
                    interest_rate=template_inst.interest_rate,
                    term_months=template_inst.term_months,
                    origination_fee_percentage=template_inst.origination_fee_percentage
                )
            elif inst_type == MezzanineDebt:
                instrument = MezzanineDebt(
                    amount=new_amount,
                    interest_rate=template_inst.interest_rate,
                    term_months=template_inst.term_months,
                    equity_kicker_percentage=template_inst.equity_kicker_percentage
                )
            elif inst_type == GapFinancing:
                instrument = GapFinancing(
                    amount=new_amount,
                    interest_rate=template_inst.interest_rate,
                    term_months=template_inst.term_months,
                    minimum_presales_percentage=template_inst.minimum_presales_percentage
                )
            elif inst_type == PreSale:
                instrument = PreSale(
                    amount=new_amount,
                    territory=template_inst.territory,
                    rights_description=template_inst.rights_description,
                    mg_amount=new_amount,
                    payment_on_delivery=template_inst.payment_on_delivery
                )
            elif inst_type == TaxIncentive:
                qualified_spend = new_amount / (template_inst.credit_rate / Decimal("100"))
                instrument = TaxIncentive(
                    amount=new_amount,
                    jurisdiction=template_inst.jurisdiction,
                    qualified_spend=qualified_spend,
                    credit_rate=template_inst.credit_rate,
                    timing_months=template_inst.timing_months
                )
            elif inst_type == Equity:
                instrument = Equity(
                    amount=new_amount,
                    ownership_percentage=template_inst.ownership_percentage,
                    premium_percentage=template_inst.premium_percentage
                )
            else:
                continue

            perturbed_components.append(CapitalComponent(instrument=instrument, position=position))

        return CapitalStack(
            stack_name=f"{stack.stack_name}_perturbed",
            project_budget=stack.project_budget,
            components=perturbed_components
        )

    def _normalize_instrument_type(self, type_name: str) -> str:
        """Normalize instrument type name for consistency."""
        # Convert SeniorDebt -> senior_debt, etc.
        normalized = ""
        for i, char in enumerate(type_name):
            if char.isupper() and i > 0:
                normalized += "_"
            normalized += char.lower()
        return normalized

    def _get_cache_key(self, amounts: np.ndarray) -> str:
        """Create cache key from amounts (rounded for stability)."""
        rounded = tuple(round(float(a), -3) for a in amounts)  # Round to nearest 1000
        return str(rounded)
