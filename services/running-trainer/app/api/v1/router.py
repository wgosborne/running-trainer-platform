"""
Main router for API version 1.

This module aggregates all v1 endpoint routers into a single
API v1 router that can be included in the main FastAPI application.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import plans, workouts, runs, analytics

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
router.include_router(plans.router)
router.include_router(workouts.router)
router.include_router(runs.router)
router.include_router(analytics.router)
