"""
FastAPI application entry point.

This module initializes the FastAPI application, configures middleware,
registers error handlers, and sets up startup/shutdown events.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.constants import API_CONSTANTS
from app.exceptions import (
    AppException,
    ValidationError,
    NotFoundError,
    ConflictError,
    DatabaseError,
    AuthenticationError,
    AuthorizationError,
)
from app.db.init_db import init_db, check_db_health
from app.utils.logger import get_logger, setup_logging
from app.api.v1.router import router as api_v1_router


# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)


# ============================================================================
# Lifespan Context Manager
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.

    This function is called once when the application starts and once
    when it shuts down. It's used for initialization and cleanup tasks.

    Args:
        app: The FastAPI application instance

    Yields:
        Control to the application
    """
    # Startup
    logger.info("=" * 70)
    logger.info(f"Starting {settings.APP_NAME} ({settings.API_VERSION})")
    logger.info("=" * 70)

    # Set up logging with configured level
    setup_logging(settings.LOG_LEVEL)
    logger.info(f"Logging configured at {settings.LOG_LEVEL} level")

    # Check database health
    logger.info("Checking database connection...")
    if not check_db_health():
        logger.error("Database connection failed - application may not work correctly")
    else:
        logger.info("Database connection successful")

    # Initialize database tables
    try:
        logger.info("Initializing database tables...")
        init_db()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.error("Application may not work correctly")

    logger.info(f"{settings.APP_NAME} startup complete")
    logger.info("=" * 70)

    # Yield control to application
    yield

    # Shutdown
    logger.info("=" * 70)
    logger.info(f"Shutting down {settings.APP_NAME}")
    logger.info("=" * 70)


# ============================================================================
# FastAPI Application
# ============================================================================


app = FastAPI(
    title=settings.APP_NAME,
    description="A production-ready microservice for managing running training plans",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================================================
# Rate Limiting Configuration
# ============================================================================


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[API_CONSTANTS.RATE_LIMIT_READ_OPS],
    storage_uri="memory://",  # Use in-memory storage (for production, use Redis)
    headers_enabled=True,  # Add rate limit info to response headers
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================================
# Middleware Configuration
# ============================================================================


# CORS middleware - configure allowed origins based on environment
# In production, set ALLOWED_ORIGINS env var to specific domains
allowed_origins = settings.get_allowed_origins()

# Log CORS configuration for debugging
logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


# Request size limiting middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """
    Limit request body size to prevent memory exhaustion attacks.

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        The response from the route handler or error if too large
    """
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > API_CONSTANTS.MAX_REQUEST_SIZE_BYTES:
            logger.warning(
                f"Request body too large: {content_length} bytes "
                f"(max: {API_CONSTANTS.MAX_REQUEST_SIZE_BYTES})"
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error_code": "REQUEST_TOO_LARGE",
                    "message": f"Request body too large. Maximum size is {API_CONSTANTS.MAX_REQUEST_SIZE_BYTES / 1_000_000}MB",
                }
            )

    return await call_next(request)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests and responses.

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        The response from the route handler
    """
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code}"
    )

    return response


# ============================================================================
# Exception Handlers
# ============================================================================


@app.exception_handler(ValidationError)
async def validation_error_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """
    Handle ValidationError exceptions.

    Args:
        request: The request that caused the error
        exc: The validation error

    Returns:
        JSON response with error details
    """
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.to_dict()
    )


@app.exception_handler(NotFoundError)
async def not_found_error_handler(
    request: Request,
    exc: NotFoundError
) -> JSONResponse:
    """
    Handle NotFoundError exceptions.

    Args:
        request: The request that caused the error
        exc: The not found error

    Returns:
        JSON response with error details
    """
    logger.warning(f"Not found: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=exc.to_dict()
    )


@app.exception_handler(ConflictError)
async def conflict_error_handler(
    request: Request,
    exc: ConflictError
) -> JSONResponse:
    """
    Handle ConflictError exceptions.

    Args:
        request: The request that caused the error
        exc: The conflict error

    Returns:
        JSON response with error details
    """
    logger.warning(f"Conflict: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=exc.to_dict()
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(
    request: Request,
    exc: DatabaseError
) -> JSONResponse:
    """
    Handle DatabaseError exceptions.

    Args:
        request: The request that caused the error
        exc: The database error

    Returns:
        JSON response with error details
    """
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "DATABASE_ERROR",
            "message": "A database error occurred",
            "details": {}  # Don't expose internal details
        }
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(
    request: Request,
    exc: AuthenticationError
) -> JSONResponse:
    """
    Handle AuthenticationError exceptions.

    Args:
        request: The request that caused the error
        exc: The authentication error

    Returns:
        JSON response with error details
    """
    logger.warning(f"Authentication error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=exc.to_dict()
    )


@app.exception_handler(AuthorizationError)
async def authorization_error_handler(
    request: Request,
    exc: AuthorizationError
) -> JSONResponse:
    """
    Handle AuthorizationError exceptions.

    Args:
        request: The request that caused the error
        exc: The authorization error

    Returns:
        JSON response with error details
    """
    logger.warning(f"Authorization error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=exc.to_dict()
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic request validation errors.

    Args:
        request: The request that caused the error
        exc: The validation error

    Returns:
        JSON response with error details
    """
    logger.warning(f"Request validation error: {exc.errors()}")

    # Convert error details to JSON-serializable format
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc", []),
            "msg": str(error.get("msg", "")),
            "type": error.get("type", "")
        }
        errors.append(error_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "REQUEST_VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle any unhandled exceptions.

    Args:
        request: The request that caused the error
        exc: The exception

    Returns:
        JSON response with generic error message
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {}  # Don't expose internal details in production
        }
    )


# ============================================================================
# Health Check Endpoint
# ============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns the status of the application and its dependencies.
    Useful for load balancers, container orchestration, and monitoring.

    Returns:
        Health check response with status and details

    Example Response:
        {
            "status": "ok",
            "service": "Running Trainer API",
            "version": "v1",
            "database": "connected"
        }
    """
    # Check database health
    db_status = "connected" if check_db_health() else "disconnected"

    # Overall health is OK if database is connected
    overall_status = "ok" if db_status == "connected" else "degraded"

    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "database": db_status
    }


# ============================================================================
# API Routes
# ============================================================================


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint.

    Returns basic information about the API.

    Returns:
        API information
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include API v1 routes
app.include_router(api_v1_router)
