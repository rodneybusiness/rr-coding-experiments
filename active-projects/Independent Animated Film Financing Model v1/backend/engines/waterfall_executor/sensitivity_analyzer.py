"""
Sensitivity Analyzer

Performs sensitivity analysis to identify which variables have the biggest
impact on investor returns (tornado charts).
"""

import logging
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
class SensitivityVariable:
    """
    Variable to analyze sensitivity for.

    Attributes:
        variable_name: Variable identifier
        base_value: Base case value
        low_value: Pessimistic value
        high_value: Optimistic value
        variable_type: Type (revenue, cost, rate)
    """
    variable_name: str
    base_value: Decimal
    low_value: Decimal
    high_value: Decimal
    variable_type: str = "revenue"


@dataclass
class SensitivityResult:
    """
    Sensitivity analysis for one variable.

    Attributes:
        variable: Variable analyzed
        base_case: Metric values at base
        low_case: Metric values at low
        high_case: Metric values at high
        delta_low: base - low
        delta_high: high - base
        impact_score: Max(|delta_low|, |delta_high|)
    """
    variable: SensitivityVariable

    base_case: Dict[str, Decimal]
    low_case: Dict[str, Decimal]
    high_case: Dict[str, Decimal]

    delta_low: Dict[str, Decimal]
    delta_high: Dict[str, Decimal]

    impact_score: Decimal


@dataclass
class TornadoChartData:
    """
    Data for tornado chart visualization.

    Attributes:
        target_metric: Metric being analyzed
        variables: Variable names sorted by impact
        base_value: Base case value
        low_deltas: Negative deltas
        high_deltas: Positive deltas
    """
    target_metric: str
    variables: List[str]
    base_value: Decimal
    low_deltas: List[Decimal]
    high_deltas: List[Decimal]


class SensitivityAnalyzer:
    """
    Perform sensitivity analysis to identify key drivers.

    Tests how changes in input variables affect investor returns to identify
    which variables have the biggest impact.
    """

    def __init__(
        self,
        waterfall_structure: WaterfallStructure,
        capital_stack: CapitalStack,
        base_revenue_projection: RevenueProjection
    ):
        """
        Initialize with base case structures.

        Args:
            waterfall_structure: Waterfall structure
            capital_stack: Capital stack
            base_revenue_projection: Base revenue projection
        """
        self.waterfall = waterfall_structure
        self.capital_stack = capital_stack
        self.base_projection = base_revenue_projection

        logger.info("SensitivityAnalyzer initialized")

    def analyze(
        self,
        variables: List[SensitivityVariable],
        target_metrics: List[str]
    ) -> Dict[str, List[SensitivityResult]]:
        """
        Perform sensitivity analysis.

        Args:
            variables: List of variables to analyze
            target_metrics: Metrics to track (e.g., ["equity_irr"])

        Returns:
            Dict mapping target_metric → sorted list of SensitivityResult
        """
        results_by_metric: Dict[str, List[SensitivityResult]] = {
            metric: [] for metric in target_metrics
        }

        # Run base case
        base_metrics = self._run_scenario(self.base_projection)

        # Analyze each variable
        for variable in variables:
            # Run low case
            low_projection = self._adjust_projection(
                self.base_projection,
                variable.variable_name,
                variable.low_value
            )
            low_metrics = self._run_scenario(low_projection)

            # Run high case
            high_projection = self._adjust_projection(
                self.base_projection,
                variable.variable_name,
                variable.high_value
            )
            high_metrics = self._run_scenario(high_projection)

            # Calculate deltas for each target metric
            for metric in target_metrics:
                base_val = base_metrics.get(metric, Decimal("0"))
                low_val = low_metrics.get(metric, Decimal("0"))
                high_val = high_metrics.get(metric, Decimal("0"))

                delta_low = base_val - low_val
                delta_high = high_val - base_val

                impact_score = max(abs(delta_low), abs(delta_high))

                result = SensitivityResult(
                    variable=variable,
                    base_case={metric: base_val},
                    low_case={metric: low_val},
                    high_case={metric: high_val},
                    delta_low={metric: delta_low},
                    delta_high={metric: delta_high},
                    impact_score=impact_score
                )

                results_by_metric[metric].append(result)

        # Sort by impact score (descending)
        for metric in target_metrics:
            results_by_metric[metric].sort(key=lambda r: r.impact_score, reverse=True)

        logger.info(f"Sensitivity analysis complete for {len(variables)} variables")

        return results_by_metric

    def generate_tornado_chart_data(
        self,
        sensitivity_results: List[SensitivityResult],
        target_metric: str
    ) -> TornadoChartData:
        """
        Generate data for tornado chart visualization.

        Args:
            sensitivity_results: Results from analyze()
            target_metric: Which metric to visualize

        Returns:
            TornadoChartData ready for plotting
        """
        variables = [r.variable.variable_name for r in sensitivity_results]

        base_value = sensitivity_results[0].base_case[target_metric] if sensitivity_results else Decimal("0")

        low_deltas = [-r.delta_low[target_metric] for r in sensitivity_results]
        high_deltas = [r.delta_high[target_metric] for r in sensitivity_results]

        return TornadoChartData(
            target_metric=target_metric,
            variables=variables,
            base_value=base_value,
            low_deltas=low_deltas,
            high_deltas=high_deltas
        )

    def _run_scenario(self, projection: RevenueProjection) -> Dict[str, Decimal]:
        """
        Run scenario and extract key metrics.

        Args:
            projection: Revenue projection

        Returns:
            Dict of metrics
        """
        # Execute waterfall
        executor = WaterfallExecutor(self.waterfall)
        waterfall_result = executor.execute_over_time(projection)

        # Analyze stakeholders
        analyzer = StakeholderAnalyzer(self.capital_stack)
        stakeholder_analysis = analyzer.analyze(waterfall_result)

        # Extract metrics
        metrics = {}

        # Equity IRR
        equity_stakeholders = [
            s for s in stakeholder_analysis.stakeholders
            if "equity" in s.stakeholder_type.lower()
        ]
        if equity_stakeholders:
            equity_irrs = [s.irr for s in equity_stakeholders if s.irr is not None]
            if equity_irrs:
                metrics["equity_irr"] = sum(equity_irrs) / Decimal(str(len(equity_irrs)))

        # Overall recovery rate
        total_invested = sum(s.initial_investment for s in stakeholder_analysis.stakeholders)
        total_recouped = sum(s.total_receipts for s in stakeholder_analysis.stakeholders)
        if total_invested > 0:
            metrics["overall_recovery_rate"] = (total_recouped / total_invested) * Decimal("100")

        return metrics

    def _adjust_projection(
        self,
        base_projection: RevenueProjection,
        variable_name: str,
        value: Decimal
    ) -> RevenueProjection:
        """
        Adjust projection based on variable change.

        Args:
            base_projection: Base projection
            variable_name: Variable to adjust
            value: New value

        Returns:
            Adjusted RevenueProjection
        """
        # For revenue variables, scale the projection
        if "revenue" in variable_name.lower() or "box_office" in variable_name.lower():
            base_value = Decimal(base_projection.metadata.get("total_ultimate_revenue", "1"))
            if base_value > 0:
                scale_factor = value / base_value
            else:
                scale_factor = Decimal("1")

            # Scale all revenue
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

        # For other variables, return base (would need more sophisticated handling)
        return base_projection
