"""
Tests for PolicyLoader

Tests policy loading, validation, and error handling.
"""

import pytest
from pathlib import Path
from decimal import Decimal

from backend.engines.incentive_calculator.policy_loader import (
    PolicyLoader,
    PolicyLoadError
)
from backend.models.incentive_policy import IncentivePolicy


# Fixture for policies directory
@pytest.fixture
def policies_dir():
    """Get path to policies directory"""
    base_path = Path(__file__).parent.parent.parent.parent
    return base_path / "data" / "policies"


@pytest.fixture
def loader(policies_dir):
    """Create PolicyLoader instance"""
    return PolicyLoader(policies_dir)


class TestPolicyLoader:
    """Tests for PolicyLoader class"""

    def test_init_valid_directory(self, policies_dir):
        """Test initialization with valid directory"""
        loader = PolicyLoader(policies_dir)
        assert loader.policies_dir == policies_dir
        assert loader.policies_dir.exists()

    def test_init_invalid_directory(self):
        """Test initialization with invalid directory"""
        with pytest.raises(FileNotFoundError):
            PolicyLoader(Path("/nonexistent/directory"))

    def test_init_file_not_directory(self, tmp_path):
        """Test initialization with file instead of directory"""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.touch()

        with pytest.raises(NotADirectoryError):
            PolicyLoader(file_path)

    def test_load_policy_uk_avec(self, loader):
        """Test loading UK AVEC policy"""
        policy = loader.load_policy("UK-AVEC-2025")

        assert isinstance(policy, IncentivePolicy)
        assert policy.policy_id == "UK-AVEC-2025"
        assert policy.jurisdiction == "United Kingdom"
        assert policy.headline_rate == Decimal("39.0")
        assert policy.program_name == "Audio-Visual Expenditure Credit (AVEC)"

    def test_load_policy_canada_federal(self, loader):
        """Test loading Canada Federal CPTC"""
        policy = loader.load_policy("CA-FEDERAL-CPTC-2025")

        assert policy.policy_id == "CA-FEDERAL-CPTC-2025"
        assert policy.jurisdiction == "Canada"
        assert policy.headline_rate == Decimal("25.0")

    def test_load_policy_not_found(self, loader):
        """Test loading non-existent policy"""
        with pytest.raises(FileNotFoundError):
            loader.load_policy("NONEXISTENT-POLICY-2025")

    def test_load_all_policies(self, loader):
        """Test loading all policies"""
        policies = loader.load_all()

        assert len(policies) >= 15  # We have at least 15 policies
        assert all(isinstance(p, IncentivePolicy) for p in policies)

        # Check we have some expected policies
        policy_ids = [p.policy_id for p in policies]
        assert "UK-AVEC-2025" in policy_ids
        assert "CA-QC-PSTC-2025" in policy_ids
        assert "AU-PRODUCER-OFFSET-2025" in policy_ids

    def test_load_by_jurisdiction_canada(self, loader):
        """Test loading all Canadian policies"""
        policies = loader.load_by_jurisdiction("Canada")

        assert len(policies) >= 3  # Federal, Quebec, Ontario
        assert all(p.jurisdiction == "Canada" for p in policies)

        policy_ids = [p.policy_id for p in policies]
        assert "CA-FEDERAL-CPTC-2025" in policy_ids
        assert "CA-QC-PSTC-2025" in policy_ids

    def test_load_by_jurisdiction_australia(self, loader):
        """Test loading Australian policies"""
        policies = loader.load_by_jurisdiction("Australia")

        assert len(policies) >= 2  # Producer Offset, PDV Offset
        assert all(p.jurisdiction == "Australia" for p in policies)

    def test_load_by_jurisdiction_case_insensitive(self, loader):
        """Test jurisdiction search is case-insensitive"""
        policies_upper = loader.load_by_jurisdiction("CANADA")
        policies_lower = loader.load_by_jurisdiction("canada")
        policies_mixed = loader.load_by_jurisdiction("Canada")

        assert len(policies_upper) == len(policies_lower) == len(policies_mixed)

    def test_load_by_jurisdiction_not_found(self, loader):
        """Test loading policies for non-existent jurisdiction"""
        policies = loader.load_by_jurisdiction("NonExistentCountry")
        assert len(policies) == 0

    def test_validate_policies_dir(self, loader):
        """Test validation of all policies"""
        summary = loader.validate_policies_dir()

        assert "total_files" in summary
        assert "valid" in summary
        assert "invalid" in summary
        assert "errors" in summary

        # Should have at least 15 files
        assert summary["total_files"] >= 15

        # Most/all should be valid
        assert summary["valid"] >= 15
        assert summary["invalid"] == 0  # Expecting all to be valid

    def test_get_policy_ids(self, loader):
        """Test getting list of policy IDs"""
        policy_ids = loader.get_policy_ids()

        assert len(policy_ids) >= 15
        assert "UK-AVEC-2025" in policy_ids
        assert "CA-QC-PSTC-2025" in policy_ids
        assert all(isinstance(pid, str) for pid in policy_ids)

        # Should be sorted
        assert policy_ids == sorted(policy_ids)

    def test_policy_data_integrity_uk(self, loader):
        """Test UK AVEC policy data integrity"""
        policy = loader.load_policy("UK-AVEC-2025")

        # Check key fields
        assert policy.headline_rate == Decimal("39.0")
        assert policy.enhanced_rate == Decimal("34.0")
        assert policy.minimum_local_spend == Decimal("10000")
        assert policy.cultural_test.requires_cultural_test is True
        assert policy.cultural_test.minimum_points_required == 16

    def test_policy_data_integrity_quebec(self, loader):
        """Test Quebec PSTC policy data integrity"""
        policy = loader.load_policy("CA-QC-PSTC-2025")

        # Check animation-specific rate
        assert policy.headline_rate == Decimal("36.0")
        assert "animation" in policy.notes.lower()
        assert policy.jurisdiction == "Canada"

    def test_policy_qpe_definition(self, loader):
        """Test QPE definition structure"""
        policy = loader.load_policy("UK-AVEC-2025")

        qpe = policy.qpe_definition
        assert len(qpe.included_categories) > 0
        assert qpe.excludes_financing_costs is True
        assert qpe.excludes_distribution_costs is True

    def test_policy_cultural_test_structure(self, loader):
        """Test cultural test structure"""
        # UK has cultural test
        uk_policy = loader.load_policy("UK-AVEC-2025")
        assert uk_policy.cultural_test.requires_cultural_test is True
        assert uk_policy.cultural_test.test_name is not None

        # Georgia doesn't have cultural test
        ga_policy = loader.load_policy("US-GA-GEFA-2025")
        assert ga_policy.cultural_test.requires_cultural_test is False

    def test_policy_monetization_methods(self, loader):
        """Test monetization methods structure"""
        # Georgia has transferable credit
        ga_policy = loader.load_policy("US-GA-GEFA-2025")
        assert len(ga_policy.monetization_methods) > 0

        # UK has refundable credit
        uk_policy = loader.load_policy("UK-AVEC-2025")
        assert len(uk_policy.monetization_methods) > 0

    def test_policy_timing_data(self, loader):
        """Test timing data is present"""
        policy = loader.load_policy("UK-AVEC-2025")

        assert policy.timing_months_audit_to_certification is not None
        assert policy.timing_months_certification_to_cash is not None
        assert isinstance(policy.timing_months_audit_to_certification, int)
        assert isinstance(policy.timing_months_certification_to_cash, int)

    def test_all_policies_have_required_fields(self, loader):
        """Test all policies have required fields"""
        policies = loader.load_all()

        for policy in policies:
            assert policy.policy_id
            assert policy.jurisdiction
            assert policy.program_name
            assert policy.headline_rate >= 0
            assert policy.incentive_type
            assert len(policy.monetization_methods) > 0
            assert policy.last_updated
