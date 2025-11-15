"""
Request context middleware.

Generates request IDs for correlation and tracks request metadata
throughout the request lifecycle.
"""

import time
from uuid import uuid4
from typing import Callable

from fastapi import Request, Response

from app.utils.logger import (
    get_logger,
    set_request_context,
    clear_request_context
)


logger = get_logger(__name__)


async def request_context_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to add request context tracking.

    This middleware:
    1. Generates a unique request_id for each request
    2. Extracts user_id if available (from headers or JWT)
    3. Stores context in thread-local storage for logging
    4. Adds X-Request-ID header to response
    5. Logs request start and completion with timing

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        Response with X-Request-ID header added
    """
    # Generate or extract request ID
    request_id = request.headers.get("X-Request-ID", str(uuid4()))

    # Extract user ID if present (placeholder for auth)
    user_id = request.headers.get("X-User-ID")

    # Set request context for logging
    set_request_context(
        request_id=request_id,
        user_id=user_id,
        method=request.method,
        path=str(request.url.path)
    )

    # Store request ID in request state for access in routes
    request.state.request_id = request_id
    request.state.user_id = user_id

    # Log incoming request
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None
        }
    )

    # Measure request duration
    start_time = time.time()

    try:
        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Log request completion
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration_ms:.2f}ms",
            extra={
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2)
            }
        )

        return response

    except Exception as exc:
        # Log error before re-raising
        duration_ms = (time.time() - start_time) * 1000

        logger.error(
            f"Request failed: {request.method} {request.url.path} - "
            f"Duration: {duration_ms:.2f}ms",
            extra={
                "duration_ms": round(duration_ms, 2),
                "error_type": type(exc).__name__
            },
            exc_info=True
        )

        # Re-raise to be handled by error middleware
        raise

    finally:
        # Clear request context
        clear_request_context()
