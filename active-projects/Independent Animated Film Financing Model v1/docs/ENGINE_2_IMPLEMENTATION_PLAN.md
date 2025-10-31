# Engine 2: Waterfall Execution Engine with IRR/NPV - Implementation Plan

**Version:** 1.0
**Date:** 2025-10-31
**Status:** Planning Complete → Ready for Implementation

---

## Executive Summary

Engine 2 transforms the base waterfall model (Phase 2A) into a **comprehensive investor analytics engine** that projects multi-year revenue flows, executes waterfalls over time, calculates investor returns (IRR, NPV, cash-on-cash multiples), and simulates revenue uncertainty using Monte Carlo methods.

**Why Engine 2?**
- Investors need to understand returns: IRR, NPV, payback period, cash-on-cash multiple
- Revenue is uncertain and unfolds over 5-7 years across distribution windows
- Waterfall execution must track cumulative recoupment and remaining balances over time
- Scenario analysis helps quantify risk and compare financing structures

**Key Capabilities:**
1. **Multi-Year Revenue Projection** - Model theatrical, home video, streaming, TV windows with 2025-accurate timing
2. **Time-Series Waterfall Execution** - Process revenue flows quarter-by-quarter through waterfall tiers
3. **Stakeholder Return Analytics** - Calculate IRR, NPV, cash-on-cash, payback period for each investor
4. **Monte Carlo Simulation** - 10,000 simulations of revenue outcomes with P10/P50/P90 confidence intervals
5. **Sensitivity Analysis** - Identify which variables drive returns (box office, SVOD license, distribution fees)

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│             Engine 2: Waterfall Execution Engine               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────┐        ┌──────────────────────────┐  │
│  │  RevenueProjector   │───────▶│  RevenueProjection       │  │
│  │  - project()        │        │  - quarterly_revenue{}   │  │
│  │  - windows[]        │        │  - cumulative_revenue{}  │  │
│  │  - market_shares{}  │        │  - by_window_breakdown   │  │
│  └─────────────────────┘        └──────────────────────────┘  │
│           │                                │                   │
│           │                                │                   │
│           ▼                                ▼                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │           WaterfallExecutor (Time-Series)                │ │
│  │  - execute_over_time()                                   │ │
│  │  - process_quarter()                                     │ │
│  │  - track_cumulative_recoupment()                        │ │
│  │  - generate_payout_schedule()                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         StakeholderAnalyzer (Returns Calculator)         │ │
│  │  - calculate_irr()                                       │ │
│  │  - calculate_npv()                                       │ │
│  │  - calculate_cash_on_cash()                             │ │
│  │  - calculate_payback_period()                           │ │
│  │  - generate_investor_summary()                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│           │                                │                   │
│           ▼                                ▼                   │
│  ┌───────────────────┐         ┌──────────────────────────┐  │
│  │ MonteCarloSimulator│         │  SensitivityAnalyzer     │  │
│  │ - simulate()      │         │  - analyze()             │  │
│  │ - distributions{} │         │  - tornado_chart_data()  │  │
│  │ - correlations{}  │         │  - key_drivers()         │  │
│  └───────────────────┘         └──────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
   ┌──────────┐                      ┌────────────────┐
   │ Phase 2A │                      │   Engine 1     │
   │  Models  │                      │ (Incentives)   │
   │Waterfall │                      │    Results     │
   │CapStack  │                      └────────────────┘
   └──────────┘
```

---

## Modern Distribution Windows (2025)

Understanding revenue timing is critical for accurate waterfall execution. The industry has evolved significantly:

### Theatrical Release Strategy
**Wide Release (2,500+ screens):**
- Week 1-2: 45-55% of total theatrical
- Week 3-4: 20-25%
- Week 5-8: 15-20%
- Week 9+: 5-10% (long tail)
- **Total theatrical window:** 8-12 weeks (shortened from historical 16-20 weeks)

**Platform/Limited Release:**
- Slower ramp-up: 4-8 weeks to wide
- Longer tail: 16-24 weeks total
- Lower peak but steadier revenue

### Post-Theatrical Windows (2025 Updated)

| Window | Timing After Theatrical | Duration | % of Total Revenue | Notes |
|--------|------------------------|----------|-------------------|--------|
| **PVOD** | Day-and-date OR 17-31 days | 4-8 weeks | 5-15% | Premium rentals ($19.99) |
| **EST** | 45-60 days | Perpetual | 3-8% | Digital purchase ($14.99-24.99) |
| **SVOD** | 4-6 months | 12-18 months | 30-50% | Netflix/Disney+/etc. flat license |
| **Pay TV** | 12-18 months | 12-24 months | 5-10% | HBO, Showtime (declining) |
| **AVOD/FAST** | 18-30 months | 24-36 months | 5-15% | Ad-supported streaming |
| **Free TV** | 36-60 months | 36+ months | 2-5% | Broadcast (minimal today) |

**Key Changes Since 2020:**
- PVOD now overlaps with theatrical or launches 17 days after (vs 90+ days)
- SVOD is dominant revenue source for family animation (30-50% vs historical 10-15%)
- Physical home video collapsed (DVD/Blu-ray <5% vs historical 30-40%)
- AVOD/FAST growing rapidly (Pluto TV, Tubi, Roku Channel)
- International windows compressed to match domestic

### Revenue Mix Benchmarks (Family Animation, 2025)

**Successful Theatrical ($150M+ global box office):**
- Theatrical: 40-50%
- SVOD: 30-40%
- PVOD/EST: 8-12%
- AVOD/FAST: 5-8%
- Pay TV: 3-5%

**Streaming-First Release:**
- SVOD: 70-80% (upfront license fee)
- Theatrical: 0-10% (limited platform release)
- AVOD/FAST: 10-15%
- EST/PVOD: 5-10%

**Moderate Theatrical ($50-100M global box office):**
- Theatrical: 35-45%
- SVOD: 35-45%
- PVOD/EST: 10-15%
- AVOD/FAST: 5-10%

---

## Component 1: RevenueProjector

**Purpose:** Project revenue over distribution windows with realistic timing and market share assumptions.

**File:** `backend/engines/waterfall_executor/revenue_projector.py`

### Key Classes

```python
@dataclass
class DistributionWindow:
    """Single distribution window definition"""
    window_type: str  # "theatrical", "pvod", "svod", "est", "avod", "pay_tv", "free_tv"
    start_quarter: int  # Quarters from theatrical release (0 = release quarter)
    duration_quarters: int  # How many quarters this window runs
    revenue_percentage: Decimal  # % of total ultimate revenue
    timing_profile: str  # "front_loaded", "even", "back_loaded"
    metadata: Dict[str, Any]  # Deal specifics, license fees, etc.


@dataclass
class MarketRevenue:
    """Revenue for a specific market (territory)"""
    market_name: str  # "North America", "UK", "France", etc.
    total_revenue: Decimal  # Ultimate total for this market
    distribution_windows: List[DistributionWindow]
    release_quarter: int  # Global quarter when this market releases


@dataclass
class RevenueProjection:
    """Complete multi-year revenue projection"""
    project_name: str
    projection_start_date: str  # "2025-Q1"
    total_quarters: int  # Typically 20-28 quarters (5-7 years)

    quarterly_revenue: Dict[int, Decimal]  # Quarter → gross revenue
    cumulative_revenue: Dict[int, Decimal]  # Quarter → cumulative

    by_window: Dict[str, Decimal]  # Window type → total revenue
    by_market: Dict[str, Decimal]  # Market → total revenue

    quarterly_detail: List[Dict[str, Any]]  # Detailed breakdown per quarter

    metadata: Dict[str, Any]  # Assumptions, notes


class RevenueProjector:
    """Project revenue over time with distribution window modeling"""

    def __init__(self):
        """Initialize with default window templates"""
        self.window_templates = self._load_default_templates()

    def project(
        self,
        total_ultimate_revenue: Decimal,
        theatrical_box_office: Decimal,
        svod_license_fee: Optional[Decimal] = None,
        markets: Optional[List[MarketRevenue]] = None,
        release_strategy: str = "wide_theatrical",  # or "platform", "streaming_first"
        custom_windows: Optional[List[DistributionWindow]] = None
    ) -> RevenueProjection:
        """
        Project revenue over distribution windows.

        Args:
            total_ultimate_revenue: Total lifetime revenue estimate
            theatrical_box_office: Theatrical box office (worldwide or domestic)
            svod_license_fee: If known SVOD deal, specify here
            markets: Territory-by-territory breakdown (if available)
            release_strategy: Release pattern affects window timing
            custom_windows: Override default windows

        Logic:
        1. If svod_license_fee provided, it's booked in quarter of SVOD window start
        2. If theatrical_box_office provided, calculate theatrical % and project other windows
        3. Apply timing profiles to distribute revenue within each window
        4. Aggregate across markets if provided
        5. Generate quarter-by-quarter revenue

        Returns:
            RevenueProjection with quarterly detail
        """

    def _load_default_templates(self) -> Dict[str, List[DistributionWindow]]:
        """
        Load default distribution window templates for different strategies.

        Returns:
            Dict mapping strategy → list of windows

        Strategies:
        - "wide_theatrical": Traditional wide release
        - "platform": Limited release expanding
        - "streaming_first": SVOD-led strategy
        - "day_and_date": Theatrical + PVOD simultaneous
        """

    def _apply_timing_profile(
        self,
        window: DistributionWindow,
        total_revenue: Decimal
    ) -> Dict[int, Decimal]:
        """
        Distribute window revenue across quarters based on timing profile.

        Args:
            window: Distribution window definition
            total_revenue: Total revenue for this window

        Returns:
            Dict mapping quarter → revenue for this window

        Timing Profiles:
        - "front_loaded": 60% in Q1, 25% Q2, 10% Q3, 5% Q4
        - "even": Equal distribution across quarters
        - "back_loaded": Growing over time (rare)
        - "lump_sum": 100% in first quarter (SVOD licenses)
        """

    def project_from_comparables(
        self,
        production_budget: Decimal,
        comparable_films: List[Dict[str, Any]],
        adjustment_factors: Optional[Dict[str, Decimal]] = None
    ) -> RevenueProjection:
        """
        Project revenue using comparable film analysis.

        Args:
            production_budget: Budget for this project
            comparable_films: List of comparable film data
            adjustment_factors: Adjustments for quality, IP, talent, etc.

        Logic:
        1. Calculate budget multipliers for comparables
        2. Apply adjustment factors
        3. Generate low/base/high revenue scenarios
        4. Return base case projection

        Returns:
            RevenueProjection based on comparables analysis
        """
```

### Default Window Templates

**Wide Theatrical (2025):**
```python
[
    DistributionWindow("theatrical", start_quarter=0, duration_quarters=2, revenue_percentage=42.0, timing_profile="front_loaded"),
    DistributionWindow("pvod", start_quarter=1, duration_quarters=2, revenue_percentage=10.0, timing_profile="front_loaded"),
    DistributionWindow("est", start_quarter=2, duration_quarters=20, revenue_percentage=6.0, timing_profile="back_loaded"),
    DistributionWindow("svod", start_quarter=2, duration_quarters=6, revenue_percentage=35.0, timing_profile="lump_sum"),
    DistributionWindow("pay_tv", start_quarter=6, duration_quarters=8, revenue_percentage=5.0, timing_profile="even"),
    DistributionWindow("avod", start_quarter=8, duration_quarters=12, revenue_percentage=10.0, timing_profile="even"),
]
```

**Streaming-First (2025):**
```python
[
    DistributionWindow("svod", start_quarter=0, duration_quarters=6, revenue_percentage=75.0, timing_profile="lump_sum"),
    DistributionWindow("theatrical", start_quarter=0, duration_quarters=1, revenue_percentage=5.0, timing_profile="front_loaded"),  # Platform only
    DistributionWindow("avod", start_quarter=6, duration_quarters=12, revenue_percentage=12.0, timing_profile="even"),
    DistributionWindow("est", start_quarter=2, duration_quarters=20, revenue_percentage=8.0, timing_profile="back_loaded"),
]
```

---

## Component 2: WaterfallExecutor

**Purpose:** Execute waterfall over time as revenue flows in, tracking cumulative recoupment and generating payout schedules.

**File:** `backend/engines/waterfall_executor/waterfall_executor.py`

### Key Classes

```python
@dataclass
class QuarterlyWaterfallExecution:
    """Waterfall execution for a single quarter"""
    quarter: int
    gross_receipts: Decimal  # Gross revenue this quarter
    distribution_fees: Decimal
    pa_expenses: Decimal
    remaining_pool: Decimal  # After fees/expenses

    node_payouts: Dict[str, Decimal]  # Node ID → payout this quarter
    payee_payouts: Dict[str, Decimal]  # Payee → total payout this quarter

    cumulative_recouped: Dict[str, Decimal]  # Node ID → cumulative recouped
    cumulative_paid: Dict[str, Decimal]  # Payee → cumulative paid

    unrecouped_balances: Dict[str, Decimal]  # Node ID → remaining to recoup


@dataclass
class TimeSeriesWaterfallResult:
    """Complete waterfall execution over time"""
    project_name: str
    waterfall_structure: 'WaterfallStructure'  # Reference to original
    revenue_projection: RevenueProjection

    quarterly_executions: List[QuarterlyWaterfallExecution]

    total_receipts: Decimal
    total_fees: Decimal
    total_recouped_by_node: Dict[str, Decimal]
    total_paid_by_payee: Dict[str, Decimal]

    final_unrecouped: Dict[str, Decimal]  # What didn't recoup

    metadata: Dict[str, Any]


class WaterfallExecutor:
    """Execute waterfall structure over time-series revenue"""

    def __init__(self, waterfall_structure: 'WaterfallStructure'):
        """
        Initialize with waterfall structure from Phase 2A.

        Args:
            waterfall_structure: WaterfallStructure from backend/models/waterfall.py
        """
        self.waterfall = waterfall_structure

    def execute_over_time(
        self,
        revenue_projection: RevenueProjection,
        distribution_fee_rate: Optional[Decimal] = None
    ) -> TimeSeriesWaterfallResult:
        """
        Execute waterfall quarter-by-quarter.

        Args:
            revenue_projection: Revenue projection from RevenueProjector
            distribution_fee_rate: Override default distribution fee (%)

        Logic:
        1. For each quarter with revenue:
           a. Calculate gross receipts
           b. Deduct distribution fees and P&A expenses
           c. Process remaining pool through waterfall tiers
           d. Track cumulative recoupment per node
           e. Stop paying node when fully recouped
        2. Aggregate results across all quarters
        3. Generate payout schedule showing when each investor gets paid

        Returns:
            TimeSeriesWaterfallResult with quarterly detail
        """

    def process_quarter(
        self,
        quarter: int,
        gross_receipts: Decimal,
        cumulative_state: Dict[str, Decimal]
    ) -> QuarterlyWaterfallExecution:
        """
        Process waterfall for a single quarter.

        Args:
            quarter: Quarter number
            gross_receipts: Gross revenue this quarter
            cumulative_state: Cumulative recoupment state (node_id → amount)

        Returns:
            QuarterlyWaterfallExecution with this quarter's results

        Logic:
        1. Deduct distribution fees and P&A
        2. For each waterfall node in priority order:
           a. Calculate remaining to recoup (target - cumulative)
           b. Pay lesser of (available_pool, remaining_to_recoup)
           c. Update cumulative state
           d. Reduce available_pool
        3. Return results and updated cumulative state
        """

    def generate_payout_schedule(
        self,
        result: TimeSeriesWaterfallResult
    ) -> pd.DataFrame:
        """
        Generate detailed payout schedule for each investor.

        Returns:
            DataFrame with columns:
            - quarter: int
            - date: str (estimated)
            - payee: str
            - amount: Decimal
            - cumulative: Decimal
            - percentage_recouped: Decimal
        """
```

---

## Component 3: StakeholderAnalyzer

**Purpose:** Calculate investor returns (IRR, NPV, cash-on-cash, payback period) from waterfall results.

**File:** `backend/engines/waterfall_executor/stakeholder_analyzer.py`

### Key Classes

```python
@dataclass
class StakeholderCashFlows:
    """Cash flows for a single stakeholder"""
    stakeholder_id: str
    stakeholder_name: str
    stakeholder_type: str  # "equity", "debt", "pre_sale", etc.

    initial_investment: Decimal
    investment_quarter: int

    quarterly_receipts: Dict[int, Decimal]  # Quarter → amount received
    total_receipts: Decimal

    irr: Optional[Decimal]  # Internal Rate of Return (annualized)
    npv: Optional[Decimal]  # Net Present Value at discount rate
    cash_on_cash: Decimal  # Total receipts / initial investment
    payback_quarter: Optional[int]  # Quarter when initial investment recovered
    payback_years: Optional[Decimal]  # Years to payback

    roi_percentage: Decimal  # (Total receipts - investment) / investment * 100


@dataclass
class StakeholderAnalysisResult:
    """Analysis for all stakeholders"""
    project_name: str
    waterfall_result: TimeSeriesWaterfallResult
    capital_stack: Optional['CapitalStack']

    stakeholders: List[StakeholderCashFlows]

    discount_rate: Decimal  # Used for NPV calculations

    summary_statistics: Dict[str, Any]  # Aggregate stats


class StakeholderAnalyzer:
    """Calculate investor returns from waterfall execution"""

    def __init__(
        self,
        capital_stack: 'CapitalStack',
        discount_rate: Decimal = Decimal("0.12")  # 12% default
    ):
        """
        Initialize with capital stack and discount rate.

        Args:
            capital_stack: CapitalStack from Phase 2A models
            discount_rate: Annual discount rate for NPV (e.g., 0.12 = 12%)
        """
        self.capital_stack = capital_stack
        self.discount_rate = discount_rate

    def analyze(
        self,
        waterfall_result: TimeSeriesWaterfallResult,
        investment_timing: Optional[Dict[str, int]] = None
    ) -> StakeholderAnalysisResult:
        """
        Analyze returns for all stakeholders.

        Args:
            waterfall_result: Result from WaterfallExecutor.execute_over_time()
            investment_timing: Optional dict mapping stakeholder → investment quarter
                              (defaults to quarter 0 for all)

        Logic:
        1. For each financial instrument in capital stack:
           a. Map to payee in waterfall
           b. Extract quarterly receipts from waterfall result
           c. Calculate IRR using XIRR (irregular cash flows)
           d. Calculate NPV with quarterly discounting
           e. Calculate cash-on-cash multiple
           f. Find payback quarter
        2. Generate summary statistics (median IRR, % recouped, etc.)

        Returns:
            StakeholderAnalysisResult with detailed returns
        """

    def calculate_irr(
        self,
        cash_flows: List[tuple[int, Decimal]]  # (quarter, amount)
    ) -> Optional[Decimal]:
        """
        Calculate Internal Rate of Return.

        Uses Newton-Raphson method to find discount rate where NPV = 0.

        Args:
            cash_flows: List of (quarter, amount) tuples
                       First entry should be negative (investment)

        Returns:
            Annualized IRR as decimal (e.g., 0.15 = 15%) or None if undefined
        """

    def calculate_npv(
        self,
        cash_flows: List[tuple[int, Decimal]],
        discount_rate: Decimal
    ) -> Decimal:
        """
        Calculate Net Present Value.

        NPV = Σ (CF_t / (1 + r)^t) where t is in years

        Args:
            cash_flows: List of (quarter, amount) tuples
            discount_rate: Annual discount rate

        Returns:
            NPV in currency units
        """

    def calculate_payback_period(
        self,
        initial_investment: Decimal,
        quarterly_receipts: Dict[int, Decimal]
    ) -> tuple[Optional[int], Optional[Decimal]]:
        """
        Calculate payback period (when cumulative receipts = initial investment).

        Returns:
            (payback_quarter, payback_years) or (None, None) if never pays back
        """

    def generate_summary(
        self,
        result: StakeholderAnalysisResult
    ) -> Dict[str, Any]:
        """
        Generate summary statistics across all stakeholders.

        Returns:
            Dict with:
            - total_invested: Decimal
            - total_recouped: Decimal
            - overall_recovery_rate: Decimal (%)
            - median_irr: Decimal
            - median_cash_on_cash: Decimal
            - equity_irr: Decimal (for equity investors)
            - debt_recovery_rate: Decimal (for lenders)
        """
```

### IRR Calculation Method

Modern approach using Newton-Raphson for XIRR with irregular cash flows:

```python
def _irr_newton_raphson(
    cash_flows: List[tuple[int, Decimal]],
    max_iterations: int = 100,
    precision: Decimal = Decimal("0.00001")
) -> Optional[Decimal]:
    """
    Calculate IRR using Newton-Raphson method.

    Solves for r where: NPV(r) = Σ (CF_t / (1+r)^t) = 0

    Derivative: NPV'(r) = Σ (-t * CF_t / (1+r)^(t+1))

    Newton-Raphson iteration: r_new = r_old - NPV(r) / NPV'(r)
    """
    # Convert quarters to years
    cash_flows_years = [(q / Decimal("4"), amt) for q, amt in cash_flows]

    # Initial guess: 10% annual
    r = Decimal("0.10")

    for i in range(max_iterations):
        npv = sum(amt / (1 + r) ** t for t, amt in cash_flows_years)
        npv_prime = sum(-t * amt / (1 + r) ** (t + 1) for t, amt in cash_flows_years)

        if abs(npv_prime) < precision:
            return None  # Can't converge

        r_new = r - (npv / npv_prime)

        if abs(r_new - r) < precision:
            return r_new

        r = r_new

    return None  # Didn't converge
```

---

## Component 4: MonteCarloSimulator

**Purpose:** Run 10,000 simulations of revenue outcomes to quantify uncertainty and generate confidence intervals.

**File:** `backend/engines/waterfall_executor/monte_carlo_simulator.py`

### Key Classes

```python
@dataclass
class RevenueDistribution:
    """Statistical distribution for a revenue variable"""
    variable_name: str
    distribution_type: str  # "normal", "lognormal", "triangular", "uniform"
    parameters: Dict[str, Decimal]  # mean, std, min, max, mode, etc.

    # For triangular: min, mode, max
    # For normal: mean, std
    # For lognormal: mu, sigma


@dataclass
class MonteCarloScenario:
    """Single simulation scenario"""
    scenario_id: int

    total_revenue: Decimal
    theatrical_box_office: Decimal
    svod_license_fee: Decimal

    total_recouped: Decimal
    total_paid_by_payee: Dict[str, Decimal]

    stakeholder_results: Dict[str, Dict[str, Decimal]]  # stakeholder → metrics


@dataclass
class MonteCarloResult:
    """Result of Monte Carlo simulation"""
    num_simulations: int
    scenarios: List[MonteCarloScenario]

    # Percentile analysis (P10, P50, P90)
    revenue_percentiles: Dict[str, Decimal]  # "p10", "p50", "p90"

    stakeholder_percentiles: Dict[str, Dict[str, Decimal]]
    # stakeholder → {"irr_p10": x, "irr_p50": y, "irr_p90": z, ...}

    probability_of_recoupment: Dict[str, Decimal]  # stakeholder → probability

    correlation_matrix: Optional[pd.DataFrame]  # Correlation between variables

    metadata: Dict[str, Any]


class MonteCarloSimulator:
    """Run Monte Carlo simulations of revenue uncertainty"""

    def __init__(
        self,
        waterfall_structure: 'WaterfallStructure',
        capital_stack: 'CapitalStack',
        base_revenue_projection: RevenueProjection
    ):
        """
        Initialize simulator with base case.

        Args:
            waterfall_structure: Waterfall from Phase 2A
            capital_stack: Capital stack from Phase 2A
            base_revenue_projection: Base case projection from RevenueProjector
        """
        self.waterfall = waterfall_structure
        self.capital_stack = capital_stack
        self.base_projection = base_revenue_projection

    def simulate(
        self,
        revenue_distribution: RevenueDistribution,
        num_simulations: int = 10000,
        seed: Optional[int] = None
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation.

        Args:
            revenue_distribution: Distribution for total revenue
            num_simulations: Number of scenarios to run (default 10,000)
            seed: Random seed for reproducibility

        Logic:
        1. Set random seed if provided
        2. For each simulation:
           a. Sample total revenue from distribution
           b. Generate revenue projection (proportionally scaled from base)
           c. Execute waterfall
           d. Calculate stakeholder returns
           e. Store scenario results
        3. Calculate percentiles (P10, P50, P90) for all metrics
        4. Calculate probability of recoupment for each stakeholder
        5. Generate correlation matrix

        Returns:
            MonteCarloResult with percentile analysis
        """

    def simulate_multi_variable(
        self,
        distributions: Dict[str, RevenueDistribution],
        correlations: Optional[Dict[tuple[str, str], Decimal]] = None,
        num_simulations: int = 10000,
        seed: Optional[int] = None
    ) -> MonteCarloResult:
        """
        Run Monte Carlo with multiple correlated variables.

        Args:
            distributions: Dict mapping variable name → distribution
                          Variables: "theatrical_box_office", "svod_license_fee",
                                    "international_revenue", "distribution_fee_rate"
            correlations: Optional correlations between variables
                         E.g., {("theatrical", "international"): 0.7}
            num_simulations: Number of scenarios
            seed: Random seed

        Uses Cholesky decomposition for correlated sampling.

        Returns:
            MonteCarloResult with multi-variable analysis
        """

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
```

### Statistical Distributions

**Triangular Distribution** (Most common for film revenue):
```python
# Min = pessimistic, Mode = base case, Max = optimistic
RevenueDistribution(
    variable_name="total_revenue",
    distribution_type="triangular",
    parameters={
        "min": Decimal("50000000"),   # Pessimistic: $50M
        "mode": Decimal("100000000"),  # Base case: $100M
        "max": Decimal("200000000")    # Optimistic: $200M
    }
)
```

**Lognormal Distribution** (For box office, skewed right):
```python
# Good for modeling box office (can't be negative, long right tail)
RevenueDistribution(
    variable_name="theatrical_box_office",
    distribution_type="lognormal",
    parameters={
        "mu": Decimal("18.42"),  # log(100M)
        "sigma": Decimal("0.5")  # Spread
    }
)
```

---

## Component 5: SensitivityAnalyzer

**Purpose:** Identify which variables have the biggest impact on investor returns (tornado charts).

**File:** `backend/engines/waterfall_executor/sensitivity_analyzer.py`

### Key Classes

```python
@dataclass
class SensitivityVariable:
    """Variable to analyze sensitivity for"""
    variable_name: str
    base_value: Decimal
    low_value: Decimal  # Pessimistic
    high_value: Decimal  # Optimistic
    variable_type: str  # "revenue", "cost", "rate"


@dataclass
class SensitivityResult:
    """Sensitivity analysis for one variable"""
    variable: SensitivityVariable

    base_case: Dict[str, Decimal]  # Metric → value at base
    low_case: Dict[str, Decimal]   # Metric → value at low
    high_case: Dict[str, Decimal]  # Metric → value at high

    delta_low: Dict[str, Decimal]  # base - low
    delta_high: Dict[str, Decimal]  # high - base

    impact_score: Decimal  # Max(|delta_low|, |delta_high|)


@dataclass
class TornadoChartData:
    """Data for tornado chart visualization"""
    target_metric: str  # "equity_irr", "senior_debt_recovery_rate", etc.

    variables: List[str]  # Sorted by impact (descending)
    base_value: Decimal

    low_deltas: List[Decimal]  # Negative deltas
    high_deltas: List[Decimal]  # Positive deltas

    # For plotting
    variable_labels: List[str]
    low_values: List[Decimal]
    high_values: List[Decimal]


class SensitivityAnalyzer:
    """Perform sensitivity analysis to identify key drivers"""

    def __init__(
        self,
        waterfall_structure: 'WaterfallStructure',
        capital_stack: 'CapitalStack',
        base_revenue_projection: RevenueProjection
    ):
        """Initialize with base case structures"""
        self.waterfall = waterfall_structure
        self.capital_stack = capital_stack
        self.base_projection = base_revenue_projection

    def analyze(
        self,
        variables: List[SensitivityVariable],
        target_metrics: List[str]  # ["equity_irr", "senior_debt_recovery"]
    ) -> Dict[str, List[SensitivityResult]]:
        """
        Perform sensitivity analysis.

        Args:
            variables: List of variables to analyze
            target_metrics: Metrics to track (IRR, NPV, recovery rate, etc.)

        Logic:
        1. Run base case to get baseline metrics
        2. For each variable:
           a. Run scenario with low value
           b. Run scenario with high value
           c. Calculate deltas from base case
           d. Compute impact score
        3. Sort results by impact score

        Returns:
            Dict mapping target_metric → sorted list of SensitivityResult
        """

    def generate_tornado_chart_data(
        self,
        sensitivity_results: List[SensitivityResult],
        target_metric: str
    ) -> TornadoChartData:
        """
        Generate data for tornado chart visualization.

        Tornado chart shows horizontal bars for each variable's impact:
        - Left side: Impact when variable is LOW
        - Right side: Impact when variable is HIGH
        - Sorted by total impact (widest bars at top)

        Args:
            sensitivity_results: Results from analyze()
            target_metric: Which metric to visualize

        Returns:
            TornadoChartData ready for plotting
        """

    def identify_key_drivers(
        self,
        sensitivity_results: List[SensitivityResult],
        threshold_impact: Decimal = Decimal("2.0")  # 2% change = significant
    ) -> List[str]:
        """
        Identify variables with significant impact.

        Args:
            sensitivity_results: Results from analyze()
            threshold_impact: Minimum impact score to be considered "key driver"

        Returns:
            List of variable names sorted by impact
        """
```

### Default Sensitivity Variables

```python
DEFAULT_SENSITIVITY_VARIABLES = [
    SensitivityVariable(
        variable_name="theatrical_box_office",
        base_value=Decimal("100000000"),
        low_value=Decimal("70000000"),   # -30%
        high_value=Decimal("130000000")  # +30%
    ),
    SensitivityVariable(
        variable_name="svod_license_fee",
        base_value=Decimal("50000000"),
        low_value=Decimal("40000000"),   # -20%
        high_value=Decimal("60000000")   # +20%
    ),
    SensitivityVariable(
        variable_name="distribution_fee_rate",
        base_value=Decimal("30.0"),      # 30%
        low_value=Decimal("25.0"),       # -5 points
        high_value=Decimal("35.0")       # +5 points
    ),
    SensitivityVariable(
        variable_name="international_revenue",
        base_value=Decimal("80000000"),
        low_value=Decimal("60000000"),   # -25%
        high_value=Decimal("100000000")  # +25%
    ),
]
```

---

## Integration with Existing Components

### With Phase 2A Models

**WaterfallStructure** → Used directly by WaterfallExecutor
```python
from backend.models.waterfall import WaterfallStructure

waterfall = WaterfallStructure(...)
executor = WaterfallExecutor(waterfall)
```

**CapitalStack** → Used by StakeholderAnalyzer to map investments
```python
from backend.models.capital_stack import CapitalStack

capital_stack = CapitalStack(...)
analyzer = StakeholderAnalyzer(capital_stack)
```

### With Engine 1 (Incentive Calculator)

Engine 1 results (incentive net benefits) can be integrated into capital stack:

```python
# From Engine 1
incentive_result = calculator.calculate_multi_jurisdiction(...)

# Add to capital stack as tax credit loan or soft money
tax_credit_loan = TaxCreditLoan(
    amount=incentive_result.total_net_benefits,
    ...
)

capital_stack.add_component(tax_credit_loan)

# Then use in Engine 2
analyzer = StakeholderAnalyzer(capital_stack)
```

---

## Dependencies

### Required
```toml
numpy>=1.26.0          # Numerical operations
scipy>=1.11.0          # Statistical distributions
pandas>=2.1.0          # DataFrames for results
numpy-financial>=1.0.0 # Financial functions (IRR, NPV)
```

### Optional
```toml
matplotlib>=3.8.0      # Tornado charts, distribution plots
plotly>=5.18.0        # Interactive visualizations
```

---

## Test Strategy

### Unit Tests

**test_revenue_projector.py:**
- Test default window templates
- Test timing profile distribution
- Test wide theatrical vs streaming-first strategies
- Test quarterly aggregation
- Test market-by-market projection

**test_waterfall_executor.py:**
- Test quarter-by-quarter execution
- Test cumulative recoupment tracking
- Test node completion (stop paying when recouped)
- Test payout schedule generation
- Test integration with Phase 2A WaterfallStructure

**test_stakeholder_analyzer.py:**
- Test IRR calculation (known cash flows)
- Test NPV calculation
- Test payback period calculation
- Test cash-on-cash multiple
- Test stakeholder mapping from capital stack

**test_monte_carlo_simulator.py:**
- Test triangular distribution sampling
- Test lognormal distribution sampling
- Test percentile calculation (P10, P50, P90)
- Test probability of recoupment
- Test correlation matrix generation
- Test reproducibility with seed

**test_sensitivity_analyzer.py:**
- Test single variable sensitivity
- Test multi-variable sensitivity
- Test tornado chart data generation
- Test key driver identification

### Integration Tests

**test_integration_end_to_end.py:**
- Complete workflow: Revenue Projection → Waterfall Execution → Stakeholder Analysis
- "The Dragon's Quest" scenario with real capital stack
- Monte Carlo simulation with 1,000 runs
- Sensitivity analysis with 5 variables
- Verify IRR calculations match expected
- Verify percentiles are reasonable

### Performance Tests

**test_performance.py:**
- 10,000 Monte Carlo simulations should complete in <60 seconds
- Waterfall execution for 28 quarters should complete in <1 second
- Memory usage should be reasonable (test with 100,000 simulations)

---

## Example Usage Scenarios

### Example 1: Basic Revenue Projection and Waterfall

```python
# 1. Project revenue
projector = RevenueProjector()
revenue_projection = projector.project(
    total_ultimate_revenue=Decimal("150000000"),
    theatrical_box_office=Decimal("60000000"),
    svod_license_fee=Decimal("50000000"),
    release_strategy="wide_theatrical"
)

# 2. Execute waterfall over time
executor = WaterfallExecutor(waterfall_structure)
result = executor.execute_over_time(revenue_projection)

# 3. Analyze stakeholder returns
analyzer = StakeholderAnalyzer(capital_stack, discount_rate=Decimal("0.12"))
stakeholder_analysis = analyzer.analyze(result)

# Print results
for stakeholder in stakeholder_analysis.stakeholders:
    print(f"{stakeholder.stakeholder_name}:")
    print(f"  Investment: ${stakeholder.initial_investment:,.0f}")
    print(f"  Total Receipts: ${stakeholder.total_receipts:,.0f}")
    print(f"  IRR: {stakeholder.irr * 100:.1f}%")
    print(f"  Cash-on-Cash: {stakeholder.cash_on_cash:.2f}x")
    print(f"  Payback: {stakeholder.payback_years:.1f} years")
```

### Example 2: Monte Carlo Simulation

```python
# Define revenue uncertainty
revenue_dist = RevenueDistribution(
    variable_name="total_revenue",
    distribution_type="triangular",
    parameters={
        "min": Decimal("80000000"),    # Pessimistic
        "mode": Decimal("150000000"),  # Base case
        "max": Decimal("250000000")    # Optimistic
    }
)

# Run simulation
simulator = MonteCarloSimulator(waterfall_structure, capital_stack, base_projection)
mc_result = simulator.simulate(revenue_dist, num_simulations=10000, seed=42)

# Print percentile analysis
print("Equity Investor IRR:")
print(f"  P10 (pessimistic): {mc_result.stakeholder_percentiles['equity']['irr_p10'] * 100:.1f}%")
print(f"  P50 (median): {mc_result.stakeholder_percentiles['equity']['irr_p50'] * 100:.1f}%")
print(f"  P90 (optimistic): {mc_result.stakeholder_percentiles['equity']['irr_p90'] * 100:.1f}%")

print(f"\nProbability of full recoupment: {mc_result.probability_of_recoupment['equity'] * 100:.1f}%")
```

### Example 3: Sensitivity Analysis

```python
# Define variables to test
variables = [
    SensitivityVariable("theatrical_box_office", base=Decimal("60000000"),
                       low=Decimal("40000000"), high=Decimal("80000000")),
    SensitivityVariable("svod_license_fee", base=Decimal("50000000"),
                       low=Decimal("40000000"), high=Decimal("60000000")),
    SensitivityVariable("distribution_fee_rate", base=Decimal("30.0"),
                       low=Decimal("25.0"), high=Decimal("35.0")),
]

# Analyze sensitivity
sensitivity_analyzer = SensitivityAnalyzer(waterfall_structure, capital_stack, base_projection)
results = sensitivity_analyzer.analyze(variables, target_metrics=["equity_irr"])

# Generate tornado chart data
tornado_data = sensitivity_analyzer.generate_tornado_chart_data(
    results["equity_irr"],
    "equity_irr"
)

# Identify key drivers
key_drivers = sensitivity_analyzer.identify_key_drivers(results["equity_irr"])
print(f"Key drivers of equity IRR: {', '.join(key_drivers)}")
```

---

## File Structure

```
backend/engines/waterfall_executor/
├── __init__.py
├── revenue_projector.py          # Component 1
├── waterfall_executor.py         # Component 2
├── stakeholder_analyzer.py       # Component 3
├── monte_carlo_simulator.py      # Component 4
├── sensitivity_analyzer.py       # Component 5
├── utils.py                       # Shared utilities
└── tests/
    ├── __init__.py
    ├── test_revenue_projector.py
    ├── test_waterfall_executor.py
    ├── test_stakeholder_analyzer.py
    ├── test_monte_carlo_simulator.py
    ├── test_sensitivity_analyzer.py
    └── test_integration.py

backend/engines/examples/
├── example_revenue_projection_and_waterfall.py
├── example_monte_carlo_simulation.py
├── example_sensitivity_analysis.py
└── example_dragons_quest_complete_analysis.py
```

---

## Success Criteria

Engine 2 is **complete** when:

✅ **Functional Requirements:**
1. Revenue projection generates realistic quarterly revenue over 5-7 years
2. Waterfall execution processes quarterly revenue correctly
3. Cumulative recoupment tracking stops nodes when fully recouped
4. IRR calculations match expected values for known cash flows
5. NPV calculations use proper quarterly discounting
6. Monte Carlo simulations with 10,000 runs complete successfully
7. Percentile analysis (P10, P50, P90) is reasonable
8. Sensitivity analysis identifies correct key drivers
9. Tornado chart data is correctly formatted

✅ **Quality Requirements:**
1. 90%+ test coverage on financial calculations
2. All tests pass
3. Type hints on all public functions
4. Comprehensive docstrings
5. Examples demonstrate all core features

✅ **Integration Requirements:**
1. Works seamlessly with Phase 2A WaterfallStructure and CapitalStack
2. Can integrate Engine 1 incentive results
3. Produces output compatible with Phase 4 API

✅ **Performance Requirements:**
1. 10,000 Monte Carlo simulations in <60 seconds
2. Single waterfall execution in <1 second
3. Memory efficient for large simulations

---

## Timeline Estimate

**Total:** ~8-10 hours for complete implementation + testing

| Component | Estimated Time |
|-----------|---------------|
| RevenueProjector | 2 hours |
| WaterfallExecutor | 2 hours |
| StakeholderAnalyzer (IRR/NPV) | 2 hours |
| MonteCarloSimulator | 2 hours |
| SensitivityAnalyzer | 1.5 hours |
| Unit tests | 2.5 hours |
| Integration tests + examples | 2 hours |
| Documentation | 1 hour |

---

## Next Steps After Engine 2

1. **Engine 3:** Scenario Generator & Optimizer (OR-Tools for optimal capital stack)
2. **Phase 4:** FastAPI + Next.js frontend
3. **Advanced Features:**
   - Currency hedging models
   - Co-production treaty compliance checker
   - Completion bond reserve calculations
   - Collection account waterfall (CAMA) modeling

---

**End of Implementation Plan**

This plan provides a complete roadmap for building Engine 2 with modern 2025 distribution window modeling, sophisticated financial analytics (IRR/NPV), Monte Carlo simulation, and sensitivity analysis.

Ready to proceed with implementation.
