"""
Policy Loader

Loads tax incentive policy JSON files into validated IncentivePolicy Pydantic objects.
Handles file I/O, JSON parsing, and validation with detailed error reporting.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from pydantic import ValidationError

from backend.models.incentive_policy import IncentivePolicy


logger = logging.getLogger(__name__)


class PolicyLoadError(Exception):
    """Raised when policy loading fails"""
    pass


class PolicyLoader:
    """
    Loads and validates tax incentive policies from JSON files.

    The loader reads policy files from a specified directory and converts them
    into validated IncentivePolicy Pydantic objects. It handles file I/O,
    JSON parsing, and validation errors with detailed reporting.

    Attributes:
        policies_dir: Path to directory containing policy JSON files
    """

    def __init__(self, policies_dir: Path):
        """
        Initialize loader with path to policies directory.

        Args:
            policies_dir: Path object pointing to directory with policy JSON files

        Raises:
            FileNotFoundError: If policies_dir doesn't exist
            NotADirectoryError: If policies_dir is not a directory
        """
        self.policies_dir = Path(policies_dir)

        if not self.policies_dir.exists():
            raise FileNotFoundError(f"Policies directory not found: {self.policies_dir}")

        if not self.policies_dir.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.policies_dir}")

        logger.info(f"PolicyLoader initialized with directory: {self.policies_dir}")

    def load_policy(self, policy_id: str) -> IncentivePolicy:
        """
        Load a single policy by ID.

        Args:
            policy_id: Policy identifier (e.g., "UK-AVEC-2025")

        Returns:
            Validated IncentivePolicy object

        Raises:
            FileNotFoundError: If policy file doesn't exist
            PolicyLoadError: If JSON parsing or validation fails
        """
        # Construct file path
        file_path = self.policies_dir / f"{policy_id}.json"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Policy file not found: {file_path}\n"
                f"Expected policy_id: {policy_id}"
            )

        try:
            # Read and parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate with Pydantic
            policy = IncentivePolicy(**data)

            logger.info(f"Successfully loaded policy: {policy_id}")
            return policy

        except json.JSONDecodeError as e:
            raise PolicyLoadError(
                f"Invalid JSON in policy file: {file_path}\n"
                f"Error at line {e.lineno}, column {e.colno}: {e.msg}"
            ) from e

        except ValidationError as e:
            raise PolicyLoadError(
                f"Validation error for policy: {policy_id}\n"
                f"File: {file_path}\n"
                f"Errors:\n{e}"
            ) from e

        except Exception as e:
            raise PolicyLoadError(
                f"Unexpected error loading policy: {policy_id}\n"
                f"File: {file_path}\n"
                f"Error: {e}"
            ) from e

    def load_all(self) -> List[IncentivePolicy]:
        """
        Load all policies from the policies directory.

        Only processes files with .json extension. Logs warnings for files
        that fail to load but continues processing remaining files.

        Returns:
            List of validated IncentivePolicy objects
        """
        policies = []
        json_files = list(self.policies_dir.glob("*.json"))

        if not json_files:
            logger.warning(f"No JSON files found in: {self.policies_dir}")
            return policies

        logger.info(f"Found {len(json_files)} policy files to load")

        for file_path in json_files:
            policy_id = file_path.stem  # Filename without extension

            try:
                policy = self.load_policy(policy_id)
                policies.append(policy)
            except (FileNotFoundError, PolicyLoadError) as e:
                logger.warning(f"Skipping policy {policy_id}: {e}")
                continue

        logger.info(f"Successfully loaded {len(policies)} policies")
        return policies

    def load_by_jurisdiction(self, jurisdiction: str) -> List[IncentivePolicy]:
        """
        Load all policies for a specific jurisdiction.

        Args:
            jurisdiction: Country or region name (e.g., "Canada", "United Kingdom")

        Returns:
            List of IncentivePolicy objects for that jurisdiction
        """
        all_policies = self.load_all()

        # Filter by jurisdiction (case-insensitive)
        jurisdiction_lower = jurisdiction.lower()
        matching_policies = [
            p for p in all_policies
            if p.jurisdiction.lower() == jurisdiction_lower
        ]

        logger.info(
            f"Found {len(matching_policies)} policies for jurisdiction: {jurisdiction}"
        )

        return matching_policies

    def validate_policies_dir(self) -> Dict[str, Any]:
        """
        Validate all policy files in directory.

        Attempts to load each JSON file and reports validation status.
        Useful for auditing data quality and identifying issues.

        Returns:
            Dict with validation summary:
            {
                "total_files": int,
                "valid": int,
                "invalid": int,
                "errors": List[Dict[str, str]]  # {"policy_id": ..., "error": ...}
            }
        """
        json_files = list(self.policies_dir.glob("*.json"))

        summary = {
            "total_files": len(json_files),
            "valid": 0,
            "invalid": 0,
            "errors": []
        }

        for file_path in json_files:
            policy_id = file_path.stem

            try:
                self.load_policy(policy_id)
                summary["valid"] += 1
            except (FileNotFoundError, PolicyLoadError) as e:
                summary["invalid"] += 1
                summary["errors"].append({
                    "policy_id": policy_id,
                    "file_path": str(file_path),
                    "error": str(e)
                })

        logger.info(
            f"Validation complete: {summary['valid']} valid, "
            f"{summary['invalid']} invalid out of {summary['total_files']} files"
        )

        return summary

    def get_policy_ids(self) -> List[str]:
        """
        Get list of all available policy IDs (without loading full policies).

        Returns:
            List of policy IDs (filenames without .json extension)
        """
        json_files = list(self.policies_dir.glob("*.json"))
        policy_ids = [f.stem for f in json_files]

        logger.info(f"Found {len(policy_ids)} policy IDs")
        return sorted(policy_ids)
