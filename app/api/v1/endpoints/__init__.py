"""
API v1 endpoints package.

This package contains all endpoint modules for API version 1.
Each module defines routes for a specific resource.
"""

from app.api.v1.endpoints import plans, workouts, runs, analytics

__all__ = ["plans", "workouts", "runs", "analytics"]
