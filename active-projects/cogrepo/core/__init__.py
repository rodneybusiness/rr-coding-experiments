"""
CogRepo Core Module

Foundation components shared across the application:
- Custom exceptions for proper error handling
- Logging configuration
- Configuration management with validation
- Type definitions
"""

from .exceptions import (
    CogRepoException,
    ParsingError,
    EnrichmentError,
    StorageError,
    SearchError,
    ConfigurationError,
    ValidationError,
    APIError,
    RateLimitError,
)

from .logging_config import get_logger, setup_logging

__all__ = [
    # Exceptions
    'CogRepoException',
    'ParsingError',
    'EnrichmentError',
    'StorageError',
    'SearchError',
    'ConfigurationError',
    'ValidationError',
    'APIError',
    'RateLimitError',
    # Logging
    'get_logger',
    'setup_logging',
]
