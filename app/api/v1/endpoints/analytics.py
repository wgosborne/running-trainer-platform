"""
API endpoints for analytics and reporting.

This module defines all REST API endpoints for analytics:
- GET /plans/{plan_id}/progress - Get plan progress metrics
- GET /plans/{plan_id}/weekly-summary - Get weekly training summary
"""

from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_db
from app.constants import API_CONSTANTS
from app.services.analytics_service import AnalyticsService
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.logger import get_logger

# Initialize router and logger
router = APIRouter()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/plans/{plan_id}/progress",
    summary="Get plan progress metrics",
    response_description="Plan progress and adherence metrics"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def get_plan_progress(
    request: Request,
    plan_id: UUID,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get progress metrics for a training plan.

    Calculates:
    - Total workouts planned vs completed
    - Total distance planned vs actual
    - Adherence percentage

    Args:
        plan_id: UUID of the plan
        db: Database session

    Returns:
        Dict containing progress metrics:
            - total_workouts: Total planned workouts
            - completed_workouts: Workouts with at least one linked run
            - pending_workouts: Workouts without any runs
            - total_planned_distance: Sum of all workout distances
            - total_actual_distance: Sum of all run distances
            - adherence_percentage: Percentage of workouts completed

    Raises:
        HTTPException 404: Plan not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Getting progress for plan {plan_id}")

        service = AnalyticsService()
        progress = service.get_plan_progress(db, plan_id)

        logger.info(f"API: Progress retrieved successfully for plan {plan_id}")
        return progress

    except NotFoundError as e:
        logger.warning(f"Plan not found: {plan_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error getting progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate progress"
        )

    except Exception as e:
        logger.error(f"Unexpected error getting progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/plans/{plan_id}/weekly-summary",
    summary="Get weekly training summary",
    response_description="Weekly training metrics and run details"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def get_weekly_summary(
    request: Request,
    plan_id: UUID,
    week_number: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get weekly summary for a training plan.

    Provides a breakdown of planned vs actual training for a specific week.

    Args:
        plan_id: UUID of the plan
        week_number: Week number (1-indexed). Defaults to week 1 if not provided.
        db: Database session

    Returns:
        Dict containing weekly summary:
            - week_number: Week number
            - start_date: Start date of the week
            - end_date: End date of the week
            - planned_distance: Total planned distance for the week
            - actual_distance: Total actual distance for the week
            - planned_runs: Number of planned workouts
            - completed_runs: Number of completed runs
            - runs: List of run details

    Raises:
        HTTPException 400: Invalid week number
        HTTPException 404: Plan not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Getting weekly summary for plan {plan_id}, week {week_number}")

        service = AnalyticsService()
        summary = service.get_weekly_summary(db, plan_id, week_number)

        logger.info(f"API: Weekly summary retrieved successfully for plan {plan_id}")
        return summary

    except ValidationError as e:
        logger.warning(f"Validation error getting weekly summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except NotFoundError as e:
        logger.warning(f"Plan not found: {plan_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error getting weekly summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate weekly summary"
        )

    except Exception as e:
        logger.error(f"Unexpected error getting weekly summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
