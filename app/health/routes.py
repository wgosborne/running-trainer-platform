"""
Health check API endpoints.

Provides endpoints for liveness, readiness, and detailed health checks.
These are used by container orchestrators, load balancers, and monitoring systems.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.health.checks import run_health_checks, is_healthy
from app.health.models import HealthCheckResponse
from app.utils.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health Checks"])


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Returns 200 if the application is running. Used by Kubernetes/Docker for liveness checks."
)
async def liveness_check() -> dict:
    """
    Liveness probe endpoint.

    This endpoint always returns 200 OK if the application is running.
    It's used by container orchestrators (Kubernetes, Docker Swarm) to
    determine if the container should be restarted.

    Returns:
        Simple status response

    Note:
        This check should be very lightweight and never fail unless
        the application is completely broken. Failures here will cause
        the container to be restarted.
    """
    return {
        "status": "alive"
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Returns 200 if ready to handle traffic, 503 if not. Used by load balancers."
)
async def readiness_check(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Readiness probe endpoint.

    This endpoint returns 200 if the application is ready to handle traffic,
    or 503 if it's not ready (e.g., database is down). Used by load balancers
    to determine if traffic should be routed to this instance.

    Args:
        db: Database session (injected)

    Returns:
        JSONResponse with 200 if ready, 503 if not ready

    Note:
        Failures here will remove the instance from the load balancer
        pool but won't restart the container. The instance will be added
        back once it becomes ready again.
    """
    if is_healthy(db):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready"}
        )
    else:
        logger.warning("Readiness check failed - database unhealthy")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "reason": "Database connectivity issues"
            }
        )


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed Health Check",
    description="Returns detailed health status of all application components."
)
async def health_check(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Detailed health check endpoint.

    This endpoint runs comprehensive health checks on all application
    components and returns detailed status information. It includes:
    - Overall health status
    - Individual component health (database, cache, etc.)
    - Latency metrics
    - Uptime information

    Args:
        db: Database session (injected)

    Returns:
        HealthCheckResponse with detailed status

    Status Codes:
        - 200: All checks healthy
        - 503: One or more checks degraded or unhealthy

    Example Response:
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "uptime_seconds": 3600.5,
            "version": "1.0.0",
            "checks": {
                "database": {
                    "status": "healthy",
                    "latency_ms": 2.5
                }
            }
        }
    """
    # Run all health checks
    health_response = run_health_checks(db)

    # Return appropriate status code
    if health_response.status == "healthy":
        status_code = status.HTTP_200_OK
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content=health_response.dict()
    )
