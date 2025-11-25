"""
Tests for Capital Program Model

Comprehensive test coverage for CapitalProgram, CapitalSource, CapitalDeployment,
and factory functions.
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
    create_internal_pool,
    create_external_fund,
    create_output_deal,
    create_spv,
)


# ============================================================================
# Test: CapitalSource
# ============================================================================

class TestCapitalSource:
    """Test CapitalSource model"""

    def test_create_basic_source(self):
        """Create a basic capital source"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="LP Commitment - Alpha Fund",
            source_type="lp_commitment",
            committed_amount=Decimal("10000000"),
        )

        assert source.source_id == "SRC-001"
        assert source.source_name == "LP Commitment - Alpha Fund"
        assert source.committed_amount == Decimal("10000000")
        assert source.drawn_amount == Decimal("0")
        assert source.currency == "USD"

    def test_source_available_amount(self):
        """Test available amount calculation"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Test Source",
            committed_amount=Decimal("10000000"),
            drawn_amount=Decimal("3000000"),
        )

        assert source.available_amount == Decimal("7000000")

    def test_source_utilization_rate(self):
        """Test utilization rate calculation"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Test Source",
            committed_amount=Decimal("10000000"),
            drawn_amount=Decimal("2500000"),
        )

        assert source.utilization_rate == Decimal("25")

    def test_source_with_restrictions(self):
        """Test source with geographic and genre restrictions"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Canada Fund",
            committed_amount=Decimal("5000000"),
            geographic_restrictions=["Canada", "UK"],
            genre_restrictions=["Animation", "Family"],
            budget_range_min=Decimal("5000000"),
            budget_range_max=Decimal("50000000"),
        )

        assert "Canada" in source.geographic_restrictions
        assert "Animation" in source.genre_restrictions
        assert source.budget_range_min == Decimal("5000000")

    def test_source_to_dict(self):
        """Test serialization to dictionary"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Test Source",
            committed_amount=Decimal("10000000"),
            interest_rate=Decimal("8.0"),
        )

        data = source.to_dict()
        assert data["source_id"] == "SRC-001"
        assert data["committed_amount"] == "10000000"
        assert data["interest_rate"] == "8.0"


# ============================================================================
# Test: CapitalDeployment
# ============================================================================

class TestCapitalDeployment:
    """Test CapitalDeployment model"""

    def test_create_basic_deployment(self):
        """Create a basic deployment"""
        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Sky Warriors",
            allocated_amount=Decimal("5000000"),
        )

        assert deployment.deployment_id == "DEP-001"
        assert deployment.allocated_amount == Decimal("5000000")
        assert deployment.funded_amount == Decimal("0")
        assert deployment.status == AllocationStatus.PENDING

    def test_deployment_outstanding_amount(self):
        """Test outstanding amount calculation"""
        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            allocated_amount=Decimal("5000000"),
            funded_amount=Decimal("5000000"),
            recouped_amount=Decimal("2000000"),
        )

        assert deployment.outstanding_amount == Decimal("3000000")

    def test_deployment_total_return(self):
        """Test total return calculation"""
        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            allocated_amount=Decimal("5000000"),
            funded_amount=Decimal("5000000"),
            recouped_amount=Decimal("5000000"),
            profit_distributed=Decimal("1500000"),
        )

        assert deployment.total_return == Decimal("6500000")

    def test_deployment_multiple(self):
        """Test return multiple calculation"""
        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            allocated_amount=Decimal("5000000"),
            funded_amount=Decimal("5000000"),
            recouped_amount=Decimal("5000000"),
            profit_distributed=Decimal("2500000"),
        )

        assert deployment.multiple == Decimal("1.5")

    def test_deployment_multiple_unfunded(self):
        """Test multiple returns None when not funded"""
        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            allocated_amount=Decimal("5000000"),
        )

        assert deployment.multiple is None


# ============================================================================
# Test: CapitalProgramConstraints
# ============================================================================

class TestCapitalProgramConstraints:
    """Test CapitalProgramConstraints model"""

    def test_default_constraints(self):
        """Test default constraint values"""
        constraints = CapitalProgramConstraints()

        assert constraints.max_single_project_pct == Decimal("25")
        assert constraints.max_single_counterparty_pct == Decimal("40")
        assert constraints.max_development_pct == Decimal("30")
        assert constraints.min_reserve_pct == Decimal("10")

    def test_custom_constraints(self):
        """Test custom constraint values"""
        constraints = CapitalProgramConstraints(
            max_single_project_pct=Decimal("15"),
            required_jurisdictions=["Canada", "UK", "France"],
            prohibited_ratings=["R", "NC-17"],
            target_num_projects=10,
        )

        assert constraints.max_single_project_pct == Decimal("15")
        assert "Canada" in constraints.required_jurisdictions
        assert "R" in constraints.prohibited_ratings
        assert constraints.target_num_projects == 10

    def test_constraints_to_dict(self):
        """Test serialization to dictionary"""
        constraints = CapitalProgramConstraints(
            target_portfolio_irr=Decimal("15.0"),
        )

        data = constraints.to_dict()
        assert "hard_constraints" in data
        assert "soft_constraints" in data
        assert data["soft_constraints"]["target_portfolio_irr"] == "15.0"


# ============================================================================
# Test: CapitalProgram
# ============================================================================

class TestCapitalProgram:
    """Test CapitalProgram model"""

    def test_create_basic_program(self):
        """Create a basic capital program"""
        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Animation Fund I",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("50000000"),
        )

        assert program.program_id == "PROG-001"
        assert program.program_name == "Animation Fund I"
        assert program.program_type == ProgramType.EXTERNAL_FUND
        assert program.status == ProgramStatus.PROSPECTIVE
        assert program.target_size == Decimal("50000000")

    def test_program_with_sources(self):
        """Create program with multiple sources"""
        sources = [
            CapitalSource(
                source_id="SRC-001",
                source_name="LP 1",
                committed_amount=Decimal("20000000"),
            ),
            CapitalSource(
                source_id="SRC-002",
                source_name="LP 2",
                committed_amount=Decimal("15000000"),
            ),
        ]

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Test Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("50000000"),
            sources=sources,
        )

        assert len(program.sources) == 2
        assert program.total_committed == Decimal("35000000")

    def test_program_computed_metrics(self):
        """Test program computed metrics"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Main Fund",
            committed_amount=Decimal("50000000"),
            drawn_amount=Decimal("15000000"),
        )

        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Project Alpha",
            allocated_amount=Decimal("10000000"),
            funded_amount=Decimal("10000000"),
            recouped_amount=Decimal("5000000"),
            profit_distributed=Decimal("2000000"),
            status=AllocationStatus.FUNDED,
        )

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Test Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("50000000"),
            sources=[source],
            deployments=[deployment],
        )

        assert program.total_committed == Decimal("50000000")
        assert program.total_drawn == Decimal("15000000")
        assert program.total_available == Decimal("35000000")
        assert program.total_allocated == Decimal("10000000")
        assert program.total_funded == Decimal("10000000")
        assert program.total_recouped == Decimal("5000000")
        assert program.total_profit == Decimal("2000000")
        assert program.num_active_projects == 1

    def test_program_commitment_progress(self):
        """Test commitment progress calculation"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Main Fund",
            committed_amount=Decimal("30000000"),
        )

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Test Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("50000000"),
            sources=[source],
        )

        assert program.commitment_progress == Decimal("60")

    def test_program_deployment_rate(self):
        """Test deployment rate calculation"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Main Fund",
            committed_amount=Decimal("50000000"),
        )

        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Project Alpha",
            allocated_amount=Decimal("20000000"),
        )

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Test Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("50000000"),
            sources=[source],
            deployments=[deployment],
        )

        assert program.deployment_rate == Decimal("40")

    def test_program_reserve_amount(self):
        """Test reserve amount calculation"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Main Fund",
            committed_amount=Decimal("50000000"),
        )

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Test Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("50000000"),
            sources=[source],
            constraints=CapitalProgramConstraints(min_reserve_pct=Decimal("10")),
        )

        assert program.reserve_amount == Decimal("5000000")

    def test_program_validation_drawn_exceeds_committed(self):
        """Test validation fails when drawn exceeds committed"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Main Fund",
            committed_amount=Decimal("10000000"),
            drawn_amount=Decimal("15000000"),  # More than committed
        )

        with pytest.raises(ValueError, match="drawn cannot exceed.*committed"):
            CapitalProgram(
                program_id="PROG-001",
                program_name="Test Fund",
                program_type=ProgramType.EXTERNAL_FUND,
                target_size=Decimal("50000000"),
                sources=[source],
            )

    def test_program_validation_investment_period(self):
        """Test validation fails when investment period exceeds fund term"""
        # Investment period (8 years) exceeds fund term (5 years)
        # Both are valid individually but together are invalid
        with pytest.raises(ValueError, match="Investment period cannot exceed fund term"):
            CapitalProgram(
                program_id="PROG-001",
                program_name="Test Fund",
                program_type=ProgramType.EXTERNAL_FUND,
                target_size=Decimal("50000000"),
                investment_period_years=8,
                fund_term_years=5,
            )


# ============================================================================
# Test: Factory Functions
# ============================================================================

class TestFactoryFunctions:
    """Test factory functions for creating programs"""

    def test_create_internal_pool(self):
        """Test creating internal pool"""
        program = create_internal_pool(
            program_id="POOL-001",
            program_name="Company Development Fund",
            target_size=Decimal("25000000"),
            committed_amount=Decimal("25000000"),
        )

        assert program.program_type == ProgramType.INTERNAL_POOL
        assert program.status == ProgramStatus.ACTIVE
        assert len(program.sources) == 1
        assert program.total_committed == Decimal("25000000")

    def test_create_external_fund(self):
        """Test creating external fund"""
        program = create_external_fund(
            program_id="FUND-001",
            program_name="Animation Fund I",
            target_size=Decimal("100000000"),
            manager_name="Film Finance Partners",
            management_fee_pct=Decimal("2.0"),
            carry_percentage=Decimal("20.0"),
            hurdle_rate=Decimal("8.0"),
            vintage_year=2024,
        )

        assert program.program_type == ProgramType.EXTERNAL_FUND
        assert program.status == ProgramStatus.PROSPECTIVE
        assert program.manager_name == "Film Finance Partners"
        assert program.management_fee_pct == Decimal("2.0")
        assert program.carry_percentage == Decimal("20.0")
        assert program.hurdle_rate == Decimal("8.0")
        assert program.vintage_year == 2024
        assert program.investment_period_years == 3
        assert program.fund_term_years == 10

    def test_create_output_deal(self):
        """Test creating output deal"""
        program = create_output_deal(
            program_id="OUTPUT-001",
            program_name="Studio Output Deal 2024",
            studio_name="Major Studios",
            commitment=Decimal("150000000"),
            num_pictures=5,
            term_years=5,
        )

        assert program.program_type == ProgramType.OUTPUT_DEAL
        assert program.status == ProgramStatus.ACTIVE
        assert len(program.sources) == 1
        assert program.total_committed == Decimal("150000000")
        assert program.constraints.target_num_projects == 5
        assert "Major Studios" in program.description

    def test_create_spv(self):
        """Test creating SPV"""
        program = create_spv(
            program_id="SPV-001",
            project_name="Sky Warriors",
            project_budget=Decimal("30000000"),
        )

        assert program.program_type == ProgramType.SPV
        assert program.status == ProgramStatus.PROSPECTIVE
        assert program.target_size == Decimal("30000000")
        assert program.constraints.max_single_project_pct == Decimal("100")
        assert program.constraints.target_num_projects == 1
        assert "Sky Warriors" in program.program_name


# ============================================================================
# Test: Program Types
# ============================================================================

class TestProgramTypes:
    """Test all program types"""

    def test_all_program_types_valid(self):
        """All program types can be used to create programs"""
        for program_type in ProgramType:
            program = CapitalProgram(
                program_id=f"PROG-{program_type.value}",
                program_name=f"Test {program_type.value}",
                program_type=program_type,
                target_size=Decimal("10000000"),
            )
            assert program.program_type == program_type

    def test_program_status_transitions(self):
        """Test program status values"""
        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Test Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("50000000"),
        )

        # Test all status values
        for status in ProgramStatus:
            program.status = status
            assert program.status == status

    def test_allocation_status_values(self):
        """Test allocation status values"""
        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Test Project",
            allocated_amount=Decimal("5000000"),
        )

        for status in AllocationStatus:
            deployment.status = status
            assert deployment.status == status


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_program(self):
        """Test program with no sources or deployments"""
        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Empty Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("50000000"),
        )

        assert program.total_committed == Decimal("0")
        assert program.total_available == Decimal("0")
        assert program.deployment_rate == Decimal("0")
        assert program.commitment_progress == Decimal("0")
        assert program.portfolio_multiple is None

    def test_fully_recouped_program(self):
        """Test program where all deployments are recouped"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Main Fund",
            committed_amount=Decimal("10000000"),
            drawn_amount=Decimal("10000000"),
        )

        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Successful Project",
            allocated_amount=Decimal("10000000"),
            funded_amount=Decimal("10000000"),
            recouped_amount=Decimal("10000000"),
            profit_distributed=Decimal("5000000"),
            status=AllocationStatus.RECOUPED,
        )

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Successful Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("10000000"),
            sources=[source],
            deployments=[deployment],
        )

        assert program.portfolio_multiple == Decimal("1.5")
        assert program.total_profit == Decimal("5000000")

    def test_zero_commitment_source(self):
        """Test utilization rate with zero commitment doesn't crash"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Empty Source",
            committed_amount=Decimal("0.01"),  # Minimum valid amount
        )

        assert source.utilization_rate == Decimal("0")

    def test_large_program(self):
        """Test program with large numbers"""
        sources = [
            CapitalSource(
                source_id=f"SRC-{i:03d}",
                source_name=f"LP {i}",
                committed_amount=Decimal("100000000"),  # 100M each
            )
            for i in range(10)
        ]

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Mega Fund",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("1000000000"),  # 1B
            sources=sources,
        )

        assert program.total_committed == Decimal("1000000000")
        assert program.commitment_progress == Decimal("100")


# ============================================================================
# Test: Serialization
# ============================================================================

class TestSerialization:
    """Test serialization methods"""

    def test_full_program_to_dict(self):
        """Test complete program serialization"""
        source = CapitalSource(
            source_id="SRC-001",
            source_name="Main LP",
            committed_amount=Decimal("50000000"),
            drawn_amount=Decimal("20000000"),
            interest_rate=Decimal("8.0"),
        )

        deployment = CapitalDeployment(
            deployment_id="DEP-001",
            program_id="PROG-001",
            project_id="PROJ-001",
            project_name="Project Alpha",
            allocated_amount=Decimal("15000000"),
            funded_amount=Decimal("15000000"),
            equity_percentage=Decimal("30"),
            status=AllocationStatus.FUNDED,
        )

        program = CapitalProgram(
            program_id="PROG-001",
            program_name="Animation Fund I",
            program_type=ProgramType.EXTERNAL_FUND,
            target_size=Decimal("100000000"),
            sources=[source],
            deployments=[deployment],
            manager_name="Film Finance Partners",
            vintage_year=2024,
        )

        data = program.to_dict()

        # Check structure
        assert "program_id" in data
        assert "sources" in data
        assert "deployments" in data
        assert "constraints" in data
        assert "metrics" in data

        # Check values
        assert data["program_id"] == "PROG-001"
        assert len(data["sources"]) == 1
        assert len(data["deployments"]) == 1
        assert data["metrics"]["total_committed"] == "50000000"
        assert data["metrics"]["num_active_projects"] == 1
