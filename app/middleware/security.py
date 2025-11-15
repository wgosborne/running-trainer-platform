"""
Security middleware.

Adds security headers to all responses for protection against
common web vulnerabilities.
"""

from typing import Callable

from fastapi import Request, Response

from app.config import get_settings
from app.utils.logger import get_logger


logger = get_logger(__name__)
settings = get_settings()


async def add_security_headers(request: Request, call_next: Callable) -> Response:
    """
    Middleware to add security headers to all responses.

    Adds headers to protect against common vulnerabilities:
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filtering
    - Strict-Transport-Security: Enforce HTTPS (production only)

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        Response with security headers added
    """
    response = await call_next(request)

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Enable XSS protection (legacy but doesn't hurt)
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # HSTS - only in production (requires HTTPS)
    if not settings.DEBUG:
        # Enforce HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    # Content Security Policy - basic policy
    # Can be customized based on frontend requirements
    if not settings.DEBUG:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )

    # Referrer Policy - control referrer information
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions Policy - restrict browser features
    response.headers["Permissions-Policy"] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=()"
    )

    return response
