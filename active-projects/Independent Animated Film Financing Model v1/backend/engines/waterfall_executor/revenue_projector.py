"""
Revenue Projector

Projects film revenue over multi-year distribution windows with 2025-accurate
timing for theatrical, PVOD, EST, SVOD, AVOD, and TV windows.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class DistributionWindow:
    """
    Single distribution window definition.

    Represents one revenue stream (theatrical, SVOD, etc.) with timing
    and revenue allocation.

    Attributes:
        window_type: Type of window (theatrical, pvod, svod, est, avod, pay_tv, free_tv)
        start_quarter: Quarters from theatrical release (0 = release quarter)
        duration_quarters: How many quarters this window runs
        revenue_percentage: % of total ultimate revenue from this window
        timing_profile: How revenue is distributed within window
        metadata: Additional window-specific data
    """
    window_type: str
    start_quarter: int
    duration_quarters: int
    revenue_percentage: Decimal
    timing_profile: str = "front_loaded"  # front_loaded, even, back_loaded, lump_sum
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and convert types"""
        if not isinstance(self.revenue_percentage, Decimal):
            self.revenue_percentage = Decimal(str(self.revenue_percentage))

        if self.start_quarter < 0:
            raise ValueError("start_quarter must be >= 0")
        if self.duration_quarters <= 0:
            raise ValueError("duration_quarters must be > 0")
        if self.revenue_percentage < 0 or self.revenue_percentage > 100:
            raise ValueError("revenue_percentage must be 0-100")


@dataclass
class MarketRevenue:
    """
    Revenue for a specific market (territory).

    Attributes:
        market_name: Market identifier (e.g., "North America", "UK", "France")
        total_revenue: Ultimate total revenue for this market
        distribution_windows: List of windows for this market
        release_quarter: Global quarter when this market releases
    """
    market_name: str
    total_revenue: Decimal
    distribution_windows: List[DistributionWindow]
    release_quarter: int = 0

    def __post_init__(self):
        """Validate and convert types"""
        if not isinstance(self.total_revenue, Decimal):
            self.total_revenue = Decimal(str(self.total_revenue))


@dataclass
class RevenueProjection:
    """
    Complete multi-year revenue projection.

    Attributes:
        project_name: Project identifier
        projection_start_date: Start date (e.g., "2025-Q1")
        total_quarters: Total quarters in projection (typically 20-28)
        quarterly_revenue: Quarter → gross revenue
        cumulative_revenue: Quarter → cumulative total
        by_window: Window type → total revenue
        by_market: Market → total revenue
        quarterly_detail: Detailed breakdown per quarter
        metadata: Projection assumptions and notes
    """
    project_name: str
    projection_start_date: str
    total_quarters: int

    quarterly_revenue: Dict[int, Decimal]
    cumulative_revenue: Dict[int, Decimal]

    by_window: Dict[str, Decimal]
    by_market: Dict[str, Decimal]

    quarterly_detail: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_name": self.project_name,
            "projection_start_date": self.projection_start_date,
            "total_quarters": self.total_quarters,
            "quarterly_revenue": {k: str(v) for k, v in self.quarterly_revenue.items()},
            "cumulative_revenue": {k: str(v) for k, v in self.cumulative_revenue.items()},
            "by_window": {k: str(v) for k, v in self.by_window.items()},
            "by_market": {k: str(v) for k, v in self.by_market.items()},
            "quarterly_detail": self.quarterly_detail,
            "metadata": self.metadata
        }


class RevenueProjector:
    """
    Project revenue over distribution windows.

    Models revenue timing using 2025-accurate distribution windows for
    theatrical, streaming, and TV releases.
    """

    def __init__(self):
        """Initialize with default window templates"""
        self.window_templates = self._load_default_templates()
        logger.info("RevenueProjector initialized with 2025 window templates")

    def project(
        self,
        total_ultimate_revenue: Decimal,
        theatrical_box_office: Optional[Decimal] = None,
        svod_license_fee: Optional[Decimal] = None,
        markets: Optional[List[MarketRevenue]] = None,
        release_strategy: str = "wide_theatrical",
        custom_windows: Optional[List[DistributionWindow]] = None,
        project_name: str = "Untitled Project"
    ) -> RevenueProjection:
        """
        Project revenue over distribution windows.

        Args:
            total_ultimate_revenue: Total lifetime revenue estimate
            theatrical_box_office: Theatrical box office (if known)
            svod_license_fee: SVOD license fee (if known)
            markets: Territory-by-territory breakdown (if available)
            release_strategy: Release pattern (wide_theatrical, platform, streaming_first, day_and_date)
            custom_windows: Override default windows
            project_name: Project identifier

        Returns:
            RevenueProjection with quarterly detail
        """
        if not isinstance(total_ultimate_revenue, Decimal):
            total_ultimate_revenue = Decimal(str(total_ultimate_revenue))

        # Use custom windows or template
        if custom_windows:
            windows = custom_windows
        else:
            windows = self.window_templates.get(release_strategy, self.window_templates["wide_theatrical"])

        # Adjust windows based on known values
        if theatrical_box_office:
            windows = self._adjust_for_theatrical(windows, theatrical_box_office, total_ultimate_revenue)

        if svod_license_fee:
            windows = self._adjust_for_svod(windows, svod_license_fee, total_ultimate_revenue)

        # Project quarter-by-quarter
        quarterly_revenue: Dict[int, Decimal] = {}
        by_window: Dict[str, Decimal] = {}

        for window in windows:
            window_total = total_ultimate_revenue * (window.revenue_percentage / Decimal("100"))
            by_window[window.window_type] = by_window.get(window.window_type, Decimal("0")) + window_total

            # Distribute across quarters
            quarterly_distribution = self._apply_timing_profile(window, window_total)

            for quarter, amount in quarterly_distribution.items():
                quarterly_revenue[quarter] = quarterly_revenue.get(quarter, Decimal("0")) + amount

        # Calculate cumulative
        cumulative_revenue: Dict[int, Decimal] = {}
        cumulative = Decimal("0")
        max_quarter = max(quarterly_revenue.keys()) if quarterly_revenue else 0

        for q in range(max_quarter + 1):
            cumulative += quarterly_revenue.get(q, Decimal("0"))
            cumulative_revenue[q] = cumulative

        # Generate detailed breakdown
        quarterly_detail = []
        for q in sorted(quarterly_revenue.keys()):
            detail = {
                "quarter": q,
                "revenue": str(quarterly_revenue[q]),
                "cumulative": str(cumulative_revenue[q]),
                "windows_active": [
                    w.window_type for w in windows
                    if w.start_quarter <= q < w.start_quarter + w.duration_quarters
                ]
            }
            quarterly_detail.append(detail)

        # Market breakdown (if provided)
        by_market = {}
        if markets:
            for market in markets:
                by_market[market.market_name] = market.total_revenue

        projection = RevenueProjection(
            project_name=project_name,
            projection_start_date="2025-Q1",  # Default
            total_quarters=max_quarter + 1 if quarterly_revenue else 0,
            quarterly_revenue=quarterly_revenue,
            cumulative_revenue=cumulative_revenue,
            by_window=by_window,
            by_market=by_market,
            quarterly_detail=quarterly_detail,
            metadata={
                "total_ultimate_revenue": str(total_ultimate_revenue),
                "release_strategy": release_strategy,
                "theatrical_box_office": str(theatrical_box_office) if theatrical_box_office else None,
                "svod_license_fee": str(svod_license_fee) if svod_license_fee else None
            }
        )

        logger.info(
            f"Projected revenue for '{project_name}': {len(windows)} windows, "
            f"{projection.total_quarters} quarters, ${total_ultimate_revenue:,.0f} total"
        )

        return projection

    def _load_default_templates(self) -> Dict[str, List[DistributionWindow]]:
        """
        Load default 2025 distribution window templates.

        Returns:
            Dict mapping strategy → list of windows
        """
        templates = {
            "wide_theatrical": [
                DistributionWindow("theatrical", 0, 2, Decimal("42.0"), "front_loaded",
                                  {"notes": "Wide release 2,500+ screens"}),
                DistributionWindow("pvod", 1, 2, Decimal("10.0"), "front_loaded",
                                  {"notes": "PVOD at 17-31 days, $19.99"}),
                DistributionWindow("est", 2, 20, Decimal("6.0"), "back_loaded",
                                  {"notes": "EST at 45-60 days, $14.99-24.99"}),
                DistributionWindow("svod", 2, 6, Decimal("35.0"), "lump_sum",
                                  {"notes": "SVOD at 4-6 months, flat license"}),
                DistributionWindow("pay_tv", 6, 8, Decimal("4.0"), "even",
                                  {"notes": "Pay TV at 12-18 months"}),
                DistributionWindow("avod", 8, 12, Decimal("8.0"), "even",
                                  {"notes": "AVOD/FAST at 18-30 months"}),
            ],

            "platform": [
                DistributionWindow("theatrical", 0, 4, Decimal("38.0"), "even",
                                  {"notes": "Limited release expanding"}),
                DistributionWindow("pvod", 2, 3, Decimal("12.0"), "front_loaded",
                                  {"notes": "PVOD after platform expansion"}),
                DistributionWindow("est", 3, 20, Decimal("7.0"), "back_loaded",
                                  {"notes": "EST digital purchase"}),
                DistributionWindow("svod", 3, 6, Decimal("35.0"), "lump_sum",
                                  {"notes": "SVOD flat license"}),
                DistributionWindow("pay_tv", 7, 8, Decimal("5.0"), "even",
                                  {"notes": "Pay TV"}),
                DistributionWindow("avod", 9, 12, Decimal("9.0"), "even",
                                  {"notes": "AVOD/FAST"}),
            ],

            "streaming_first": [
                DistributionWindow("svod", 0, 6, Decimal("75.0"), "lump_sum",
                                  {"notes": "SVOD exclusive window"}),
                DistributionWindow("theatrical", 0, 1, Decimal("5.0"), "front_loaded",
                                  {"notes": "Limited theatrical for awards"}),
                DistributionWindow("avod", 6, 12, Decimal("12.0"), "even",
                                  {"notes": "AVOD after SVOD window"}),
                DistributionWindow("est", 2, 20, Decimal("8.0"), "back_loaded",
                                  {"notes": "EST alongside SVOD"}),
            ],

            "day_and_date": [
                DistributionWindow("theatrical", 0, 2, Decimal("25.0"), "front_loaded",
                                  {"notes": "Theatrical + PVOD simultaneous"}),
                DistributionWindow("pvod", 0, 3, Decimal("20.0"), "front_loaded",
                                  {"notes": "PVOD day-and-date"}),
                DistributionWindow("est", 2, 20, Decimal("8.0"), "back_loaded",
                                  {"notes": "EST"}),
                DistributionWindow("svod", 3, 6, Decimal("40.0"), "lump_sum",
                                  {"notes": "SVOD after 3 months"}),
                DistributionWindow("avod", 9, 12, Decimal("10.0"), "even",
                                  {"notes": "AVOD"}),
            ]
        }

        return templates

    def _apply_timing_profile(
        self,
        window: DistributionWindow,
        total_revenue: Decimal
    ) -> Dict[int, Decimal]:
        """
        Distribute window revenue across quarters based on timing profile.

        Args:
            window: Distribution window
            total_revenue: Total revenue for this window

        Returns:
            Dict mapping quarter → revenue
        """
        quarterly_distribution: Dict[int, Decimal] = {}

        if window.timing_profile == "lump_sum":
            # 100% in first quarter
            quarterly_distribution[window.start_quarter] = total_revenue

        elif window.timing_profile == "front_loaded":
            # Theatrical and PVOD: heavy first quarters
            # 60% Q1, 25% Q2, 10% Q3, 5% Q4
            weights = [Decimal("0.60"), Decimal("0.25"), Decimal("0.10"), Decimal("0.05")]
            for i in range(window.duration_quarters):
                if i < len(weights):
                    weight = weights[i]
                else:
                    weight = Decimal("0")

                quarter = window.start_quarter + i
                quarterly_distribution[quarter] = total_revenue * weight

        elif window.timing_profile == "even":
            # Equal distribution across quarters
            per_quarter = total_revenue / Decimal(str(window.duration_quarters))
            for i in range(window.duration_quarters):
                quarter = window.start_quarter + i
                quarterly_distribution[quarter] = per_quarter

        elif window.timing_profile == "back_loaded":
            # EST: grows over time
            # Linear ramp: Q1 gets 1x, Q2 gets 2x, Q3 gets 3x, etc.
            total_weight = sum(i + 1 for i in range(window.duration_quarters))
            for i in range(window.duration_quarters):
                weight = Decimal(str(i + 1)) / Decimal(str(total_weight))
                quarter = window.start_quarter + i
                quarterly_distribution[quarter] = total_revenue * weight

        return quarterly_distribution

    def _adjust_for_theatrical(
        self,
        windows: List[DistributionWindow],
        theatrical_box_office: Decimal,
        total_ultimate: Decimal
    ) -> List[DistributionWindow]:
        """
        Adjust window percentages if theatrical box office is known.

        Args:
            windows: Original windows
            theatrical_box_office: Known theatrical box office
            total_ultimate: Total ultimate revenue

        Returns:
            Adjusted windows
        """
        if not isinstance(theatrical_box_office, Decimal):
            theatrical_box_office = Decimal(str(theatrical_box_office))

        # Calculate actual theatrical percentage
        actual_theatrical_pct = (theatrical_box_office / total_ultimate) * Decimal("100")

        # Adjust windows
        adjusted = []
        for window in windows:
            if window.window_type == "theatrical":
                # Use actual theatrical percentage
                adjusted_window = DistributionWindow(
                    window.window_type,
                    window.start_quarter,
                    window.duration_quarters,
                    actual_theatrical_pct,
                    window.timing_profile,
                    window.metadata
                )
                adjusted.append(adjusted_window)
            else:
                adjusted.append(window)

        return adjusted

    def _adjust_for_svod(
        self,
        windows: List[DistributionWindow],
        svod_license_fee: Decimal,
        total_ultimate: Decimal
    ) -> List[DistributionWindow]:
        """
        Adjust window percentages if SVOD license fee is known.

        Args:
            windows: Original windows
            svod_license_fee: Known SVOD license fee
            total_ultimate: Total ultimate revenue

        Returns:
            Adjusted windows
        """
        if not isinstance(svod_license_fee, Decimal):
            svod_license_fee = Decimal(str(svod_license_fee))

        # Calculate actual SVOD percentage
        actual_svod_pct = (svod_license_fee / total_ultimate) * Decimal("100")

        # Adjust windows
        adjusted = []
        for window in windows:
            if window.window_type == "svod":
                # Use actual SVOD percentage
                adjusted_window = DistributionWindow(
                    window.window_type,
                    window.start_quarter,
                    window.duration_quarters,
                    actual_svod_pct,
                    window.timing_profile,
                    window.metadata
                )
                adjusted.append(adjusted_window)
            else:
                adjusted.append(window)

        return adjusted
