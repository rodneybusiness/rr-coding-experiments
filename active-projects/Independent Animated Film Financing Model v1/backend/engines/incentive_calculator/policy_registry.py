"""
Policy Registry

In-memory registry for fast policy lookup and search operations.
Provides indexed access to loaded policies with various query methods.
"""

import logging
from typing import Dict, List, Optional
from decimal import Decimal

from models.incentive_policy import (
    IncentivePolicy,
    IncentiveType,
    MonetizationMethod,
)
from .policy_loader import PolicyLoader


logger = logging.getLogger(__name__)


class PolicyRegistry:
    """
    Registry for managing loaded policies with fast lookup.

    The registry loads all policies on initialization and maintains
    multiple indexes for efficient querying:
    - By policy_id (O(1) lookup)
    - By jurisdiction (grouped)
    - By incentive type

    Attributes:
        loader: PolicyLoader instance
        _policies_by_id: Dict mapping policy_id to IncentivePolicy
        _policies_by_jurisdiction: Dict mapping jurisdiction to list of policies
        _all_policies: List of all loaded policies
    """

    def __init__(self, loader: PolicyLoader):
        """
        Initialize registry with PolicyLoader and load all policies.

        Args:
            loader: PolicyLoader instance configured with policies directory
        """
        self.loader = loader
        self._policies_by_id: Dict[str, IncentivePolicy] = {}
        self._policies_by_jurisdiction: Dict[str, List[IncentivePolicy]] = {}
        self._all_policies: List[IncentivePolicy] = []

        # Load all policies on initialization
        self.reload()

    def reload(self):
        """
        Reload all policies from disk.

        Clears existing indexes and rebuilds them from scratch.
        Useful if policy files have been updated.
        """
        logger.info("Reloading policies from disk")

        # Clear existing data
        self._policies_by_id.clear()
        self._policies_by_jurisdiction.clear()
        self._all_policies.clear()

        # Load all policies
        policies = self.loader.load_all()
        self._all_policies = policies

        # Build indexes
        for policy in policies:
            # Index by ID
            self._policies_by_id[policy.policy_id] = policy

            # Index by jurisdiction
            jurisdiction = policy.jurisdiction
            if jurisdiction not in self._policies_by_jurisdiction:
                self._policies_by_jurisdiction[jurisdiction] = []
            self._policies_by_jurisdiction[jurisdiction].append(policy)

        logger.info(
            f"Registry loaded {len(policies)} policies from "
            f"{len(self._policies_by_jurisdiction)} jurisdictions"
        )

    def get_by_id(self, policy_id: str) -> Optional[IncentivePolicy]:
        """
        Retrieve policy by ID.

        Args:
            policy_id: Policy identifier (e.g., "UK-AVEC-2025")

        Returns:
            IncentivePolicy if found, None otherwise
        """
        return self._policies_by_id.get(policy_id)

    def get_by_jurisdiction(self, jurisdiction: str) -> List[IncentivePolicy]:
        """
        Retrieve all policies for a jurisdiction.

        Args:
            jurisdiction: Country or region name (case-sensitive)

        Returns:
            List of IncentivePolicy objects (empty list if none found)
        """
        return self._policies_by_jurisdiction.get(jurisdiction, [])

    def search(
        self,
        incentive_type: Optional[IncentiveType] = None,
        min_rate: Optional[Decimal] = None,
        max_rate: Optional[Decimal] = None,
        monetization_method: Optional[MonetizationMethod] = None,
        requires_cultural_test: Optional[bool] = None,
        jurisdiction: Optional[str] = None,
    ) -> List[IncentivePolicy]:
        """
        Search policies by criteria.

        All provided criteria are combined with AND logic.
        If no criteria provided, returns all policies.

        Args:
            incentive_type: Filter by type (refundable_tax_credit, rebate, etc.)
            min_rate: Minimum headline rate (inclusive)
            max_rate: Maximum headline rate (inclusive)
            monetization_method: Must support this monetization method
            requires_cultural_test: True/False to filter by cultural test requirement
            jurisdiction: Filter by jurisdiction (case-sensitive)

        Returns:
            List of policies matching ALL criteria
        """
        results = self._all_policies.copy()

        # Apply filters
        if incentive_type is not None:
            results = [p for p in results if p.incentive_type == incentive_type]

        if min_rate is not None:
            results = [p for p in results if p.headline_rate >= min_rate]

        if max_rate is not None:
            results = [p for p in results if p.headline_rate <= max_rate]

        if monetization_method is not None:
            results = [
                p for p in results
                if monetization_method in p.monetization_methods
            ]

        if requires_cultural_test is not None:
            results = [
                p for p in results
                if p.cultural_test.requires_cultural_test == requires_cultural_test
            ]

        if jurisdiction is not None:
            results = [p for p in results if p.jurisdiction == jurisdiction]

        logger.info(f"Search returned {len(results)} policies")
        return results

    def get_stackable_policies(
        self,
        jurisdiction: Optional[str] = None
    ) -> Dict[str, List[IncentivePolicy]]:
        """
        Identify stackable policy combinations.

        Known stackable combinations:
        - Canada: Federal CPTC + Provincial (Quebec PSTC, Ontario OCASE)
        - Australia: Producer Offset + PDV Offset

        Args:
            jurisdiction: Optional filter by jurisdiction

        Returns:
            Dict mapping jurisdiction/program name to list of stackable policies
            Example: {
                "Canada-Quebec": [CPTC, PSTC],
                "Australia": [Producer-Offset, PDV-Offset]
            }
        """
        stackable = {}

        # Canada: Federal + Provincial stacking
        canada_federal = self.get_by_id("CA-FEDERAL-CPTC-2025")
        if canada_federal:
            # Quebec
            quebec_pstc = self.get_by_id("CA-QC-PSTC-2025")
            if quebec_pstc:
                stackable["Canada-Quebec"] = [canada_federal, quebec_pstc]

            # Ontario
            ontario_ocase = self.get_by_id("CA-ON-OCASE-2025")
            if ontario_ocase:
                stackable["Canada-Ontario"] = [canada_federal, ontario_ocase]

        # Australia: Producer Offset + PDV Offset
        au_producer = self.get_by_id("AU-PRODUCER-OFFSET-2025")
        au_pdv = self.get_by_id("AU-PDV-OFFSET-2025")
        if au_producer and au_pdv:
            stackable["Australia"] = [au_producer, au_pdv]

        # Filter by jurisdiction if provided
        if jurisdiction:
            stackable = {
                k: v for k, v in stackable.items()
                if jurisdiction.lower() in k.lower()
            }

        logger.info(f"Found {len(stackable)} stackable policy combinations")
        return stackable

    def get_all(self) -> List[IncentivePolicy]:
        """
        Return all loaded policies.

        Returns:
            List of all IncentivePolicy objects
        """
        return self._all_policies.copy()

    def get_jurisdictions(self) -> List[str]:
        """
        Get list of all jurisdictions with policies.

        Returns:
            Sorted list of jurisdiction names
        """
        return sorted(self._policies_by_jurisdiction.keys())

    def get_summary(self) -> Dict[str, any]:
        """
        Get summary statistics about loaded policies.

        Returns:
            Dict with summary stats:
            {
                "total_policies": int,
                "jurisdictions": int,
                "by_type": Dict[IncentiveType, int],
                "by_jurisdiction": Dict[str, int],
                "average_rate": Decimal,
                "rate_range": (Decimal, Decimal)
            }
        """
        summary = {
            "total_policies": len(self._all_policies),
            "jurisdictions": len(self._policies_by_jurisdiction),
            "by_type": {},
            "by_jurisdiction": {},
            "average_rate": Decimal("0"),
            "rate_range": (Decimal("0"), Decimal("0"))
        }

        if not self._all_policies:
            return summary

        # Count by jurisdiction (include sub-national regions from policy IDs)
        regional_keys = set()
        for policy in self._all_policies:
            policy_type = policy.incentive_type
            summary["by_type"][policy_type] = summary["by_type"].get(policy_type, 0) + 1

            parts = policy.policy_id.split("-")
            if len(parts) > 2:
                regional_keys.add(f"{policy.jurisdiction}:{parts[1]}")

        for jurisdiction, policies in self._policies_by_jurisdiction.items():
            summary["by_jurisdiction"][jurisdiction] = len(policies)

        jurisdiction_keys = set(self._policies_by_jurisdiction.keys()) | regional_keys
        summary["jurisdictions"] = len(jurisdiction_keys)

        # Calculate rate statistics
        rates = [p.headline_rate for p in self._all_policies]
        summary["average_rate"] = sum(rates) / len(rates)
        summary["rate_range"] = (min(rates), max(rates))

        return summary
