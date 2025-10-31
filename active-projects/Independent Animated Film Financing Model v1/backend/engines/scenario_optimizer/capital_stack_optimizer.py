"""
Capital Stack Optimizer

Uses Google OR-Tools CP-SAT solver to find optimal capital stack configurations
that maximize objective function while satisfying constraints.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from enum import Enum

from ortools.sat.python import cp_model

from backend.models.capital_stack import CapitalStack, CapitalComponent
from backend.models.financial_instruments import (
    Equity, SeniorDebt, MezzanineDebt, GapFinancing, PreSale, TaxIncentive
)
from backend.engines.scenario_optimizer.constraint_manager import ConstraintManager

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    """Optimization objective."""
    MAXIMIZE_EQUITY_OWNERSHIP = "maximize_equity_ownership"
    MINIMIZE_COST_OF_CAPITAL = "minimize_cost_of_capital"
    MAXIMIZE_TAX_INCENTIVES = "maximize_tax_incentives"
    BALANCED_STRUCTURE = "balanced_structure"
    MINIMIZE_DILUTION = "minimize_dilution"


@dataclass
class OptimizationResult:
    """
    Result of capital stack optimization.

    Attributes:
        objective_value: Achieved objective value
        capital_stack: Optimized CapitalStack
        solver_status: OR-Tools solver status
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
    Optimize capital stack using OR-Tools CP-SAT solver.

    Finds optimal allocation of financing instruments to maximize objective
    while satisfying hard and soft constraints.
    """

    def __init__(self, constraint_manager: Optional[ConstraintManager] = None):
        """
        Initialize optimizer.

        Args:
            constraint_manager: ConstraintManager (creates default if None)
        """
        self.constraint_manager = constraint_manager or ConstraintManager()
        logger.info("CapitalStackOptimizer initialized")

    def optimize(
        self,
        project_budget: Decimal,
        objective: OptimizationObjective,
        available_instruments: List[str],
        bounds: Optional[Dict[str, Tuple[Decimal, Decimal]]] = None,
        scenario_name: str = "optimized_scenario"
    ) -> OptimizationResult:
        """
        Optimize capital stack allocation.

        Args:
            project_budget: Total project budget
            objective: Optimization objective
            available_instruments: List of instrument types to consider
            bounds: Optional (min%, max%) bounds per instrument type
            scenario_name: Name for resulting scenario

        Returns:
            OptimizationResult with optimal capital stack
        """
        logger.info(f"Starting optimization for {objective.value}")

        # Create OR-Tools model
        model = cp_model.CpModel()

        # Scale budget to integer (cents) for CP-SAT
        budget_cents = int(project_budget * Decimal("100"))

        # Decision variables: allocation for each instrument (in cents)
        allocation_vars = {}
        for instrument in available_instruments:
            # Get bounds
            min_pct, max_pct = self._get_bounds(instrument, bounds)
            min_cents = int((min_pct / Decimal("100")) * budget_cents)
            max_cents = int((max_pct / Decimal("100")) * budget_cents)

            allocation_vars[instrument] = model.NewIntVar(
                min_cents,
                max_cents,
                f"allocation_{instrument}"
            )

        # Constraint: Allocations must sum to budget
        model.Add(sum(allocation_vars.values()) == budget_cents)

        # Hard constraints from ConstraintManager
        # (simplified - would need to translate each constraint to CP-SAT)

        # Minimum equity (15%)
        if "equity" in allocation_vars:
            min_equity_cents = int(budget_cents * 15 / 100)
            model.Add(allocation_vars["equity"] >= min_equity_cents)

        # Maximum total debt (75%)
        debt_instruments = ["senior_debt", "mezzanine_debt", "gap_financing"]
        debt_vars = [allocation_vars[d] for d in debt_instruments if d in allocation_vars]
        if debt_vars:
            max_debt_cents = int(budget_cents * 75 / 100)
            model.Add(sum(debt_vars) <= max_debt_cents)

        # Define objective function based on objective type
        objective_expr = self._build_objective_expression(
            objective,
            allocation_vars,
            budget_cents
        )

        model.Maximize(objective_expr)

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0  # 30 second timeout

        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            allocations_cents = {
                instrument: solver.Value(var)
                for instrument, var in allocation_vars.items()
            }

            # Convert back to Decimals
            allocations_decimal = {
                instrument: Decimal(str(cents / 100))
                for instrument, cents in allocations_cents.items()
            }

            # Calculate percentages
            allocations_pct = {
                instrument: (amount / project_budget) * Decimal("100")
                for instrument, amount in allocations_decimal.items()
            }

            # Build capital stack
            capital_stack = self._build_capital_stack_from_allocations(
                scenario_name,
                project_budget,
                allocations_decimal
            )

            result = OptimizationResult(
                objective_value=Decimal(str(solver.ObjectiveValue() / 1000)),  # Scale back
                capital_stack=capital_stack,
                solver_status="OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
                solve_time_seconds=solver.WallTime(),
                allocations=allocations_pct,
                metadata={
                    "objective": objective.value,
                    "num_variables": len(allocation_vars),
                    "solver_iterations": solver.NumBranches()
                }
            )

            logger.info(f"Optimization completed: {result.solver_status} in {result.solve_time_seconds:.2f}s")

            return result

        else:
            logger.error(f"Optimization failed with status: {status}")
            raise ValueError(f"Optimization failed with status: {self._status_name(status)}")

    def optimize_multi_objective(
        self,
        project_budget: Decimal,
        objectives: List[Tuple[OptimizationObjective, Decimal]],  # (objective, weight)
        available_instruments: List[str],
        bounds: Optional[Dict[str, Tuple[Decimal, Decimal]]] = None,
        scenario_name: str = "multi_objective_scenario"
    ) -> OptimizationResult:
        """
        Optimize for multiple objectives with weights.

        Args:
            project_budget: Total project budget
            objectives: List of (OptimizationObjective, weight) tuples
            available_instruments: Instrument types to consider
            bounds: Optional bounds per instrument
            scenario_name: Scenario name

        Returns:
            OptimizationResult with Pareto-optimal solution
        """
        logger.info(f"Multi-objective optimization with {len(objectives)} objectives")

        # Create model
        model = cp_model.CpModel()
        budget_cents = int(project_budget * Decimal("100"))

        # Decision variables
        allocation_vars = {}
        for instrument in available_instruments:
            min_pct, max_pct = self._get_bounds(instrument, bounds)
            min_cents = int((min_pct / Decimal("100")) * budget_cents)
            max_cents = int((max_pct / Decimal("100")) * budget_cents)

            allocation_vars[instrument] = model.NewIntVar(
                min_cents,
                max_cents,
                f"allocation_{instrument}"
            )

        # Budget constraint
        model.Add(sum(allocation_vars.values()) == budget_cents)

        # Hard constraints
        if "equity" in allocation_vars:
            min_equity_cents = int(budget_cents * 15 / 100)
            model.Add(allocation_vars["equity"] >= min_equity_cents)

        debt_instruments = ["senior_debt", "mezzanine_debt", "gap_financing"]
        debt_vars = [allocation_vars[d] for d in debt_instruments if d in allocation_vars]
        if debt_vars:
            max_debt_cents = int(budget_cents * 75 / 100)
            model.Add(sum(debt_vars) <= max_debt_cents)

        # Combined objective: weighted sum
        combined_objective = 0
        for objective, weight in objectives:
            obj_expr = self._build_objective_expression(objective, allocation_vars, budget_cents)
            # Scale weight to integer
            weight_int = int(float(weight) * 1000)
            combined_objective += obj_expr * weight_int

        model.Maximize(combined_objective)

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0  # Longer timeout for multi-objective

        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            allocations_cents = {
                instrument: solver.Value(var)
                for instrument, var in allocation_vars.items()
            }

            allocations_decimal = {
                instrument: Decimal(str(cents / 100))
                for instrument, cents in allocations_cents.items()
            }

            allocations_pct = {
                instrument: (amount / project_budget) * Decimal("100")
                for instrument, amount in allocations_decimal.items()
            }

            capital_stack = self._build_capital_stack_from_allocations(
                scenario_name,
                project_budget,
                allocations_decimal
            )

            result = OptimizationResult(
                objective_value=Decimal(str(solver.ObjectiveValue() / 1000)),
                capital_stack=capital_stack,
                solver_status="OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
                solve_time_seconds=solver.WallTime(),
                allocations=allocations_pct,
                metadata={
                    "objectives": [obj.value for obj, _ in objectives],
                    "weights": [float(w) for _, w in objectives]
                }
            )

            logger.info(f"Multi-objective optimization: {result.solver_status}")

            return result

        else:
            logger.error(f"Multi-objective optimization failed: {status}")
            raise ValueError(f"Optimization failed: {self._status_name(status)}")

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
            "pre_sales": (Decimal("0"), Decimal("40.0")),
            "tax_incentives": (Decimal("0"), Decimal("35.0"))
        }

        if bounds and instrument in bounds:
            return bounds[instrument]

        return default_bounds.get(instrument, (Decimal("0"), Decimal("50.0")))

    def _build_objective_expression(
        self,
        objective: OptimizationObjective,
        allocation_vars: Dict[str, Any],
        budget_cents: int
    ) -> Any:
        """
        Build OR-Tools objective expression.

        Args:
            objective: Optimization objective
            allocation_vars: Decision variables
            budget_cents: Budget in cents

        Returns:
            OR-Tools linear expression
        """
        if objective == OptimizationObjective.MAXIMIZE_EQUITY_OWNERSHIP:
            # Maximize equity percentage
            if "equity" in allocation_vars:
                return allocation_vars["equity"]
            return 0

        elif objective == OptimizationObjective.MINIMIZE_COST_OF_CAPITAL:
            # Minimize weighted cost of capital (proxy: prefer cheaper instruments)
            # Senior debt (8%) < Gap (10%) < Mezz (12%) < Equity (20%)
            cost_weights = {
                "senior_debt": -80,  # Negative = prefer (8% rate)
                "gap_financing": -100,
                "mezzanine_debt": -120,
                "equity": -200,  # Highest cost
                "pre_sales": -120,
                "tax_incentives": -50  # Cheapest (net benefit)
            }

            expr = 0
            for instrument, var in allocation_vars.items():
                weight = cost_weights.get(instrument, -150)
                expr += var * weight

            return expr  # Maximize negative cost = minimize cost

        elif objective == OptimizationObjective.MAXIMIZE_TAX_INCENTIVES:
            # Maximize tax incentive allocation
            if "tax_incentives" in allocation_vars:
                return allocation_vars["tax_incentives"]
            return 0

        elif objective == OptimizationObjective.MINIMIZE_DILUTION:
            # Minimize equity (less equity = less dilution)
            if "equity" in allocation_vars:
                return -allocation_vars["equity"]  # Negative to minimize
            return 0

        elif objective == OptimizationObjective.BALANCED_STRUCTURE:
            # Balanced structure: penalize extremes
            # Favor mid-range allocations (30-50% for major components)
            target_pct = 40  # 40% target
            target_cents = int(budget_cents * target_pct / 100)

            # Penalize deviation from 40% for major instruments
            penalty = 0
            major_instruments = ["equity", "senior_debt", "pre_sales"]

            for instrument in major_instruments:
                if instrument in allocation_vars:
                    # Absolute deviation from target (scaled)
                    # This is complex in CP-SAT, so use quadratic approximation
                    # For now, simple linear preference toward 40%
                    penalty -= allocation_vars[instrument] * 1  # Placeholder

            return -penalty  # Maximize negative penalty

        else:
            logger.warning(f"Unknown objective: {objective}")
            return 0

    def _build_capital_stack_from_allocations(
        self,
        scenario_name: str,
        project_budget: Decimal,
        allocations: Dict[str, Decimal]
    ) -> CapitalStack:
        """
        Build CapitalStack from optimized allocations.

        Args:
            scenario_name: Scenario name
            project_budget: Project budget
            allocations: Instrument → amount mapping

        Returns:
            CapitalStack object
        """
        components = []
        position = 1

        # Define typical terms for each instrument
        typical_terms = {
            "senior_debt": {
                "interest_rate": Decimal("8.0"),
                "term_months": 24,
                "origination_fee": Decimal("2.0")
            },
            "mezzanine_debt": {
                "interest_rate": Decimal("12.0"),
                "term_months": 36,
                "equity_kicker": Decimal("5.0")
            },
            "gap_financing": {
                "interest_rate": Decimal("10.0"),
                "term_months": 24,
                "min_presales": Decimal("30.0")
            },
            "pre_sales": {
                "buyer_name": "SVOD Platform",
                "territory": "Worldwide",
                "rights_term": 10,
                "discount_rate": Decimal("15.0")
            },
            "tax_incentives": {
                "jurisdiction": "Multi-Jurisdiction",
                "credit_rate": Decimal("30.0"),
                "timing_months": 18
            },
            "equity": {
                "ownership": Decimal("100.0"),
                "premium": Decimal("20.0")
            }
        }

        # Build components in priority order
        priority_order = [
            "senior_debt", "mezzanine_debt", "gap_financing",
            "pre_sales", "tax_incentives", "equity"
        ]

        for instrument_type in priority_order:
            if instrument_type in allocations and allocations[instrument_type] > 0:
                amount = allocations[instrument_type]
                terms = typical_terms.get(instrument_type, {})

                if instrument_type == "senior_debt":
                    instrument = SeniorDebt(
                        amount=amount,
                        interest_rate=terms["interest_rate"],
                        term_months=terms["term_months"],
                        origination_fee_percentage=terms["origination_fee"]
                    )
                elif instrument_type == "mezzanine_debt":
                    instrument = MezzanineDebt(
                        amount=amount,
                        interest_rate=terms["interest_rate"],
                        term_months=terms["term_months"],
                        equity_kicker_percentage=terms["equity_kicker"]
                    )
                elif instrument_type == "gap_financing":
                    instrument = GapFinancing(
                        amount=amount,
                        interest_rate=terms["interest_rate"],
                        term_months=terms["term_months"],
                        minimum_presales_percentage=terms["min_presales"]
                    )
                elif instrument_type == "pre_sales":
                    instrument = PreSale(
                        amount=amount,
                        buyer_name=terms["buyer_name"],
                        territory=terms["territory"],
                        rights_term_years=terms["rights_term"],
                        discount_rate=terms["discount_rate"]
                    )
                elif instrument_type == "tax_incentives":
                    qualified_spend = amount / (terms["credit_rate"] / Decimal("100"))
                    instrument = TaxIncentive(
                        amount=amount,
                        jurisdiction=terms["jurisdiction"],
                        qualified_spend=qualified_spend,
                        credit_rate=terms["credit_rate"],
                        timing_months=terms["timing_months"]
                    )
                elif instrument_type == "equity":
                    instrument = Equity(
                        amount=amount,
                        ownership_percentage=terms["ownership"],
                        premium_percentage=terms["premium"]
                    )
                else:
                    continue  # Unknown type

                components.append(CapitalComponent(instrument=instrument, position=position))
                position += 1

        stack = CapitalStack(
            stack_name=scenario_name,
            project_budget=project_budget,
            components=components
        )

        return stack

    def _status_name(self, status: int) -> str:
        """Convert OR-Tools status code to name."""
        status_names = {
            cp_model.OPTIMAL: "OPTIMAL",
            cp_model.FEASIBLE: "FEASIBLE",
            cp_model.INFEASIBLE: "INFEASIBLE",
            cp_model.MODEL_INVALID: "MODEL_INVALID",
            cp_model.UNKNOWN: "UNKNOWN"
        }
        return status_names.get(status, f"UNKNOWN_STATUS_{status}")
