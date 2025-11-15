"""
Health check models.

Pydantic models for health check responses.
"""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """
    Individual health check result.

    Represents the result of a single health check (database, cache, etc.)
    """

    status: str = Field(
        description="Status of the check (healthy, degraded, unhealthy)"
    )
    latency_ms: Optional[float] = Field(
        default=None,
        description="Latency of the check in milliseconds"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if check failed"
    )
    details: Optional[Dict] = Field(
        default=None,
        description="Additional check-specific details"
    )


class HealthCheckResponse(BaseModel):
    """
    Comprehensive health check response.

    Aggregates results from all health checks and provides
    overall application health status.
    """

    status: str = Field(
        description="Overall health status (healthy, degraded, unhealthy)"
    )
    timestamp: datetime = Field(
        description="When the health check was performed"
    )
    uptime_seconds: float = Field(
        description="Application uptime in seconds"
    )
    version: str = Field(
        description="Application version"
    )
    checks: Dict[str, HealthCheck] = Field(
        description="Individual check results"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "uptime_seconds": 3600.5,
                "version": "1.0.0",
                "checks": {
                    "database": {
                        "status": "healthy",
                        "latency_ms": 2.5,
                        "error": None
                    }
                }
            }
        }
