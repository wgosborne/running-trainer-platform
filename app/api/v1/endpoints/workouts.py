"""
API endpoints for workout operations.

This module defines all REST API endpoints for managing workouts:
- POST /plans/{plan_id}/workouts - Create a new workout
- GET /plans/{plan_id}/workouts - List workouts for a plan
- GET /plans/{plan_id}/workouts/{workout_id} - Get a specific workout
- PATCH /plans/{plan_id}/workouts/{workout_id} - Update a workout
- DELETE /plans/{plan_id}/workouts/{workout_id} - Delete a workout
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_db
from app.constants import API_CONSTANTS
from app.schemas.workout import WorkoutCreate, WorkoutUpdate, WorkoutResponse
from app.services.workout_service import WorkoutService
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.logger import get_logger

# Initialize router and logger
router = APIRouter()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/plans/{plan_id}/workouts",
    response_model=WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workout for a plan",
    response_description="The created workout"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def create_workout(
    request: Request,
    plan_id: UUID,
    workout_data: WorkoutCreate,
    db: Session = Depends(get_db)
) -> WorkoutResponse:
    """
    Create a new workout for a training plan.

    Args:
        plan_id: UUID of the parent plan
        workout_data: Workout creation data
        db: Database session

    Returns:
        WorkoutResponse: The created workout

    Raises:
        HTTPException 400: Invalid data (validation error)
        HTTPException 404: Plan not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Creating workout for plan {plan_id}")

        service = WorkoutService()
        workout = service.create_workout(db, plan_id, workout_data)

        logger.info(f"API: Workout created successfully: {workout.id}")
        return workout

    except ValidationError as e:
        logger.warning(f"Validation error creating workout: {str(e)}")
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
        logger.error(f"Database error creating workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workout"
        )

    except Exception as e:
        logger.error(f"Unexpected error creating workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/plans/{plan_id}/workouts",
    response_model=List[WorkoutResponse],
    summary="List workouts for a plan",
    response_description="List of workouts"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def list_workouts(
    request: Request,
    plan_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[WorkoutResponse]:
    """
    Retrieve workouts for a specific plan with pagination.

    Args:
        plan_id: UUID of the parent plan
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        db: Database session

    Returns:
        List[WorkoutResponse]: List of workouts

    Raises:
        HTTPException 400: Invalid pagination parameters
        HTTPException 404: Plan not found
        HTTPException 500: Database error
    """
    try:
        # Validate pagination parameters
        if skip < 0:
            raise ValidationError(message="skip must be >= 0")
        if limit <= 0:
            raise ValidationError(message="limit must be > 0")
        if limit > 100:
            raise ValidationError(message="limit cannot exceed 100")

        logger.info(f"API: Listing workouts for plan {plan_id} (skip={skip}, limit={limit})")

        service = WorkoutService()
        workouts = service.get_workouts_for_plan(db, plan_id, skip=skip, limit=limit)

        logger.info(f"API: Retrieved {len(workouts)} workouts")
        return workouts

    except ValidationError as e:
        logger.warning(f"Validation error listing workouts: {str(e)}")
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
        logger.error(f"Database error listing workouts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workouts"
        )

    except Exception as e:
        logger.error(f"Unexpected error listing workouts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/plans/{plan_id}/workouts/{workout_id}",
    response_model=WorkoutResponse,
    summary="Get a specific workout",
    response_description="The requested workout"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def get_workout(
    request: Request,
    plan_id: UUID,
    workout_id: UUID,
    db: Session = Depends(get_db)
) -> WorkoutResponse:
    """
    Retrieve a specific workout by ID.

    Args:
        plan_id: UUID of the parent plan
        workout_id: UUID of the workout to retrieve
        db: Database session

    Returns:
        WorkoutResponse: The requested workout

    Raises:
        HTTPException 404: Plan or workout not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Getting workout {workout_id} for plan {plan_id}")

        service = WorkoutService()
        workout = service.get_workout(db, plan_id, workout_id)

        logger.info(f"API: Workout retrieved successfully: {workout_id}")
        return workout

    except NotFoundError as e:
        logger.warning(f"Resource not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error getting workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workout"
        )

    except Exception as e:
        logger.error(f"Unexpected error getting workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch(
    "/plans/{plan_id}/workouts/{workout_id}",
    response_model=WorkoutResponse,
    summary="Update a workout",
    response_description="The updated workout"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def update_workout(
    request: Request,
    plan_id: UUID,
    workout_id: UUID,
    workout_data: WorkoutUpdate,
    db: Session = Depends(get_db)
) -> WorkoutResponse:
    """
    Update an existing workout (partial update).

    Args:
        plan_id: UUID of the parent plan
        workout_id: UUID of the workout to update
        workout_data: Workout update data (all fields optional)
        db: Database session

    Returns:
        WorkoutResponse: The updated workout

    Raises:
        HTTPException 400: Invalid data (validation error)
        HTTPException 404: Plan or workout not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Updating workout {workout_id} for plan {plan_id}")

        service = WorkoutService()
        workout = service.update_workout(db, plan_id, workout_id, workout_data)

        logger.info(f"API: Workout updated successfully: {workout_id}")
        return workout

    except ValidationError as e:
        logger.warning(f"Validation error updating workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except NotFoundError as e:
        logger.warning(f"Resource not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error updating workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workout"
        )

    except Exception as e:
        logger.error(f"Unexpected error updating workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/plans/{plan_id}/workouts/{workout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workout",
    response_description="Workout deleted successfully"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def delete_workout(
    request: Request,
    plan_id: UUID,
    workout_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a workout by ID.

    Args:
        plan_id: UUID of the parent plan
        workout_id: UUID of the workout to delete
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: Plan or workout not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Deleting workout {workout_id} for plan {plan_id}")

        service = WorkoutService()
        service.delete_workout(db, plan_id, workout_id)

        logger.info(f"API: Workout deleted successfully: {workout_id}")

    except NotFoundError as e:
        logger.warning(f"Resource not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error deleting workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workout"
        )

    except Exception as e:
        logger.error(f"Unexpected error deleting workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
