"""
Standardized Exception Handling

Provides consistent error responses across all API endpoints.
"""

from fastapi import HTTPException, status
from typing import Optional, Any


def raise_not_found(resource: str, identifier: str) -> None:
    """Raise 404 Not Found error."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found: {identifier}"
    )


def raise_bad_request(message: str, field: Optional[str] = None) -> None:
    """Raise 400 Bad Request error."""
    detail = f"Invalid {field}: {message}" if field else message
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )


def raise_validation_error(message: str) -> None:
    """Raise 400 Bad Request for validation errors."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Validation error: {message}"
    )


def raise_server_error(operation: str, error: Exception) -> None:
    """Raise 500 Internal Server Error."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"{operation} failed: {str(error)}"
    )


class APIError(HTTPException):
    """Base class for API errors with consistent formatting."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details
            } if details else {
                "code": code,
                "message": message
            }
        )


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"{resource} not found: {identifier}"
        )


class ValidationError(APIError):
    """Validation error."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            message=message,
            details={"field": field} if field else None
        )


class BusinessLogicError(APIError):
    """Business logic violation error."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BUSINESS_LOGIC_ERROR",
            message=message,
            details=details
        )
