"""
Health check implementations.

Functions to check the health of various application components.
"""

import time
from datetime import datetime
from typing import Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.health.models import HealthCheck, HealthCheckResponse
from app.config import get_settings
from app.utils.logger import get_logger


logger = get_logger(__name__)
settings = get_settings()

# Track application start time for uptime calculation
APP_START_TIME = time.time()


def get_db_health(db: Session) -> HealthCheck:
    """
    Check database connectivity and latency.

    Performs a simple query to verify the database is accessible
    and measures the response time.

    Args:
        db: Database session

    Returns:
        HealthCheck with database status

    Example:
        >>> health = get_db_health(db)
        >>> assert health.status == "healthy"
    """
    start_time = time.time()

    try:
        # Execute simple query to test connectivity
        db.execute(text("SELECT 1"))

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Log slow queries
        if latency_ms > 100:
            logger.warning(
                f"Database health check slow: {latency_ms:.2f}ms",
                extra={"latency_ms": latency_ms}
            )

        return HealthCheck(
            status="healthy",
            latency_ms=round(latency_ms, 2),
            error=None
        )

    except Exception as e:
        logger.error(
            f"Database health check failed: {str(e)}",
            exc_info=True
        )

        return HealthCheck(
            status="unhealthy",
            latency_ms=None,
            error=str(e)
        )


def get_system_health() -> Dict:
    """
    Get system-level health metrics.

    Collects information about application uptime and resource usage.

    Returns:
        Dictionary with system health metrics

    Example:
        >>> health = get_system_health()
        >>> assert "uptime_seconds" in health
    """
    uptime_seconds = time.time() - APP_START_TIME

    return {
        "uptime_seconds": round(uptime_seconds, 2)
    }


def run_health_checks(db: Session) -> HealthCheckResponse:
    """
    Run all health checks and aggregate results.

    Executes all registered health checks and determines overall
    application health status based on the results.

    Args:
        db: Database session

    Returns:
        HealthCheckResponse with aggregated results

    Health Status Logic:
        - healthy: All checks pass
        - degraded: Some non-critical checks fail
        - unhealthy: Critical checks fail (e.g., database)

    Example:
        >>> response = run_health_checks(db)
        >>> assert response.status in ["healthy", "degraded", "unhealthy"]
    """
    # Run individual checks
    db_health = get_db_health(db)
    system_health = get_system_health()

    # Aggregate check results
    checks = {
        "database": db_health
    }

    # Determine overall status
    if db_health.status == "unhealthy":
        # Database is critical - mark as unhealthy
        overall_status = "unhealthy"
    elif db_health.status == "degraded":
        # Database degraded - mark as degraded
        overall_status = "degraded"
    else:
        # All checks healthy
        overall_status = "healthy"

    # Build response
    response = HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        uptime_seconds=system_health["uptime_seconds"],
        version=settings.API_VERSION,
        checks=checks
    )

    # Log health check results
    if overall_status != "healthy":
        logger.warning(
            f"Health check status: {overall_status}",
            extra={
                "status": overall_status,
                "checks": {
                    name: check.dict()
                    for name, check in checks.items()
                }
            }
        )

    return response


def is_healthy(db: Session) -> bool:
    """
    Quick health check - returns True if application is healthy.

    This is a simplified check for use in liveness/readiness probes.

    Args:
        db: Database session

    Returns:
        True if healthy, False otherwise

    Example:
        >>> assert is_healthy(db) == True
    """
    try:
        db_health = get_db_health(db)
        return db_health.status == "healthy"
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False
