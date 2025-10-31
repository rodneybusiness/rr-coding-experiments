# Engine 1: Enhanced Incentive Calculator - Implementation Plan

**Version:** 1.0
**Date:** 2025-10-31
**Status:** Planning Complete → Ready for Implementation

---

## Executive Summary

Engine 1 is the **foundational calculation engine** for the Animation Film Financing Navigator. It transforms our curated real-world tax incentive data into actionable financial intelligence by:

1. **Loading & validating** 15+ tax incentive policies from JSON → Pydantic models
2. **Calculating net benefits** for single and multi-jurisdiction production scenarios
3. **Handling stacking logic** (Quebec+Federal, Australia PDV+Location, etc.)
4. **Projecting cash flow timelines** with month-by-month visibility
5. **Comparing monetization strategies** (direct cash vs. loan/transfer vs. offset)

**Why Engine 1 First?**
- Engines 2 & 3 depend on it
- Directly leverages our 15 curated policies
- Provides immediate standalone value
- Foundation for API endpoints (Phase 4)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Engine 1: Incentive Calculator           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────────────┐   │
│  │  PolicyLoader    │─────▶│  PolicyRegistry          │   │
│  │  - load_policy() │      │  - get_by_id()          │   │
│  │  - load_all()    │      │  - get_by_jurisdiction()│   │
│  │  - validate()    │      │  - search()             │   │
│  └──────────────────┘      └──────────────────────────┘   │
│          │                            │                     │
│          ▼                            ▼                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        IncentiveCalculator (Core Engine)             │  │
│  │  - calculate_single_jurisdiction()                   │  │
│  │  - calculate_multi_jurisdiction()                    │  │
│  │  - apply_stacking_rules()                           │  │
│  │  - calculate_net_benefit()                          │  │
│  └──────────────────────────────────────────────────────┘  │
│          │                            │                     │
│          ▼                            ▼                     │
│  ┌──────────────────┐      ┌──────────────────────────┐   │
│  │ CashFlowProjector│      │ MonetizationComparator   │   │
│  │ - project()      │      │ - compare_strategies()   │   │
│  │ - monthly_view() │      │ - optimal_strategy()     │   │
│  └──────────────────┘      └──────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
   ┌──────────┐                      ┌────────────────┐
   │ Pydantic │                      │  JSON Policy   │
   │  Models  │                      │     Files      │
   │ (Phase2A)│                      │   (Phase 3)    │
   └──────────┘                      └────────────────┘
```

---

## Component Breakdown

### 1. PolicyLoader

**Purpose:** Load tax incentive policy JSON files into validated `IncentivePolicy` Pydantic objects.

**File:** `backend/engines/incentive_calculator/policy_loader.py`

**Key Functions:**

```python
class PolicyLoader:
    """Loads and validates tax incentive policies from JSON files"""

    def __init__(self, policies_dir: Path):
        """Initialize loader with path to policies directory"""

    def load_policy(self, policy_id: str) -> IncentivePolicy:
        """
        Load a single policy by ID.

        Args:
            policy_id: Policy identifier (e.g., "UK-AVEC-2025")

        Returns:
            Validated IncentivePolicy object

        Raises:
            FileNotFoundError: If policy file doesn't exist
            ValidationError: If policy data is invalid
        """

    def load_all(self) -> List[IncentivePolicy]:
        """
        Load all policies from the policies directory.

        Returns:
            List of validated IncentivePolicy objects
        """

    def load_by_jurisdiction(self, jurisdiction: str) -> List[IncentivePolicy]:
        """
        Load all policies for a specific jurisdiction.

        Args:
            jurisdiction: Country or region name (e.g., "Canada", "United Kingdom")

        Returns:
            List of IncentivePolicy objects for that jurisdiction
        """

    def validate_policies_dir(self) -> Dict[str, Any]:
        """
        Validate all policy files in directory.

        Returns:
            Dict with validation summary:
            {
                "total_files": int,
                "valid": int,
                "invalid": int,
                "errors": List[Dict]
            }
        """
```

**Data Flow:**
1. Read JSON file from `backend/data/policies/`
2. Parse JSON → dict
3. Pass to `IncentivePolicy(**data)` for Pydantic validation
4. Return validated object or raise detailed error

**Error Handling:**
- File not found → Clear error with expected path
- Invalid JSON → JSON parsing error with line number
- Schema validation failure → Pydantic ValidationError with field details
- All errors logged with context

---

### 2. PolicyRegistry

**Purpose:** In-memory registry for fast policy lookup and search.

**File:** `backend/engines/incentive_calculator/policy_registry.py`

**Key Functions:**

```python
class PolicyRegistry:
    """Registry for managing loaded policies with fast lookup"""

    def __init__(self, loader: PolicyLoader):
        """Initialize with PolicyLoader and load all policies"""

    def get_by_id(self, policy_id: str) -> Optional[IncentivePolicy]:
        """Retrieve policy by ID"""

    def get_by_jurisdiction(self, jurisdiction: str) -> List[IncentivePolicy]:
        """Retrieve all policies for a jurisdiction"""

    def search(
        self,
        incentive_type: Optional[IncentiveType] = None,
        min_rate: Optional[Decimal] = None,
        max_rate: Optional[Decimal] = None,
        monetization_method: Optional[MonetizationMethod] = None,
        requires_cultural_test: Optional[bool] = None
    ) -> List[IncentivePolicy]:
        """
        Search policies by criteria.

        Returns policies matching ALL provided criteria (AND logic).
        """

    def get_stackable_policies(
        self,
        jurisdiction: Optional[str] = None
    ) -> Dict[str, List[IncentivePolicy]]:
        """
        Identify stackable policy combinations.

        Returns:
            Dict mapping jurisdiction/program to list of stackable policies
            Example: {
                "Canada-Quebec": [CPTC, PSTC],
                "Australia": [Producer-Offset, PDV-Offset]
            }
        """

    def get_all(self) -> List[IncentivePolicy]:
        """Return all loaded policies"""

    def reload(self):
        """Reload all policies from disk"""
```

**Data Structures:**
- `_policies_by_id: Dict[str, IncentivePolicy]` - O(1) lookup
- `_policies_by_jurisdiction: Dict[str, List[IncentivePolicy]]` - Grouped by country
- `_all_policies: List[IncentivePolicy]` - Complete list

---

### 3. IncentiveCalculator (Core Engine)

**Purpose:** Calculate net incentive benefits for single and multi-jurisdiction scenarios.

**File:** `backend/engines/incentive_calculator/calculator.py`

**Key Classes & Functions:**

```python
@dataclass
class JurisdictionSpend:
    """Spending allocation for a single jurisdiction"""
    jurisdiction: str
    policy_ids: List[str]  # Policies to apply (for stacking)
    qualified_spend: Decimal
    total_spend: Decimal  # Includes non-qualified
    labor_spend: Decimal  # For labor-specific credits
    goods_services_spend: Decimal
    post_production_spend: Decimal
    vfx_animation_spend: Decimal


@dataclass
class IncentiveResult:
    """Result of incentive calculation for one policy"""
    policy_id: str
    jurisdiction: str
    policy_name: str
    qualified_spend: Decimal
    gross_credit: Decimal
    transfer_discount: Optional[Decimal]
    discount_amount: Decimal
    tax_cost: Decimal
    audit_cost: Decimal
    application_fee: Decimal
    net_cash_benefit: Decimal
    effective_rate: Decimal  # Net benefit / qualified spend
    monetization_method: MonetizationMethod
    timing_months: int  # Total months to cash receipt
    warnings: List[str]  # Validation warnings (e.g., below minimum spend)


@dataclass
class MultiJurisdictionResult:
    """Result of multi-jurisdiction calculation"""
    total_budget: Decimal
    total_qualified_spend: Decimal
    jurisdiction_results: List[IncentiveResult]
    total_gross_credits: Decimal
    total_net_benefits: Decimal
    blended_effective_rate: Decimal  # Total net / total qualified
    stacking_applied: List[str]  # Which stacking combinations were used
    total_timing_weighted_months: Decimal  # Weighted by benefit size


class IncentiveCalculator:
    """Core incentive calculation engine"""

    def __init__(self, registry: PolicyRegistry):
        """Initialize with policy registry"""

    def calculate_single_jurisdiction(
        self,
        policy_id: str,
        jurisdiction_spend: JurisdictionSpend,
        monetization_method: MonetizationMethod,
        transfer_discount: Optional[Decimal] = None
    ) -> IncentiveResult:
        """
        Calculate incentive for a single policy.

        Uses IncentivePolicy.calculate_net_benefit() method with additional
        validation and business logic.

        Validation:
        - Check minimum spend requirements
        - Validate per-project cap not exceeded
        - Check cultural test requirements (warning if needed)
        - Validate monetization method is supported

        Returns:
            IncentiveResult with full breakdown
        """

    def calculate_multi_jurisdiction(
        self,
        total_budget: Decimal,
        jurisdiction_spends: List[JurisdictionSpend],
        monetization_preferences: Dict[str, MonetizationMethod]
    ) -> MultiJurisdictionResult:
        """
        Calculate incentives across multiple jurisdictions.

        Handles:
        1. Calculate each jurisdiction separately
        2. Apply stacking rules where applicable
        3. Aggregate results
        4. Calculate blended effective rate

        Args:
            total_budget: Total production budget
            jurisdiction_spends: List of spending allocations
            monetization_preferences: Dict mapping policy_id to preferred method

        Returns:
            MultiJurisdictionResult with aggregated data
        """

    def apply_stacking_rules(
        self,
        jurisdiction: str,
        policy_results: List[IncentiveResult]
    ) -> List[IncentiveResult]:
        """
        Apply stacking rules for jurisdictions with multiple policies.

        Known stacking scenarios:
        - Canada: Federal CPTC + Provincial (Quebec/Ontario)
        - Australia: Producer Offset + PDV Offset (if criteria met)

        Logic:
        - Validate stacking is allowed (different bases, non-overlapping)
        - Ensure combined benefits don't exceed budget caps
        - Apply any special stacking rules from policy notes

        Returns:
            Adjusted IncentiveResult list with stacking applied
        """

    def validate_cultural_test_requirements(
        self,
        policy: IncentivePolicy,
        project_profile: Optional[ProjectProfile] = None
    ) -> Dict[str, Any]:
        """
        Check if project would pass cultural test.

        If project_profile provided, can attempt to score it.
        Otherwise, returns requirements and warning.

        Returns:
            {
                "requires_test": bool,
                "test_name": str,
                "likely_passes": Optional[bool],
                "notes": str
            }
        """
```

**Calculation Logic:**

1. **Single Jurisdiction:**
   - Validate policy exists
   - Check minimum spend thresholds
   - Call `policy.calculate_net_benefit()`
   - Add audit costs, application fees
   - Calculate total timing (audit + certification + cash)
   - Generate warnings for cultural tests, SPV requirements, etc.

2. **Multi-Jurisdiction:**
   - Process each jurisdiction separately
   - Identify stacking opportunities
   - Validate total spend = sum of jurisdiction spends
   - Calculate weighted averages for timing
   - Flag any conflicts or warnings

3. **Stacking Rules:**
   - Federal + Provincial (Canada): OK - different bases
   - Producer Offset + PDV Offset (Australia): OK if spend qualifies for both
   - National + Regional (Spain, France): Check local rules

---

### 4. CashFlowProjector

**Purpose:** Project monthly cash flow impact of tax incentives.

**File:** `backend/engines/incentive_calculator/cash_flow_projector.py`

**Key Functions:**

```python
@dataclass
class CashFlowEvent:
    """Single cash flow event"""
    month: int  # Months from project start (0 = start)
    event_type: str  # "production_spend", "incentive_receipt", "loan_disbursement", etc.
    description: str
    amount: Decimal
    cumulative_balance: Decimal
    policy_id: Optional[str] = None


@dataclass
class CashFlowProjection:
    """Complete cash flow timeline"""
    project_start_month: int  # e.g., 0
    production_period_months: int  # e.g., 18
    events: List[CashFlowEvent]
    monthly_summary: Dict[int, Decimal]  # month → net cash flow
    cumulative_summary: Dict[int, Decimal]  # month → cumulative balance
    peak_funding_required: Decimal
    total_incentive_receipts: Decimal


class CashFlowProjector:
    """Project cash flow timeline for incentive scenarios"""

    def __init__(self):
        """Initialize projector"""

    def project(
        self,
        production_budget: Decimal,
        production_schedule_months: int,
        jurisdiction_spends: List[JurisdictionSpend],
        incentive_results: List[IncentiveResult],
        spend_curve: Optional[List[Decimal]] = None
    ) -> CashFlowProjection:
        """
        Project cash flow with incentive timing.

        Args:
            production_budget: Total budget
            production_schedule_months: Production timeline
            jurisdiction_spends: Spending by jurisdiction
            incentive_results: Calculated incentive results
            spend_curve: Optional monthly spend profile (% of budget per month)
                        If not provided, uses S-curve default

        Logic:
        1. Generate production spend events (monthly)
        2. Calculate incentive receipt timing based on:
           - Completion month (end of production)
           - Audit period (timing_months_audit_to_certification)
           - Cash receipt (timing_months_certification_to_cash)
        3. If loan/transfer: Adjust timing for upfront disbursement
        4. Calculate running balance

        Returns:
            CashFlowProjection with month-by-month detail
        """

    def monthly_view(
        self,
        projection: CashFlowProjection
    ) -> pd.DataFrame:
        """
        Convert projection to DataFrame for analysis.

        Columns:
        - month: int
        - spend: Decimal
        - incentive_receipts: Decimal
        - net_cash_flow: Decimal
        - cumulative_balance: Decimal
        - events: List[str] (event descriptions)

        Returns:
            pandas DataFrame (optional dependency)
        """

    def compare_timing_scenarios(
        self,
        base_projection: CashFlowProjection,
        loan_projection: CashFlowProjection
    ) -> Dict[str, Any]:
        """
        Compare direct monetization vs. loan timing.

        Returns:
            {
                "peak_funding_difference": Decimal,
                "months_earlier": int,
                "loan_cost": Decimal,
                "net_benefit_difference": Decimal
            }
        """
```

**Spend Curve Defaults:**
- **S-Curve (Default):** Slow ramp (months 0-3), peak (months 4-10), tail (months 11+)
- **Even Distribution:** Equal monthly spend
- **Front-Loaded:** Higher spend in early months (pre-production heavy)
- **Custom:** User-provided monthly percentages

---

### 5. MonetizationComparator

**Purpose:** Compare different monetization strategies for tax incentives.

**File:** `backend/engines/incentive_calculator/monetization_comparator.py`

**Key Functions:**

```python
@dataclass
class MonetizationScenario:
    """Single monetization strategy"""
    strategy_name: str  # "Direct Cash", "Tax Credit Loan", "Transfer to Investor"
    monetization_method: MonetizationMethod
    gross_credit: Decimal
    discount_rate: Decimal  # Transfer discount or loan fee
    discount_amount: Decimal
    net_proceeds: Decimal
    timing_months: int
    effective_rate: Decimal
    notes: str


@dataclass
class MonetizationComparison:
    """Comparison of multiple monetization strategies"""
    policy_id: str
    policy_name: str
    qualified_spend: Decimal
    scenarios: List[MonetizationScenario]
    recommended_strategy: str
    recommendation_reason: str


class MonetizationComparator:
    """Compare monetization strategies for tax incentives"""

    def __init__(self, calculator: IncentiveCalculator):
        """Initialize with calculator reference"""

    def compare_strategies(
        self,
        policy_id: str,
        qualified_spend: Decimal,
        jurisdiction_spend: JurisdictionSpend,
        strategies: Optional[List[MonetizationMethod]] = None
    ) -> MonetizationComparison:
        """
        Compare available monetization strategies for a policy.

        Args:
            policy_id: Policy to analyze
            qualified_spend: Amount of qualified spend
            jurisdiction_spend: Full spending detail
            strategies: List of strategies to compare (if None, use all supported)

        Logic:
        1. Get policy from registry
        2. For each monetization method policy supports:
           - Calculate net benefit with typical market rate
           - Calculate effective rate
           - Note timing differences
        3. Rank by net benefit (adjusted for time value if applicable)
        4. Generate recommendation

        Returns:
            MonetizationComparison with all scenarios
        """

    def optimal_strategy(
        self,
        comparison: MonetizationComparison,
        time_value_discount_rate: Optional[Decimal] = None
    ) -> MonetizationScenario:
        """
        Select optimal strategy considering time value of money.

        Args:
            comparison: MonetizationComparison to analyze
            time_value_discount_rate: Annual discount rate (e.g., 0.12 for 12%)
                                     If provided, adjusts for timing differences

        Returns:
            MonetizationScenario that maximizes NPV
        """

    def loan_vs_direct_analysis(
        self,
        policy_id: str,
        qualified_spend: Decimal,
        jurisdiction_spend: JurisdictionSpend,
        loan_fee_rate: Decimal,
        production_schedule_months: int
    ) -> Dict[str, Any]:
        """
        Detailed comparison of tax credit loan vs. direct monetization.

        Returns:
            {
                "loan_scenario": {
                    "upfront_proceeds": Decimal,
                    "loan_fee": Decimal,
                    "month_received": int,
                    "net_benefit": Decimal
                },
                "direct_scenario": {
                    "cash_received": Decimal,
                    "month_received": int,
                    "net_benefit": Decimal
                },
                "difference": {
                    "loan_cost": Decimal,
                    "months_earlier": int,
                    "break_even_opportunity_cost": Decimal  # Annual rate where equal
                }
            }
        """
```

**Default Market Rates (from rate_card_2025.json):**
- Transfer discount: 15-25% (use 20% default)
- Tax credit loan fee: 8-12% (use 10% default)
- Tax liability offset: 0% discount (but requires corporate tax liability)

---

## File Structure

```
backend/engines/
└── incentive_calculator/
    ├── __init__.py
    ├── policy_loader.py          # PolicyLoader class
    ├── policy_registry.py        # PolicyRegistry class
    ├── calculator.py             # IncentiveCalculator + result dataclasses
    ├── cash_flow_projector.py   # CashFlowProjector class
    ├── monetization_comparator.py  # MonetizationComparator class
    ├── stacking_rules.py         # Stacking logic helpers
    └── utils.py                   # Shared utilities

backend/engines/incentive_calculator/tests/
    ├── __init__.py
    ├── test_policy_loader.py
    ├── test_policy_registry.py
    ├── test_calculator.py
    ├── test_cash_flow_projector.py
    ├── test_monetization_comparator.py
    └── test_integration.py       # End-to-end scenarios

backend/engines/examples/
    ├── example_single_jurisdiction.py
    ├── example_multi_jurisdiction.py
    ├── example_stacking.py
    ├── example_cash_flow.py
    └── example_monetization_comparison.py
```

---

## Integration Points

### With Existing Pydantic Models (Phase 2A)

- **IncentivePolicy** (`backend/models/incentive_policy.py`): Core data model used throughout
- **ProjectProfile** (`backend/models/project_profile.py`): Optional integration for cultural test validation
- **CapitalStack** (`backend/models/capital_stack.py`): Engine 1 results can inform tax credit loan sizing

### With Curated Data (Phase 3)

- **Policy JSON files** (`backend/data/policies/*.json`): Primary data source
- **Rate card** (`backend/data/market/rate_card_2025.json`): Default monetization rates

### With Future Components

- **Engine 2 (Waterfall)**: Incentive results feed into waterfall as financing sources
- **Engine 3 (Optimizer)**: Multi-jurisdiction results used for scenario optimization
- **Phase 4 API**: All Engine 1 classes exposed via FastAPI endpoints
- **Phase 4 Frontend**: Results formatted for visualization

---

## Data Flow Example

### Scenario: "The Dragon's Quest" Multi-Jurisdiction Calculation

**Input:**
```python
total_budget = Decimal("30000000")

quebec_spend = JurisdictionSpend(
    jurisdiction="Canada-Quebec",
    policy_ids=["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],  # Stacking
    qualified_spend=Decimal("16500000"),
    total_spend=Decimal("16500000"),
    labor_spend=Decimal("12000000"),  # 55% of budget
    goods_services_spend=Decimal("3000000"),
    post_production_spend=Decimal("1000000"),
    vfx_animation_spend=Decimal("500000")
)

ireland_spend = JurisdictionSpend(
    jurisdiction="Ireland",
    policy_ids=["IE-S481-SCEAL-2025"],
    qualified_spend=Decimal("7500000"),  # 25% of budget
    total_spend=Decimal("7500000"),
    labor_spend=Decimal("5000000"),
    goods_services_spend=Decimal("2000000"),
    post_production_spend=Decimal("400000"),
    vfx_animation_spend=Decimal("100000")
)

california_spend = JurisdictionSpend(
    jurisdiction="United States",
    policy_ids=["US-CA-FILMTAX-2025"],
    qualified_spend=Decimal("6000000"),  # 20% of budget
    total_spend=Decimal("6000000"),
    labor_spend=Decimal("4500000"),
    goods_services_spend=Decimal("1200000"),
    post_production_spend=Decimal("200000"),
    vfx_animation_spend=Decimal("100000")
)

monetization_prefs = {
    "CA-FEDERAL-CPTC-2025": MonetizationMethod.DIRECT_CASH,
    "CA-QC-PSTC-2025": MonetizationMethod.DIRECT_CASH,
    "IE-S481-SCEAL-2025": MonetizationMethod.DIRECT_CASH,
    "US-CA-FILMTAX-2025": MonetizationMethod.DIRECT_CASH
}
```

**Processing:**
1. PolicyLoader loads 4 policies from JSON
2. IncentiveCalculator processes each:
   - Quebec: Federal CPTC (25% × $12M labor = $3M, capped at 15% budget = $2.475M)
   - Quebec: Provincial PSTC (36% × $12M labor = $4.32M) → **Stacking applied**
   - Ireland: Scéal (40% × $7.5M = $3M)
   - California: 35% × $6M = $2.1M
3. Apply stacking rules for Canada Federal + Quebec
4. Calculate net benefits (apply audit costs, timing)
5. Aggregate results

**Output:**
```python
MultiJurisdictionResult(
    total_budget=Decimal("30000000"),
    total_qualified_spend=Decimal("30000000"),
    jurisdiction_results=[
        IncentiveResult(policy_id="CA-FEDERAL-CPTC-2025", net_cash_benefit=Decimal("2475000"), effective_rate=Decimal("20.625"), ...),
        IncentiveResult(policy_id="CA-QC-PSTC-2025", net_cash_benefit=Decimal("4320000"), effective_rate=Decimal("36.0"), ...),
        IncentiveResult(policy_id="IE-S481-SCEAL-2025", net_cash_benefit=Decimal("3000000"), effective_rate=Decimal("40.0"), ...),
        IncentiveResult(policy_id="US-CA-FILMTAX-2025", net_cash_benefit=Decimal("2100000"), effective_rate=Decimal("35.0"), ...)
    ],
    total_gross_credits=Decimal("11895000"),
    total_net_benefits=Decimal("11895000"),  # Simplified (after audit costs ~$145k)
    blended_effective_rate=Decimal("39.65"),  # $11.895M / $30M
    stacking_applied=["Canada: Federal CPTC + Quebec PSTC"],
    total_timing_weighted_months=Decimal("9.2")
)
```

---

## Test Strategy

### Unit Tests

**`test_policy_loader.py`**
- ✓ Load single policy by ID
- ✓ Load all policies
- ✓ Load by jurisdiction
- ✓ Handle missing file error
- ✓ Handle invalid JSON error
- ✓ Handle schema validation error
- ✓ Validate policies directory

**`test_policy_registry.py`**
- ✓ Initialize and load policies
- ✓ Get policy by ID
- ✓ Get policies by jurisdiction
- ✓ Search by criteria (rate, type, monetization method)
- ✓ Identify stackable policies
- ✓ Reload policies

**`test_calculator.py`**
- ✓ Calculate single jurisdiction (base case)
- ✓ Calculate with per-project cap applied
- ✓ Calculate with two-tier rate (Spain)
- ✓ Calculate with labor cap (Canada Federal)
- ✓ Multi-jurisdiction without stacking
- ✓ Multi-jurisdiction with stacking (Canada)
- ✓ Multi-jurisdiction with stacking (Australia)
- ✓ Validate minimum spend requirements
- ✓ Validate cultural test warnings
- ✓ Handle monetization method not supported

**`test_cash_flow_projector.py`**
- ✓ Project with default S-curve spend
- ✓ Project with custom spend curve
- ✓ Calculate incentive receipt timing
- ✓ Generate monthly summary DataFrame
- ✓ Compare direct vs. loan timing

**`test_monetization_comparator.py`**
- ✓ Compare all strategies for transferable credit
- ✓ Compare all strategies for refundable credit
- ✓ Calculate optimal strategy with time value
- ✓ Loan vs. direct detailed analysis
- ✓ Recommend strategy with reasoning

**`test_integration.py`** (End-to-end)
- ✓ Complete "Dragon's Quest" scenario (3 jurisdictions, stacking)
- ✓ Quebec-only maximum stacking scenario
- ✓ Australia Producer + PDV stacking scenario
- ✓ UK AVEC single jurisdiction scenario
- ✓ Cash flow projection for multi-jurisdiction project
- ✓ Monetization comparison across all policies

### Test Data

- Use existing 15 policy JSON files
- Create `test_fixtures.py` with sample JurisdictionSpend objects
- Mock rate card data for monetization tests

### Coverage Target

- **Minimum:** 90% code coverage
- **Priority:** 100% coverage on calculation logic (calculator.py core functions)

---

## Example Usage Scenarios

### Example 1: Single Jurisdiction Calculation

```python
from backend.engines.incentive_calculator import PolicyLoader, PolicyRegistry, IncentiveCalculator
from backend.models.incentive_policy import MonetizationMethod
from decimal import Decimal

# Initialize
loader = PolicyLoader(Path("backend/data/policies"))
registry = PolicyRegistry(loader)
calculator = IncentiveCalculator(registry)

# Define spend
uk_spend = JurisdictionSpend(
    jurisdiction="United Kingdom",
    policy_ids=["UK-AVEC-2025"],
    qualified_spend=Decimal("5000000"),
    total_spend=Decimal("6000000"),
    labor_spend=Decimal("3000000"),
    goods_services_spend=Decimal("1500000"),
    post_production_spend=Decimal("400000"),
    vfx_animation_spend=Decimal("100000")
)

# Calculate
result = calculator.calculate_single_jurisdiction(
    policy_id="UK-AVEC-2025",
    jurisdiction_spend=uk_spend,
    monetization_method=MonetizationMethod.DIRECT_CASH
)

print(f"UK AVEC Result:")
print(f"  Qualified Spend: £{result.qualified_spend:,.0f}")
print(f"  Gross Credit: £{result.gross_credit:,.0f}")
print(f"  Net Benefit: £{result.net_cash_benefit:,.0f}")
print(f"  Effective Rate: {result.effective_rate}%")
print(f"  Timing: {result.timing_months} months")
```

### Example 2: Multi-Jurisdiction with Stacking

```python
# Quebec + Federal stacking
quebec_spend = JurisdictionSpend(
    jurisdiction="Canada-Quebec",
    policy_ids=["CA-FEDERAL-CPTC-2025", "CA-QC-PSTC-2025"],
    qualified_spend=Decimal("10000000"),
    total_spend=Decimal("10000000"),
    labor_spend=Decimal("8000000"),
    goods_services_spend=Decimal("1500000"),
    post_production_spend=Decimal("400000"),
    vfx_animation_spend=Decimal("100000")
)

result = calculator.calculate_multi_jurisdiction(
    total_budget=Decimal("10000000"),
    jurisdiction_spends=[quebec_spend],
    monetization_preferences={
        "CA-FEDERAL-CPTC-2025": MonetizationMethod.DIRECT_CASH,
        "CA-QC-PSTC-2025": MonetizationMethod.DIRECT_CASH
    }
)

print(f"Quebec Stacking Result:")
print(f"  Total Net Benefits: ${result.total_net_benefits:,.0f}")
print(f"  Blended Effective Rate: {result.blended_effective_rate}%")
print(f"  Stacking Applied: {', '.join(result.stacking_applied)}")
```

### Example 3: Cash Flow Projection

```python
from backend.engines.incentive_calculator import CashFlowProjector

projector = CashFlowProjector()

projection = projector.project(
    production_budget=Decimal("30000000"),
    production_schedule_months=18,
    jurisdiction_spends=[quebec_spend, ireland_spend, california_spend],
    incentive_results=result.jurisdiction_results
)

print(f"Cash Flow Projection:")
print(f"  Peak Funding Required: ${projection.peak_funding_required:,.0f}")
print(f"  Total Incentive Receipts: ${projection.total_incentive_receipts:,.0f}")
print(f"\nKey Events:")
for event in projection.events[:10]:  # First 10 events
    print(f"  Month {event.month}: {event.description} - ${event.amount:,.0f}")
```

### Example 4: Monetization Comparison

```python
from backend.engines.incentive_calculator import MonetizationComparator

comparator = MonetizationComparator(calculator)

comparison = comparator.compare_strategies(
    policy_id="US-GA-GEFA-2025",
    qualified_spend=Decimal("8000000"),
    jurisdiction_spend=georgia_spend,
    strategies=[
        MonetizationMethod.DIRECT_CASH,
        MonetizationMethod.TRANSFER_TO_INVESTOR,
        MonetizationMethod.TAX_CREDIT_LOAN
    ]
)

print(f"Georgia Monetization Comparison:")
for scenario in comparison.scenarios:
    print(f"\n{scenario.strategy_name}:")
    print(f"  Net Proceeds: ${scenario.net_proceeds:,.0f}")
    print(f"  Effective Rate: {scenario.effective_rate}%")
    print(f"  Timing: {scenario.timing_months} months")

print(f"\nRecommended: {comparison.recommended_strategy}")
print(f"Reason: {comparison.recommendation_reason}")
```

---

## Dependencies

### Required (Already in Project)
- `pydantic>=2.5.0` - Data validation
- `python>=3.11` - Type hints and performance

### New Dependencies for Engine 1
```toml
# Add to pyproject.toml or requirements.txt
pandas>=2.1.0  # Optional - for monthly_view() DataFrame output
numpy>=1.26.0  # Optional - for spend curve calculations
```

### Optional (Future)
- `plotly>=5.18.0` - For cash flow visualization
- `jupyter>=1.0.0` - For example notebooks

---

## Timeline Estimate

**Total:** ~6-7 hours for complete implementation + testing

| Component | Estimated Time |
|-----------|---------------|
| PolicyLoader + PolicyRegistry | 1.5 hours |
| IncentiveCalculator (core) | 2 hours |
| Stacking logic | 1 hour |
| CashFlowProjector | 1 hour |
| MonetizationComparator | 1 hour |
| Unit tests | 2 hours |
| Integration tests + examples | 1.5 hours |
| Documentation | 1 hour |

**Parallel Work Opportunities:**
- PolicyLoader + Registry can be built independently
- CashFlowProjector and MonetizationComparator can be built in parallel after calculator core is done
- Tests can be written concurrently with implementation

---

## Success Criteria

Engine 1 is **complete** when:

✅ **Functional Requirements:**
1. Can load all 15 curated policies without errors
2. Single jurisdiction calculations match manual calculations (within $1)
3. Multi-jurisdiction calculations correctly aggregate results
4. Stacking logic works for Canada (Federal+Provincial) and Australia (Offset+PDV)
5. Cash flow projections generate month-by-month timelines
6. Monetization comparisons identify optimal strategy

✅ **Quality Requirements:**
1. 90%+ test coverage
2. All tests pass
3. Type hints on all public functions
4. Docstrings on all classes and public methods
5. Example files demonstrate all core features

✅ **Integration Requirements:**
1. Works seamlessly with Phase 2A Pydantic models
2. Reads Phase 3 JSON policy files
3. Produces output compatible with future Engine 2 (waterfall)

---

## Next Steps After Engine 1

Once Engine 1 is complete:

1. **Engine 2:** Waterfall Execution Engine
   - Integrate incentive results into capital stack
   - Execute 13-tier recoupment waterfall
   - Generate investor return projections

2. **Engine 3:** Scenario Generator & Optimizer
   - Monte Carlo simulation for revenue uncertainty
   - Optimization of jurisdiction allocation
   - Sensitivity analysis

3. **Phase 4:** API + Frontend
   - FastAPI endpoints exposing Engine 1 functions
   - Next.js UI for interactive incentive calculator
   - D3.js visualization of cash flows and comparisons

---

## Appendix: Stacking Rules Reference

### Canada: Federal + Provincial

**Stackable:**
- Federal CPTC (labor-based, max 15% of budget)
- Quebec PSTC (labor-based, 36% for animation)
- Ontario OCASE (labor-based, 18% on animation labor)

**Rules:**
- Different bases (federal vs. provincial taxes)
- No double-dipping on same labor dollars (but both can claim same labor expense)
- Combined can exceed 50% of budget

**Example:**
- $10M budget, $8M Quebec labor
- Federal: 25% × $8M = $2M, capped at 15% budget = $1.5M
- Quebec: 36% × $8M = $2.88M
- Total: $4.38M (43.8% of budget)

### Australia: Producer Offset + PDV Offset

**Stackable:**
- Producer Offset (40% theatrical / 30% other)
- PDV Offset (30% on post/VFX/animation)

**Rules:**
- Can stack if spend qualifies for both
- Producer Offset on Australian production costs
- PDV Offset on Australian post/digital/visual work
- Combined cap at 60% of qualifying spend (not budget)

**Example:**
- $15M budget, $10M qualifies for Producer Offset, $6M qualifies for PDV (overlap)
- Producer: 40% × $10M = $4M
- PDV: 30% × $6M = $1.8M
- Total: $5.8M if both apply (check cap rules)

### Spain: National + Regional

**Potentially Stackable:**
- National credit (30%/25%)
- Regional incentives (Canary Islands, Basque Country)

**Rules:**
- Check specific regional program compatibility
- Combined subject to 75% cap for low-budget animations (<€2.5M)

---

**End of Implementation Plan**

This plan provides a complete roadmap for building Engine 1. All components are designed to integrate with existing Phase 2A models and Phase 3 data, while providing a foundation for Engines 2 & 3.

Ready to proceed with implementation.
