"""
Monte Carlo Simulator

Runs Monte Carlo simulations of revenue uncertainty to quantify risk and
generate confidence intervals for investor returns.
"""

import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal

from backend.models.waterfall import WaterfallStructure
from backend.models.capital_stack import CapitalStack
from backend.engines.waterfall_executor.revenue_projector import RevenueProjector, RevenueProjection
from backend.engines.waterfall_executor.waterfall_executor import WaterfallExecutor
from backend.engines.waterfall_executor.stakeholder_analyzer import StakeholderAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class RevenueDistribution:
    """
    Statistical distribution for a revenue variable.

    Attributes:
        variable_name: Variable identifier
        distribution_type: Distribution type (triangular, uniform, normal)
        parameters: Distribution parameters (min, mode, max for triangular)
    """
    variable_name: str
    distribution_type: str  # "triangular", "uniform", "normal"
    parameters: Dict[str, Decimal]

    def __post_init__(self):
        """Validate distribution parameters"""
        if self.distribution_type == "triangular":
            required = ["min", "mode", "max"]
            for param in required:
                if param not in self.parameters:
                    raise ValueError(f"Triangular distribution requires {param}")


@dataclass
class MonteCarloScenario:
    """
    Single simulation scenario.

    Attributes:
        scenario_id: Scenario number
        total_revenue: Sampled total revenue
        stakeholder_results: Stakeholder → metrics dict
    """
    scenario_id: int
    total_revenue: Decimal
    stakeholder_results: Dict[str, Dict[str, Decimal]] = field(default_factory=dict)


@dataclass
class MonteCarloResult:
    """
    Result of Monte Carlo simulation.

    Attributes:
        num_simulations: Number of scenarios run
        scenarios: List of scenarios
        revenue_percentiles: P10, P50, P90 for revenue
        stakeholder_percentiles: Stakeholder → metric percentiles
        probability_of_recoupment: Stakeholder → probability
        metadata: Simulation parameters
    """
    num_simulations: int
    scenarios: List[MonteCarloScenario]

    revenue_percentiles: Dict[str, Decimal]
    stakeholder_percentiles: Dict[str, Dict[str, Decimal]]
    probability_of_recoupment: Dict[str, Decimal]

    metadata: Dict[str, Any] = field(default_factory=dict)


class MonteCarloSimulator:
    """
    Run Monte Carlo simulations of revenue uncertainty.

    Simulates thousands of revenue scenarios to quantify risk and generate
    confidence intervals for investor returns.
    """

    def __init__(
        self,
        waterfall_structure: WaterfallStructure,
        capital_stack: CapitalStack,
        base_revenue_projection: RevenueProjection
    ):
        """
        Initialize simulator with base case.

        Args:
            waterfall_structure: Waterfall from Phase 2A
            capital_stack: Capital stack from Phase 2A
            base_revenue_projection: Base case projection
        """
        self.waterfall = waterfall_structure
        self.capital_stack = capital_stack
        self.base_projection = base_revenue_projection

        logger.info("MonteCarloSimulator initialized")

    def simulate(
        self,
        revenue_distribution: RevenueDistribution,
        num_simulations: int = 1000,
        seed: Optional[int] = None
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation.

        Args:
            revenue_distribution: Distribution for total revenue
            num_simulations: Number of scenarios to run
            seed: Random seed for reproducibility

        Returns:
            MonteCarloResult with percentile analysis
        """
        if seed is not None:
            random.seed(seed)

        scenarios = []
        all_revenues = []

        # Collect all stakeholder IDs
        stakeholder_ids = set()

        logger.info(f"Running {num_simulations} Monte Carlo simulations...")

        for i in range(num_simulations):
            # Sample revenue
            sampled_revenue = self._sample_from_distribution(revenue_distribution)
            all_revenues.append(sampled_revenue)

            # Generate revenue projection (scaled from base)
            # Convert metadata value to Decimal if it's a string
            total_revenue = self.base_projection.metadata["total_ultimate_revenue"]
            if isinstance(total_revenue, str):
                total_revenue = Decimal(total_revenue)
            scale_factor = sampled_revenue / total_revenue
            scaled_projection = self._scale_projection(self.base_projection, scale_factor)

            # Execute waterfall
            executor = WaterfallExecutor(self.waterfall)
            waterfall_result = executor.execute_over_time(scaled_projection)

            # Analyze stakeholders
            analyzer = StakeholderAnalyzer(self.capital_stack)
            stakeholder_analysis = analyzer.analyze(waterfall_result)

            # Extract results
            stakeholder_results = {}
            for stakeholder in stakeholder_analysis.stakeholders:
                stakeholder_ids.add(stakeholder.stakeholder_id)
                stakeholder_results[stakeholder.stakeholder_id] = {
                    "irr": stakeholder.irr if stakeholder.irr else Decimal("0"),
                    "cash_on_cash": stakeholder.cash_on_cash,
                    "total_receipts": stakeholder.total_receipts,
                    "fully_recouped": stakeholder.total_receipts >= stakeholder.initial_investment
                }

            scenario = MonteCarloScenario(
                scenario_id=i,
                total_revenue=sampled_revenue,
                stakeholder_results=stakeholder_results
            )

            scenarios.append(scenario)

        # Calculate percentiles
        revenue_percentiles = {
            "p10": self._calculate_percentile(all_revenues, 10),
            "p50": self._calculate_percentile(all_revenues, 50),
            "p90": self._calculate_percentile(all_revenues, 90)
        }

        # Calculate stakeholder percentiles
        stakeholder_percentiles = {}
        probability_of_recoupment = {}

        for stakeholder_id in stakeholder_ids:
            irrs = []
            cocs = []
            recouped_count = 0

            for scenario in scenarios:
                if stakeholder_id in scenario.stakeholder_results:
                    result = scenario.stakeholder_results[stakeholder_id]
                    irrs.append(result["irr"])
                    cocs.append(result["cash_on_cash"])
                    if result["fully_recouped"]:
                        recouped_count += 1

            stakeholder_percentiles[stakeholder_id] = {
                "irr_p10": self._calculate_percentile(irrs, 10),
                "irr_p50": self._calculate_percentile(irrs, 50),
                "irr_p90": self._calculate_percentile(irrs, 90),
                "coc_p10": self._calculate_percentile(cocs, 10),
                "coc_p50": self._calculate_percentile(cocs, 50),
                "coc_p90": self._calculate_percentile(cocs, 90),
            }

            probability_of_recoupment[stakeholder_id] = Decimal(str(recouped_count)) / Decimal(str(num_simulations))

        result = MonteCarloResult(
            num_simulations=num_simulations,
            scenarios=scenarios,
            revenue_percentiles=revenue_percentiles,
            stakeholder_percentiles=stakeholder_percentiles,
            probability_of_recoupment=probability_of_recoupment,
            metadata={
                "distribution": revenue_distribution.distribution_type,
                "seed": seed
            }
        )

        logger.info(f"Completed {num_simulations} simulations")

        return result

    def _sample_from_distribution(
        self,
        distribution: RevenueDistribution
    ) -> Decimal:
        """
        Sample a value from the specified distribution.

        Args:
            distribution: RevenueDistribution specification

        Returns:
            Sampled value as Decimal
        """
        if distribution.distribution_type == "triangular":
            # Triangular distribution
            min_val = float(distribution.parameters["min"])
            mode_val = float(distribution.parameters["mode"])
            max_val = float(distribution.parameters["max"])

            sampled = random.triangular(min_val, max_val, mode_val)
            return Decimal(str(sampled))

        elif distribution.distribution_type == "uniform":
            # Uniform distribution
            min_val = float(distribution.parameters["min"])
            max_val = float(distribution.parameters["max"])

            sampled = random.uniform(min_val, max_val)
            return Decimal(str(sampled))

        elif distribution.distribution_type == "normal":
            # Normal distribution
            mean = float(distribution.parameters["mean"])
            std = float(distribution.parameters["std"])

            sampled = random.gauss(mean, std)
            # Ensure non-negative
            sampled = max(0, sampled)
            return Decimal(str(sampled))

        else:
            raise ValueError(f"Unsupported distribution type: {distribution.distribution_type}")

    def _scale_projection(
        self,
        base_projection: RevenueProjection,
        scale_factor: Decimal
    ) -> RevenueProjection:
        """
        Scale revenue projection by a factor.

        Args:
            base_projection: Base projection
            scale_factor: Scale factor (e.g., 0.8 = 80% of base)

        Returns:
            Scaled RevenueProjection
        """
        scaled_quarterly = {
            q: amt * scale_factor
            for q, amt in base_projection.quarterly_revenue.items()
        }

        scaled_cumulative = {}
        cumulative = Decimal("0")
        for q in sorted(scaled_quarterly.keys()):
            cumulative += scaled_quarterly[q]
            scaled_cumulative[q] = cumulative

        scaled_by_window = {
            window: amt * scale_factor
            for window, amt in base_projection.by_window.items()
        }

        return RevenueProjection(
            project_name=base_projection.project_name,
            projection_start_date=base_projection.projection_start_date,
            total_quarters=base_projection.total_quarters,
            quarterly_revenue=scaled_quarterly,
            cumulative_revenue=scaled_cumulative,
            by_window=scaled_by_window,
            by_market=base_projection.by_market,
            metadata=base_projection.metadata
        )

    def _calculate_percentile(
        self,
        values: List[Decimal],
        percentile: int
    ) -> Decimal:
        """
        Calculate percentile of values.

        Args:
            values: List of values
            percentile: Percentile (0-100)

        Returns:
            Percentile value
        """
        if not values:
            return Decimal("0")

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        index = min(index, len(sorted_values) - 1)

        return sorted_values[index]
