"""
Path Setup Module

Configures Python path to enable imports from backend root packages
(models, engines, data) when running the API.

This module should be imported once at application startup before
any endpoint modules that need access to backend packages.
"""

import sys
from pathlib import Path

# Backend root is 4 levels up from this file (core/path_setup.py)
# api/app/core/path_setup.py -> backend/
_backend_root = Path(__file__).parent.parent.parent.parent

# Only add to path if not already present
_backend_root_str = str(_backend_root)
if _backend_root_str not in sys.path:
    sys.path.insert(0, _backend_root_str)

# Export for reference by other modules if needed
BACKEND_ROOT = _backend_root
