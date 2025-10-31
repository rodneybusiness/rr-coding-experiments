"""
Engine 2: Waterfall Execution Engine with IRR/NPV

This module provides comprehensive investor analytics capabilities:
- Multi-year revenue projection with 2025-accurate distribution windows
- Time-series waterfall execution tracking cumulative recoupment
- Stakeholder return calculations (IRR, NPV, cash-on-cash, payback)
- Monte Carlo simulation of revenue uncertainty
- Sensitivity analysis to identify key drivers
"""

from backend.engines.waterfall_executor.revenue_projector import (
    RevenueProjector,
    DistributionWindow,
    MarketRevenue,
    RevenueProjection,
)
from backend.engines.waterfall_executor.waterfall_executor import (
    WaterfallExecutor,
    QuarterlyWaterfallExecution,
    TimeSeriesWaterfallResult,
)
from backend.engines.waterfall_executor.stakeholder_analyzer import (
    StakeholderAnalyzer,
    StakeholderCashFlows,
    StakeholderAnalysisResult,
)
from backend.engines.waterfall_executor.monte_carlo_simulator import (
    MonteCarloSimulator,
    RevenueDistribution,
    MonteCarloScenario,
    MonteCarloResult,
)
from backend.engines.waterfall_executor.sensitivity_analyzer import (
    SensitivityAnalyzer,
    SensitivityVariable,
    SensitivityResult,
    TornadoChartData,
)

__all__ = [
    # Revenue projection
    "RevenueProjector",
    "DistributionWindow",
    "MarketRevenue",
    "RevenueProjection",
    # Waterfall execution
    "WaterfallExecutor",
    "QuarterlyWaterfallExecution",
    "TimeSeriesWaterfallResult",
    # Stakeholder analysis
    "StakeholderAnalyzer",
    "StakeholderCashFlows",
    "StakeholderAnalysisResult",
    # Monte Carlo simulation
    "MonteCarloSimulator",
    "RevenueDistribution",
    "MonteCarloScenario",
    "MonteCarloResult",
    # Sensitivity analysis
    "SensitivityAnalyzer",
    "SensitivityVariable",
    "SensitivityResult",
    "TornadoChartData",
]

__version__ = "1.0.0"
