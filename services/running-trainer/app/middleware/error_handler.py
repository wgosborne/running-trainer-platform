"""
Error handling middleware.

Catches all uncaught exceptions and converts them to appropriate
HTTP responses with error tracking IDs.
"""

import traceback
from uuid import uuid4
from datetime import datetime
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.exceptions import (
    AppException,
    ValidationError as AppValidationError,
    NotFoundError,
    ConflictError,
    DatabaseError
)
from app.utils.logger import get_logger, log_exception


logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to catch and handle all uncaught exceptions.

    This middleware wraps all request processing and ensures that:
    1. All exceptions are logged with full context
    2. All error responses include an error_id for tracking
    3. Sensitive information is not exposed to clients
    4. Appropriate HTTP status codes are returned

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        Response with error details if exception occurred

    Note:
        This middleware should be added early in the middleware stack
        to ensure it catches exceptions from other middleware.
    """
    try:
        # Process the request
        response = await call_next(request)
        return response

    except AppValidationError as exc:
        # Our custom validation errors (400)
        error_id = str(exc.error_id) if hasattr(exc, 'error_id') else str(uuid4())

        logger.warning(
            f"Validation error: {exc.message}",
            extra={
                "error_id": error_id,
                "error_code": getattr(exc, 'error_code', 'VALIDATION_ERROR'),
                "method": request.method,
                "path": str(request.url.path),
                "details": getattr(exc, 'details', {})
            }
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error_id": error_id,
                "error_code": getattr(exc, 'error_code', 'VALIDATION_ERROR'),
                "message": exc.message,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "details": getattr(exc, 'details', {})
            }
        )

    except NotFoundError as exc:
        # Resource not found errors (404)
        error_id = str(exc.error_id) if hasattr(exc, 'error_id') else str(uuid4())

        logger.warning(
            f"Not found: {exc.message}",
            extra={
                "error_id": error_id,
                "error_code": getattr(exc, 'error_code', 'NOT_FOUND'),
                "method": request.method,
                "path": str(request.url.path),
                "resource_type": getattr(exc, 'resource_type', None),
                "resource_id": getattr(exc, 'resource_id', None)
            }
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_id": error_id,
                "error_code": getattr(exc, 'error_code', 'NOT_FOUND'),
                "message": exc.message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    except ConflictError as exc:
        # Conflict errors (409)
        error_id = str(exc.error_id) if hasattr(exc, 'error_id') else str(uuid4())

        logger.warning(
            f"Conflict: {exc.message}",
            extra={
                "error_id": error_id,
                "error_code": getattr(exc, 'error_code', 'CONFLICT'),
                "method": request.method,
                "path": str(request.url.path)
            }
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error_id": error_id,
                "error_code": getattr(exc, 'error_code', 'CONFLICT'),
                "message": exc.message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    except DatabaseError as exc:
        # Database errors (500)
        error_id = str(exc.error_id) if hasattr(exc, 'error_id') else str(uuid4())

        log_exception(
            logger,
            f"Database error: {exc.message}",
            error_id=error_id,
            error_code=getattr(exc, 'error_code', 'DATABASE_ERROR'),
            method=request.method,
            path=str(request.url.path)
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_id": error_id,
                "error_code": "DATABASE_ERROR",
                "message": "A database error occurred",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    except ValidationError as exc:
        # Pydantic validation errors (422)
        error_id = str(uuid4())

        logger.warning(
            "Request validation error",
            extra={
                "error_id": error_id,
                "errors": exc.errors(),
                "method": request.method,
                "path": str(request.url.path)
            }
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_id": error_id,
                "error_code": "REQUEST_VALIDATION_ERROR",
                "message": "Request validation failed",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "details": exc.errors()
            }
        )

    except ValueError as exc:
        # Generic value errors (400)
        error_id = str(uuid4())

        logger.warning(
            f"Value error: {str(exc)}",
            extra={
                "error_id": error_id,
                "method": request.method,
                "path": str(request.url.path)
            }
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error_id": error_id,
                "error_code": "INVALID_VALUE",
                "message": str(exc),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    except Exception as exc:
        # Catch-all for unexpected errors (500)
        error_id = str(uuid4())

        log_exception(
            logger,
            f"Unhandled exception: {type(exc).__name__}",
            error_id=error_id,
            error_type=type(exc).__name__,
            method=request.method,
            path=str(request.url.path),
            headers=dict(request.headers)
        )

        # Don't expose internal error details to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_id": error_id,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
