"""
Tests for CapitalProgramManager Engine

Comprehensive test coverage for capital allocation, constraint validation,
portfolio metrics, and funding lifecycle.
"""

import pytest
from decimal import Decimal
from datetime import date
import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from models.capital_program import (
    CapitalProgram,
    CapitalSource,
    CapitalDeployment,
    CapitalProgramConstraints,
    ProgramType,
    ProgramStatus,
    AllocationStatus,
)

from engines.capital_programs import (
    AllocationRequest,
    AllocationResult,
    ConstraintViolation,
    PortfolioMetrics,
    CapitalProgramManager,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def manager():
    """Create fresh manager for each test"""
    return CapitalProgramManager()


@pytest.fixture
def basic_program():
    """Create a basic capital program"""
    source = CapitalSource(
        source_id="SRC-001",
        source_name="Main Fund",
        source_type="general",
        committed_amount=Decimal("50000000"),
    )

    return CapitalProgram(
        program_id="PROG-001",
        program_name="Animation Fund I",
        program_type=ProgramType.EXTERNAL_FUND,
        status=ProgramStatus.ACTIVE,
        target_size=Decimal("50000000"),
        sources=[source],
    )


@pytest.fixture
def constrained_program():
    """Create a program with strict constraints"""
    source = CapitalSource(
        source_id="SRC-001",
        source_name="Canadian Film Fund",
        source_type="government",
        committed_amount=Decimal("30000000"),
        geographic_restrictions=["Canada"],
        genre_restrictions=["Animation", "Family"],
    )

    constraints = CapitalProgramConstraints(
        max_single_project_pct=Decimal("20"),
        max_single_counterparty_pct=Decimal("30"),
        required_jurisdictions=["Canada"],
        prohibited_ratings=["R", "NC-17"],
        min_project_budget=Decimal("5000000"),
        max_project_budget=Decimal("40000000"),
    )

    return CapitalProgram(
        program_id="PROG-002",
        program_name="Canadian Animation Fund",
        program_type=ProgramType.GOVERNMENT_FUND,
        status=ProgramStatus.ACTIVE,
        target_size=Decimal("30000000"),
        sources=[source],
        constraints=constraints,
    )


# ============================================================================
# Test: Program Registration
# ============================================================================

class TestProgramRegistration:
    """Test program registration and retrieval"""

    def test_register_program(self, manager, basic_program):
        """Test registering a program"""
        manager.register_program(basic_program)

        retrieved = manager.get_program("PROG-001")
        assert retrieved is not None
        assert retrieved.program_name == "Animation Fund I"

    def test_get_nonexistent_program(self, manager):
        """Test getting a program that doesn't exist"""
        result = manager.get_program("NONEXISTENT")
        assert result is None

    def test_list_programs(self, manager, basic_program, constrained_program):
        """Test listing all programs"""
        manager.register_program(basic_program)
        manager.register_program(constrained_program)

        programs = manager.list_programs()
        assert len(programs) == 2

    def test_register_multiple_programs(self, manager):
        """Test registering multiple programs"""
        for i in range(5):
            program = CapitalProgram(
                program_id=f"PROG-{i:03d}",
                program_name=f"Fund {i}",
                program_type=ProgramType.EXTERNAL_FUND,
                target_size=Decimal("10000000"),
            )
            manager.register_program(program)

        assert len(manager.list_programs()) == 5


# ============================================================================
# Test: Basic Allocation
# ============================================================================

class TestBasicAllocation:
    """Test basic capital allocation"""

    def test_successful_allocation(self, manager, basic_program):
        """Test a successful allocation"""
        manager.register_program(basic_program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Sky Warriors",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )

        result = manager.allocate_capital(request)

        assert result.success is True
        assert result.allocation_id is not None
        assert result.deployment is not None
        assert result.deployment.allocated_amount == Decimal("5000000")
        assert result.deployment.status == AllocationStatus.APPROVED

    def test_allocation_updates_source(self, manager, basic_program):
        """Test that allocation updates source drawn amount"""
        manager.register_program(basic_program)
        initial_available = basic_program.sources[0].available_amount

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("10000000"),
            project_budget=Decimal("30000000"),
        )

        manager.allocate_capital(request)

        # Source should have less available
        assert basic_program.sources[0].available_amount == initial_available - Decimal("10000000")

    def test_allocation_creates_deployment(self, manager, basic_program):
        """Test that allocation creates deployment in program"""
        manager.register_program(basic_program)
        assert len(basic_program.deployments) == 0

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )

        manager.allocate_capital(request)

        assert len(basic_program.deployments) == 1
        assert basic_program.deployments[0].project_name == "Test Project"

    def test_allocation_nonexistent_program(self, manager):
        """Test allocation to nonexistent program fails"""
        request = AllocationRequest(
            program_id="NONEXISTENT",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )

        result = manager.allocate_capital(request)

        assert result.success is False
        assert len(result.violations) > 0
        assert any("not found" in v.description for v in result.violations)

    def test_allocation_inactive_program(self, manager, basic_program):
        """Test allocation to inactive program fails"""
        basic_program.status = ProgramStatus.CLOSED
        manager.register_program(basic_program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )

        result = manager.allocate_capital(request)

        assert result.success is False


# ============================================================================
# Test: Constraint Validation
# ============================================================================

class TestConstraintValidation:
    """Test constraint validation during allocation"""

    def test_concentration_limit_violation(self, manager, basic_program):
        """Test single project concentration limit"""
        basic_program.constraints = CapitalProgramConstraints(
            max_single_project_pct=Decimal("10")
        )
        manager.register_program(basic_program)

        # Request 20% of fund
        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Large Project",
            requested_amount=Decimal("10000000"),  # 20% of 50M
            project_budget=Decimal("50000000"),
        )

        result = manager.allocate_capital(request)

        assert result.success is False
        assert any(
            v.constraint_name == "max_single_project_pct"
            for v in result.violations
        )

    def test_jurisdiction_prohibited(self, manager, constrained_program):
        """Test prohibited jurisdiction"""
        manager.register_program(constrained_program)

        request = AllocationRequest(
            program_id="PROG-002",
            project_id="PROJ-001",
            project_name="US Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("20000000"),
            jurisdiction="United States",
        )

        result = manager.allocate_capital(request)

        # Should fail - US not in required list (Canada only)
        assert result.success is False

    def test_jurisdiction_required(self, manager, constrained_program):
        """Test required jurisdiction passes"""
        manager.register_program(constrained_program)

        request = AllocationRequest(
            program_id="PROG-002",
            project_id="PROJ-001",
            project_name="Canadian Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("20000000"),
            jurisdiction="Canada",
            genre="Animation",
        )

        result = manager.allocate_capital(request)
        assert result.success is True

    def test_rating_prohibited(self, manager, constrained_program):
        """Test prohibited rating fails"""
        manager.register_program(constrained_program)

        request = AllocationRequest(
            program_id="PROG-002",
            project_id="PROJ-001",
            project_name="R-Rated Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("20000000"),
            jurisdiction="Canada",
            rating="R",
        )

        result = manager.allocate_capital(request)

        assert result.success is False
        assert any(
            v.constraint_name == "prohibited_rating"
            for v in result.violations
        )

    def test_budget_too_small(self, manager, constrained_program):
        """Test project budget below minimum"""
        manager.register_program(constrained_program)

        request = AllocationRequest(
            program_id="PROG-002",
            project_id="PROJ-001",
            project_name="Small Project",
            requested_amount=Decimal("1000000"),
            project_budget=Decimal("2000000"),  # Below 5M minimum
            jurisdiction="Canada",
        )

        result = manager.allocate_capital(request)

        assert result.success is False
        assert any(
            v.constraint_name == "min_project_budget"
            for v in result.violations
        )

    def test_budget_too_large(self, manager, constrained_program):
        """Test project budget above maximum"""
        manager.register_program(constrained_program)

        request = AllocationRequest(
            program_id="PROG-002",
            project_id="PROJ-001",
            project_name="Mega Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("60000000"),  # Above 40M maximum
            jurisdiction="Canada",
        )

        result = manager.allocate_capital(request)

        assert result.success is False
        assert any(
            v.constraint_name == "max_project_budget"
            for v in result.violations
        )

    def test_soft_constraint_warning(self, manager, basic_program):
        """Test soft constraints generate warnings, not blocks"""
        basic_program.constraints = CapitalProgramConstraints(
            max_development_pct=Decimal("10"),
        )
        manager.register_program(basic_program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Development Project",
            requested_amount=Decimal("10000000"),
            project_budget=Decimal("30000000"),
            is_development=True,
        )

        result = manager.allocate_capital(request)

        # Soft constraints don't block
        assert result.success is True
        # But should have warnings
        assert len(result.warnings) > 0 or any(
            not v.is_blocking for v in result.violations
        )


# ============================================================================
# Test: Source Selection
# ============================================================================

class TestSourceSelection:
    """Test funding source selection logic"""

    def test_select_specified_source(self, manager):
        """Test selecting a specified source"""
        sources = [
            CapitalSource(
                source_id="SRC-001",
                source_name="Source A",
                committed_amount=Decimal("20000000"),
            ),
            CapitalSource(
                source_id="SRC-002",
                source_name="Source B",
                committed_amount=Decimal("30000000"),
            ),
        ]

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Multi-Source Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            status=ProgramStatus.ACTIVE,
            target_size=Decimal("50000000"),
            sources=sources,
        )
        manager.register_program(program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
            source_id="SRC-002",
        )

        result = manager.allocate_capital(request)

        assert result.success is True
        assert result.selected_source_id == "SRC-002"

    def test_auto_select_source(self, manager):
        """Test automatic source selection"""
        sources = [
            CapitalSource(
                source_id="SRC-001",
                source_name="Source A",
                committed_amount=Decimal("20000000"),
                interest_rate=Decimal("10"),  # Higher cost
            ),
            CapitalSource(
                source_id="SRC-002",
                source_name="Source B",
                committed_amount=Decimal("30000000"),
                interest_rate=Decimal("5"),  # Lower cost
            ),
        ]

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Multi-Source Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            status=ProgramStatus.ACTIVE,
            target_size=Decimal("50000000"),
            sources=sources,
        )
        manager.register_program(program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )

        result = manager.allocate_capital(request)

        # Should select lower cost source
        assert result.success is True
        assert result.selected_source_id == "SRC-002"

    def test_insufficient_source_capacity(self, manager, basic_program):
        """Test allocation fails when no source has capacity"""
        basic_program.sources[0].drawn_amount = Decimal("48000000")  # Only 2M left
        manager.register_program(basic_program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),  # Need 5M
            project_budget=Decimal("30000000"),
        )

        result = manager.allocate_capital(request)

        assert result.success is False
        assert any("available" in v.description.lower() for v in result.violations)


# ============================================================================
# Test: Dry Run / Validation
# ============================================================================

class TestDryRun:
    """Test dry run validation"""

    def test_dry_run_doesnt_allocate(self, manager, basic_program):
        """Test dry run doesn't create deployment"""
        manager.register_program(basic_program)
        initial_deployments = len(basic_program.deployments)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )

        result = manager.allocate_capital(request, dry_run=True)

        assert result.success is True
        assert result.deployment is None
        assert len(basic_program.deployments) == initial_deployments

    def test_dry_run_validates(self, manager, constrained_program):
        """Test dry run still validates constraints"""
        manager.register_program(constrained_program)

        request = AllocationRequest(
            program_id="PROG-002",
            project_id="PROJ-001",
            project_name="Invalid Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("2000000"),  # Below minimum
            jurisdiction="Canada",
        )

        result = manager.allocate_capital(request, dry_run=True)

        assert result.success is False
        assert len(result.violations) > 0


# ============================================================================
# Test: Funding Lifecycle
# ============================================================================

class TestFundingLifecycle:
    """Test deployment funding and recoupment lifecycle"""

    def test_fund_deployment(self, manager, basic_program):
        """Test funding a deployment"""
        manager.register_program(basic_program)

        # Create allocation
        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )
        result = manager.allocate_capital(request)
        deployment_id = result.allocation_id

        # Fund it
        success = manager.fund_deployment("PROG-001", deployment_id)

        assert success is True

        deployment = basic_program.deployments[0]
        assert deployment.status == AllocationStatus.FUNDED
        assert deployment.funded_amount == Decimal("5000000")
        assert deployment.funding_date == date.today()

    def test_partial_funding(self, manager, basic_program):
        """Test partial funding"""
        manager.register_program(basic_program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("10000000"),
            project_budget=Decimal("30000000"),
        )
        result = manager.allocate_capital(request)
        deployment_id = result.allocation_id

        # Fund partially
        manager.fund_deployment("PROG-001", deployment_id, Decimal("4000000"))

        deployment = basic_program.deployments[0]
        assert deployment.funded_amount == Decimal("4000000")

    def test_record_recoupment(self, manager, basic_program):
        """Test recording recoupment"""
        manager.register_program(basic_program)

        # Create and fund
        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )
        result = manager.allocate_capital(request)
        deployment_id = result.allocation_id
        manager.fund_deployment("PROG-001", deployment_id)

        # Record recoupment
        success = manager.record_recoupment(
            "PROG-001",
            deployment_id,
            recouped_amount=Decimal("3000000"),
            profit_amount=Decimal("500000"),
        )

        assert success is True

        deployment = basic_program.deployments[0]
        assert deployment.recouped_amount == Decimal("3000000")
        assert deployment.profit_distributed == Decimal("500000")

    def test_full_recoupment_changes_status(self, manager, basic_program):
        """Test that full recoupment changes status"""
        manager.register_program(basic_program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )
        result = manager.allocate_capital(request)
        deployment_id = result.allocation_id
        manager.fund_deployment("PROG-001", deployment_id)

        # Full recoupment
        manager.record_recoupment(
            "PROG-001",
            deployment_id,
            recouped_amount=Decimal("5000000"),
            profit_amount=Decimal("1000000"),
        )

        deployment = basic_program.deployments[0]
        assert deployment.status == AllocationStatus.RECOUPED


# ============================================================================
# Test: Portfolio Metrics
# ============================================================================

class TestPortfolioMetrics:
    """Test portfolio metrics calculation"""

    def test_basic_metrics(self, manager, basic_program):
        """Test basic portfolio metrics"""
        manager.register_program(basic_program)

        # Create some deployments
        for i in range(3):
            request = AllocationRequest(
                program_id="PROG-001",
                project_id=f"PROJ-{i:03d}",
                project_name=f"Project {i}",
                requested_amount=Decimal("5000000"),
                project_budget=Decimal("30000000"),
            )
            manager.allocate_capital(request)

        metrics = manager.calculate_portfolio_metrics("PROG-001")

        assert metrics is not None
        assert metrics.total_committed == Decimal("50000000")
        assert metrics.total_deployed == Decimal("15000000")
        assert metrics.num_projects == 3

    def test_concentration_metrics(self, manager, basic_program):
        """Test concentration metrics calculation"""
        manager.register_program(basic_program)

        # Create one large and one small deployment
        manager.allocate_capital(AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Large Project",
            requested_amount=Decimal("10000000"),
            project_budget=Decimal("50000000"),
        ))

        manager.allocate_capital(AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-002",
            project_name="Small Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("20000000"),
        ))

        metrics = manager.calculate_portfolio_metrics("PROG-001")

        # Largest project is 10M/50M = 20%
        assert metrics.largest_project_pct == Decimal("20")

    def test_metrics_nonexistent_program(self, manager):
        """Test metrics for nonexistent program"""
        metrics = manager.calculate_portfolio_metrics("NONEXISTENT")
        assert metrics is None


# ============================================================================
# Test: Batch Allocation
# ============================================================================

class TestBatchAllocation:
    """Test batch allocation optimization"""

    def test_batch_allocate_multiple(self, manager, basic_program):
        """Test allocating to multiple projects"""
        manager.register_program(basic_program)

        projects = [
            AllocationRequest(
                program_id="PROG-001",
                project_id=f"PROJ-{i:03d}",
                project_name=f"Project {i}",
                requested_amount=Decimal("5000000"),
                project_budget=Decimal("30000000"),
            )
            for i in range(5)
        ]

        results = manager.optimize_allocation("PROG-001", projects)

        assert len(results) == 5
        successful = sum(1 for r in results if r.success)
        assert successful == 5

    def test_batch_respects_capacity(self, manager, basic_program):
        """Test batch allocation respects total capacity"""
        manager.register_program(basic_program)

        # Request more than available
        projects = [
            AllocationRequest(
                program_id="PROG-001",
                project_id=f"PROJ-{i:03d}",
                project_name=f"Project {i}",
                requested_amount=Decimal("15000000"),  # 15M each
                project_budget=Decimal("40000000"),
            )
            for i in range(5)  # 75M total, but only 50M available
        ]

        results = manager.optimize_allocation("PROG-001", projects)

        total_allocated = sum(
            r.deployment.allocated_amount
            for r in results
            if r.success and r.deployment
        )

        # Should not exceed available capital (accounting for reserves)
        assert total_allocated <= basic_program.deployable_capital

    def test_batch_with_cap(self, manager, basic_program):
        """Test batch allocation with explicit cap"""
        manager.register_program(basic_program)

        projects = [
            AllocationRequest(
                program_id="PROG-001",
                project_id=f"PROJ-{i:03d}",
                project_name=f"Project {i}",
                requested_amount=Decimal("5000000"),
                project_budget=Decimal("30000000"),
            )
            for i in range(5)
        ]

        results = manager.optimize_allocation(
            "PROG-001",
            projects,
            max_total_allocation=Decimal("10000000"),
        )

        total_allocated = sum(
            r.deployment.allocated_amount
            for r in results
            if r.success and r.deployment
        )

        assert total_allocated <= Decimal("10000000")


# ============================================================================
# Test: Recommendations
# ============================================================================

class TestRecommendations:
    """Test recommendation generation"""

    def test_recommendations_on_violation(self, manager, basic_program):
        """Test recommendations are generated on constraint violation"""
        basic_program.constraints = CapitalProgramConstraints(
            max_single_project_pct=Decimal("10"),
        )
        manager.register_program(basic_program)

        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Large Project",
            requested_amount=Decimal("10000000"),
            project_budget=Decimal("50000000"),
        )

        result = manager.allocate_capital(request)

        assert len(result.recommendations) > 0

    def test_recommendations_high_deployment(self, manager, basic_program):
        """Test recommendations when fund capital is constrained"""
        # Set high utilization to trigger reserve warning
        basic_program.sources[0].drawn_amount = Decimal("42000000")  # 84% utilized
        manager.register_program(basic_program)

        # Allocate more (will dip into reserves)
        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("5000000"),
            project_budget=Decimal("30000000"),
        )

        result = manager.allocate_capital(request)

        # Should get recommendation about reserves or allocation
        assert len(result.recommendations) > 0


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_zero_amount_allocation(self, manager, basic_program):
        """Test allocation with zero amount raises error"""
        manager.register_program(basic_program)

        # AllocationRequest dataclass doesn't validate, but deployment creation will fail
        request = AllocationRequest(
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            requested_amount=Decimal("0"),
            project_budget=Decimal("30000000"),
        )

        # Raises validation error when trying to create deployment with amount=0
        with pytest.raises(Exception):
            manager.allocate_capital(request)

    def test_multiple_allocations_same_project(self, manager, basic_program):
        """Test multiple allocations to same project"""
        manager.register_program(basic_program)

        for i in range(3):
            request = AllocationRequest(
                program_id="PROG-001",
                project_id="PROJ-001",  # Same project
                project_name="Same Project",
                requested_amount=Decimal("2000000"),
                project_budget=Decimal("30000000"),
            )
            result = manager.allocate_capital(request)
            assert result.success is True

        # Should have 3 deployments
        assert len(basic_program.deployments) == 3

    def test_fund_nonexistent_deployment(self, manager, basic_program):
        """Test funding nonexistent deployment"""
        manager.register_program(basic_program)

        success = manager.fund_deployment("PROG-001", "NONEXISTENT")
        assert success is False

    def test_recoup_nonexistent_deployment(self, manager, basic_program):
        """Test recoupment on nonexistent deployment"""
        manager.register_program(basic_program)

        success = manager.record_recoupment(
            "PROG-001",
            "NONEXISTENT",
            Decimal("1000000"),
        )
        assert success is False
