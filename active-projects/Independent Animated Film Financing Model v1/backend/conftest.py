"""
Pytest Configuration

Sets up the Python path for all tests to properly import backend modules.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "api"))

# This allows imports like:
# - from models.deal_block import DealBlock
# - from engines.incentive_calculator import IncentiveCalculator
# - from app.main import app
