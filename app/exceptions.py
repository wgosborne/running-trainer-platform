"""
Custom exception classes for the application.

This module defines a hierarchy of exceptions that represent different
failure modes in the application. These exceptions can be caught and
handled appropriately by error handlers in the API layer.

Each exception includes:
- error_code: Machine-readable identifier
- error_id: Unique ID for tracking this specific error occurrence
- message: Human-readable description
- details: Additional context
"""

from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class AppException(Exception):
    """
    Base exception class for all application-specific exceptions.

    All custom exceptions should inherit from this class to allow
    for centralized exception handling and consistent error tracking.

    Attributes:
        message: Human-readable error description
        error_code: Machine-readable error identifier
        error_id: Unique ID for this error occurrence (for tracking/debugging)
        details: Additional context information
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        error_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for clients
            error_id: Unique error ID (generated if not provided)
            details: Additional context about the error
        """
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.error_id = error_id or uuid4()
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        return f"[{self.error_code}:{self.error_id}] {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format.

        Returns:
            Dictionary containing error information
        """
        return {
            "error_code": self.error_code,
            "error_id": str(self.error_id),
            "message": self.message,
            "details": self.details
        }


class ValidationError(AppException):
    """
    Exception raised when business logic validation fails.

    This is distinct from Pydantic validation errors and represents
    domain-specific validation rules (e.g., "pace must be slower than
    world record pace", "plan cannot be completed before it's started").

    HTTP Status: 400 Bad Request
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Description of what validation failed
            field: Name of the field that failed validation
            details: Additional context about the validation failure
        """
        error_details = details or {}
        if field:
            error_details["field"] = field

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details
        )


class NotFoundError(AppException):
    """
    Exception raised when a requested resource is not found.

    Examples:
    - Training plan with given ID doesn't exist
    - Workout with given ID doesn't exist
    - Run with given ID doesn't exist

    HTTP Status: 404 Not Found
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize not found error.

        Args:
            resource_type: Type of resource (e.g., "TrainingPlan", "Workout")
            resource_id: ID of the resource that wasn't found
            details: Additional context
        """
        message = f"{resource_type} with ID '{resource_id}' not found"
        error_details = details or {}
        error_details.update({
            "resource_type": resource_type,
            "resource_id": str(resource_id)
        })

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details=error_details
        )


class ConflictError(AppException):
    """
    Exception raised when an operation conflicts with current state.

    Examples:
    - Trying to activate a plan when another plan is already active
    - Trying to complete a plan that's not active
    - Attempting to create a duplicate resource

    HTTP Status: 409 Conflict
    """

    def __init__(
        self,
        message: str,
        conflicting_resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize conflict error.

        Args:
            message: Description of the conflict
            conflicting_resource: Identifier of the conflicting resource
            details: Additional context about the conflict
        """
        error_details = details or {}
        if conflicting_resource:
            error_details["conflicting_resource"] = conflicting_resource

        super().__init__(
            message=message,
            error_code="CONFLICT",
            details=error_details
        )


class DatabaseError(AppException):
    """
    Exception raised when a database operation fails.

    This wraps lower-level database errors to provide a consistent
    error interface. The original exception should be logged but
    not exposed to the client for security reasons.

    Examples:
    - Connection timeout
    - Transaction rollback
    - Integrity constraint violation
    - Deadlock

    HTTP Status: 500 Internal Server Error (or 503 Service Unavailable for connection issues)
    """

    def __init__(
        self,
        message: str = "A database error occurred",
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize database error.

        Args:
            message: High-level description of the error
            operation: Name of the operation that failed (e.g., "create_plan")
            details: Additional context (should not include sensitive data)
        """
        error_details = details or {}
        if operation:
            error_details["operation"] = operation

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=error_details
        )


class AuthenticationError(AppException):
    """
    Exception raised when authentication fails.

    Examples:
    - Invalid credentials
    - Missing authentication token
    - Expired token

    HTTP Status: 401 Unauthorized

    Note: This is defined for future use when authentication is implemented.
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize authentication error.

        Args:
            message: Description of the authentication failure
            details: Additional context
        """
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(AppException):
    """
    Exception raised when a user lacks permission for an operation.

    Examples:
    - Trying to modify another user's training plan
    - Accessing a resource without proper permissions

    HTTP Status: 403 Forbidden

    Note: This is defined for future use when authorization is implemented.
    """

    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize authorization error.

        Args:
            message: Description of the authorization failure
            required_permission: The permission that was required
            details: Additional context
        """
        error_details = details or {}
        if required_permission:
            error_details["required_permission"] = required_permission

        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=error_details
        )
