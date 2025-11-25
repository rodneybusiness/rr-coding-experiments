"""
API Integration Tests for Capital Programs (Engine 5)

Comprehensive tests for the Capital Programs REST API endpoints.
Tests cover CRUD operations, allocation workflows, and constraint validation.
"""

import pytest
from decimal import Decimal
from datetime import date


class TestCapitalProgramEndpoints:
    """Tests for capital program CRUD operations"""

    def test_create_program_success(self, client):
        """Test creating a valid capital program"""
        payload = {
            "program_name": "Animation Fund I",
            "program_type": "external_fund",
            "target_size": "50000000",
            "manager_name": "Film Finance Partners",
            "management_fee_pct": "2.0",
            "carry_percentage": "20.0",
            "hurdle_rate": "8.0",
            "vintage_year": 2024
        }

        response = client.post("/api/v1/capital-programs", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["program_name"] == "Animation Fund I"
        assert data["program_type"] == "external_fund"
        assert data["status"] == "prospective"
        assert "program_id" in data
        assert "metrics" in data

    def test_create_program_with_constraints(self, client):
        """Test creating program with portfolio constraints"""
        payload = {
            "program_name": "Constrained Fund",
            "program_type": "private_equity",
            "target_size": "100000000",
            "constraints": {
                "max_single_project_pct": "20",
                "max_single_counterparty_pct": "35",
                "min_project_budget": "5000000",
                "max_project_budget": "50000000",
                "prohibited_jurisdictions": ["Russia", "Belarus"],
                "required_genres": ["Animation", "Family"],
                "max_development_pct": "25"
            }
        }

        response = client.post("/api/v1/capital-programs", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["constraints"] is not None

    def test_create_program_invalid_type(self, client):
        """Test that invalid program type is rejected"""
        payload = {
            "program_name": "Invalid Fund",
            "program_type": "invalid_type",
            "target_size": "50000000"
        }

        response = client.post("/api/v1/capital-programs", json=payload)

        assert response.status_code == 422

    def test_create_program_missing_required(self, client):
        """Test that missing required fields are rejected"""
        payload = {
            "program_name": "Incomplete Fund"
            # Missing program_type and target_size
        }

        response = client.post("/api/v1/capital-programs", json=payload)

        assert response.status_code == 422

    def test_get_program(self, client, sample_program_id):
        """Test retrieving a program by ID"""
        response = client.get(f"/api/v1/capital-programs/{sample_program_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["program_id"] == sample_program_id

    def test_get_program_not_found(self, client):
        """Test 404 for non-existent program"""
        response = client.get("/api/v1/capital-programs/nonexistent-id")

        assert response.status_code == 404

    def test_list_programs(self, client, sample_program_id):
        """Test listing all programs"""
        response = client.get("/api/v1/capital-programs")

        assert response.status_code == 200
        data = response.json()
        assert "programs" in data
        assert "total_count" in data
        assert data["total_count"] >= 1

    def test_list_programs_filter_by_type(self, client, sample_program_id):
        """Test filtering programs by type"""
        response = client.get("/api/v1/capital-programs?program_type=external_fund")

        assert response.status_code == 200
        data = response.json()
        for program in data["programs"]:
            assert program["program_type"] == "external_fund"

    def test_list_programs_filter_by_status(self, client, sample_program_id):
        """Test filtering programs by status"""
        response = client.get("/api/v1/capital-programs?status=active")

        assert response.status_code == 200

    def test_delete_program(self, client):
        """Test deleting a program"""
        # First create a program to delete
        create_response = client.post("/api/v1/capital-programs", json={
            "program_name": "To Delete",
            "program_type": "spv",
            "target_size": "10000000"
        })
        program_id = create_response.json()["program_id"]

        # Delete it
        response = client.delete(f"/api/v1/capital-programs/{program_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/v1/capital-programs/{program_id}")
        assert get_response.status_code == 404


class TestCapitalSourceEndpoints:
    """Tests for capital source management within programs"""

    def test_add_source_success(self, client, sample_program_id):
        """Test adding a capital source to a program"""
        payload = {
            "source_name": "LP Commitment A",
            "source_type": "lp_commitment",
            "committed_amount": "10000000",
            "interest_rate": "8.0",
            "geographic_restrictions": ["United States", "Canada"]
        }

        response = client.post(
            f"/api/v1/capital-programs/{sample_program_id}/sources",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["source_name"] == "LP Commitment A"
        assert data["committed_amount"] == 10000000
        assert data["available_amount"] == 10000000
        assert data["utilization_rate"] == 0

    def test_add_source_with_restrictions(self, client, sample_program_id):
        """Test adding source with budget and genre restrictions"""
        payload = {
            "source_name": "Restricted LP",
            "source_type": "lp_commitment",
            "committed_amount": "20000000",
            "budget_range_min": "10000000",
            "budget_range_max": "40000000",
            "genre_restrictions": ["Animation", "Family", "Comedy"]
        }

        response = client.post(
            f"/api/v1/capital-programs/{sample_program_id}/sources",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["genre_restrictions"]) == 3

    def test_add_source_invalid_amount(self, client, sample_program_id):
        """Test that negative/zero amounts are rejected"""
        payload = {
            "source_name": "Invalid Source",
            "source_type": "general",
            "committed_amount": "0"
        }

        response = client.post(
            f"/api/v1/capital-programs/{sample_program_id}/sources",
            json=payload
        )

        assert response.status_code == 422

    def test_remove_source(self, client, sample_program_id):
        """Test removing a capital source"""
        # First add a source
        add_response = client.post(
            f"/api/v1/capital-programs/{sample_program_id}/sources",
            json={
                "source_name": "To Remove",
                "source_type": "general",
                "committed_amount": "5000000"
            }
        )
        source_id = add_response.json()["source_id"]

        # Remove it
        response = client.delete(
            f"/api/v1/capital-programs/{sample_program_id}/sources/{source_id}"
        )

        assert response.status_code == 204


class TestAllocationEndpoints:
    """Tests for capital allocation to projects"""

    def test_allocate_capital_success(self, client, sample_program_with_source):
        """Test successful capital allocation"""
        program_id = sample_program_with_source["program_id"]
        payload = {
            "project_id": "PROJ-001",
            "project_name": "Sky Warriors",
            "requested_amount": "5000000",
            "project_budget": "30000000",
            "jurisdiction": "Canada",
            "genre": "Animation",
            "equity_percentage": "16.67"
        }

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/allocate",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["allocation_id"] is not None
        assert data["deployment"] is not None
        assert data["deployment"]["allocated_amount"] == 5000000

    def test_allocate_capital_constraint_violation(self, client, sample_constrained_program):
        """Test allocation blocked by hard constraints"""
        program_id = sample_constrained_program["program_id"]
        # Try to allocate to prohibited jurisdiction
        payload = {
            "project_id": "PROJ-BAD",
            "project_name": "Blocked Project",
            "requested_amount": "5000000",
            "project_budget": "30000000",
            "jurisdiction": "Russia"  # Prohibited
        }

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/allocate",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert len(data["violations"]) > 0
        assert any(v["constraint_name"] == "prohibited_jurisdiction" for v in data["violations"])

    def test_allocate_capital_exceeds_available(self, client, sample_program_with_source):
        """Test allocation exceeding available capital"""
        program_id = sample_program_with_source["program_id"]
        # Request more than available
        payload = {
            "project_id": "PROJ-BIG",
            "project_name": "Too Big Project",
            "requested_amount": "100000000",  # More than committed
            "project_budget": "200000000"
        }

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/allocate",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        # Should either fail or warn about insufficient capital
        assert data["success"] is False or len(data["warnings"]) > 0

    def test_allocate_with_source_selection(self, client, sample_program_with_multiple_sources):
        """Test automatic source selection"""
        program_id = sample_program_with_multiple_sources["program_id"]
        payload = {
            "project_id": "PROJ-AUTO",
            "project_name": "Auto Source Selection",
            "requested_amount": "5000000",
            "project_budget": "25000000",
            "jurisdiction": "Canada"
        }

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/allocate",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        if data["success"]:
            assert data["selected_source_id"] is not None
            assert data["source_selection_reason"] is not None


class TestDeploymentLifecycleEndpoints:
    """Tests for deployment lifecycle management"""

    def test_fund_deployment(self, client, sample_program_with_allocation):
        """Test funding a pending deployment"""
        program_id = sample_program_with_allocation["program_id"]
        deployment_id = sample_program_with_allocation["deployment_id"]

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/deployments/{deployment_id}/fund",
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "funded"
        assert data["funded_amount"] > 0

    def test_fund_deployment_partial(self, client, sample_program_with_allocation):
        """Test partial funding"""
        program_id = sample_program_with_allocation["program_id"]
        deployment_id = sample_program_with_allocation["deployment_id"]

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/deployments/{deployment_id}/fund",
            json={"amount": "1000000"}  # Partial amount
        )

        assert response.status_code == 200
        data = response.json()
        assert data["funded_amount"] == 1000000

    def test_record_recoupment(self, client, sample_funded_deployment):
        """Test recording recoupment"""
        program_id = sample_funded_deployment["program_id"]
        deployment_id = sample_funded_deployment["deployment_id"]

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/deployments/{deployment_id}/recoup",
            json={
                "recouped_amount": "3000000",
                "profit_amount": "500000"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["recouped_amount"] == 3000000
        assert data["profit_distributed"] == 500000


class TestPortfolioMetricsEndpoints:
    """Tests for portfolio metrics and analytics"""

    def test_get_portfolio_metrics(self, client, sample_program_with_deployments):
        """Test retrieving portfolio metrics"""
        program_id = sample_program_with_deployments["program_id"]

        response = client.get(
            f"/api/v1/capital-programs/{program_id}/metrics"
        )

        assert response.status_code == 200
        data = response.json()
        assert "size_metrics" in data
        assert "project_metrics" in data
        assert "concentration_metrics" in data
        assert "performance_metrics" in data
        assert "risk_metrics" in data
        assert "constraint_compliance" in data

    def test_get_program_types(self, client):
        """Test listing available program types"""
        response = client.get("/api/v1/capital-programs/types")

        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert len(data["types"]) >= 10  # At least 10 program types


class TestValidationEndpoints:
    """Tests for allocation validation (dry run)"""

    def test_validate_allocation_passes(self, client, sample_program_with_source):
        """Test validation passes for valid allocation"""
        program_id = sample_program_with_source["program_id"]
        payload = {
            "allocation": {
                "project_id": "PROJ-VAL",
                "project_name": "Validation Test",
                "requested_amount": "5000000",
                "project_budget": "30000000"
            },
            "dry_run": True
        }

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/validate",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        # Should pass validation
        assert len(data.get("violations", [])) == 0 or data.get("success") is True

    def test_validate_allocation_fails(self, client, sample_constrained_program):
        """Test validation fails for constraint-violating allocation"""
        program_id = sample_constrained_program["program_id"]
        payload = {
            "allocation": {
                "project_id": "PROJ-FAIL",
                "project_name": "Should Fail Validation",
                "requested_amount": "100000000",  # Too large
                "project_budget": "200000000"  # Exceeds max
            },
            "dry_run": True
        }

        response = client.post(
            f"/api/v1/capital-programs/{program_id}/validate",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        # Should have violations
        assert len(data.get("violations", [])) > 0 or data.get("success") is False


# === Fixtures ===

@pytest.fixture
def client():
    """Create test client"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_program_id(client):
    """Create a sample program and return its ID"""
    response = client.post("/api/v1/capital-programs", json={
        "program_name": "Test Fund",
        "program_type": "external_fund",
        "target_size": "50000000",
        "vintage_year": 2024
    })
    return response.json()["program_id"]


@pytest.fixture
def sample_program_with_source(client, sample_program_id):
    """Create program with a capital source"""
    client.post(
        f"/api/v1/capital-programs/{sample_program_id}/sources",
        json={
            "source_name": "Test LP",
            "source_type": "lp_commitment",
            "committed_amount": "25000000"
        }
    )
    response = client.get(f"/api/v1/capital-programs/{sample_program_id}")
    return response.json()


@pytest.fixture
def sample_constrained_program(client):
    """Create program with strict constraints"""
    response = client.post("/api/v1/capital-programs", json={
        "program_name": "Constrained Fund",
        "program_type": "private_equity",
        "target_size": "50000000",
        "constraints": {
            "max_single_project_pct": "20",
            "max_project_budget": "40000000",
            "prohibited_jurisdictions": ["Russia", "Belarus", "North Korea"]
        }
    })
    program_id = response.json()["program_id"]

    # Add source
    client.post(
        f"/api/v1/capital-programs/{program_id}/sources",
        json={
            "source_name": "Constrained LP",
            "source_type": "lp_commitment",
            "committed_amount": "50000000"
        }
    )

    return client.get(f"/api/v1/capital-programs/{program_id}").json()


@pytest.fixture
def sample_program_with_multiple_sources(client):
    """Create program with multiple sources having different restrictions"""
    response = client.post("/api/v1/capital-programs", json={
        "program_name": "Multi-Source Fund",
        "program_type": "external_fund",
        "target_size": "100000000"
    })
    program_id = response.json()["program_id"]

    # Add US-focused source
    client.post(
        f"/api/v1/capital-programs/{program_id}/sources",
        json={
            "source_name": "US LP",
            "source_type": "lp_commitment",
            "committed_amount": "30000000",
            "geographic_restrictions": ["United States"]
        }
    )

    # Add Canada-focused source
    client.post(
        f"/api/v1/capital-programs/{program_id}/sources",
        json={
            "source_name": "Canada LP",
            "source_type": "lp_commitment",
            "committed_amount": "20000000",
            "geographic_restrictions": ["Canada"],
            "interest_rate": "6.0"
        }
    )

    # Add general source
    client.post(
        f"/api/v1/capital-programs/{program_id}/sources",
        json={
            "source_name": "General LP",
            "source_type": "lp_commitment",
            "committed_amount": "50000000"
        }
    )

    return client.get(f"/api/v1/capital-programs/{program_id}").json()


@pytest.fixture
def sample_program_with_allocation(client, sample_program_with_source):
    """Create program with a pending allocation"""
    program_id = sample_program_with_source["program_id"]

    alloc_response = client.post(
        f"/api/v1/capital-programs/{program_id}/allocate",
        json={
            "project_id": "PROJ-ALLOC",
            "project_name": "Allocated Project",
            "requested_amount": "5000000",
            "project_budget": "30000000"
        }
    )

    return {
        "program_id": program_id,
        "deployment_id": alloc_response.json().get("allocation_id")
    }


@pytest.fixture
def sample_funded_deployment(client, sample_program_with_allocation):
    """Create program with a funded deployment"""
    program_id = sample_program_with_allocation["program_id"]
    deployment_id = sample_program_with_allocation["deployment_id"]

    client.post(
        f"/api/v1/capital-programs/{program_id}/deployments/{deployment_id}/fund",
        json={}
    )

    return {
        "program_id": program_id,
        "deployment_id": deployment_id
    }


@pytest.fixture
def sample_program_with_deployments(client):
    """Create program with multiple deployments at various stages"""
    response = client.post("/api/v1/capital-programs", json={
        "program_name": "Multi-Deployment Fund",
        "program_type": "external_fund",
        "target_size": "100000000"
    })
    program_id = response.json()["program_id"]

    # Add source
    client.post(
        f"/api/v1/capital-programs/{program_id}/sources",
        json={
            "source_name": "Main LP",
            "source_type": "lp_commitment",
            "committed_amount": "100000000"
        }
    )

    # Add several deployments
    for i in range(3):
        alloc_response = client.post(
            f"/api/v1/capital-programs/{program_id}/allocate",
            json={
                "project_id": f"PROJ-{i:03d}",
                "project_name": f"Project {i + 1}",
                "requested_amount": str((i + 1) * 5000000),
                "project_budget": str((i + 1) * 30000000)
            }
        )
        if alloc_response.json().get("success"):
            deployment_id = alloc_response.json()["allocation_id"]
            # Fund first deployment
            if i == 0:
                client.post(
                    f"/api/v1/capital-programs/{program_id}/deployments/{deployment_id}/fund",
                    json={}
                )

    return {"program_id": program_id}
