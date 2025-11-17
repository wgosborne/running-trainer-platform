"""
API endpoints for training plan operations.

This module defines all REST API endpoints for managing training plans:
- POST /plans - Create a new plan
- GET /plans - List all plans
- GET /plans/{plan_id} - Get a specific plan
- PUT /plans/{plan_id} - Update a plan
- DELETE /plans/{plan_id} - Delete a plan
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_db
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse
from app.services.plan_service import PlanService
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.logger import get_logger
from app.constants import API_CONSTANTS

# Initialize router, logger, and rate limiter
router = APIRouter(prefix="/plans", tags=["plans"])
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new training plan",
    response_description="The created training plan"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def create_plan(
    request: Request,
    plan_data: PlanCreate,
    db: Session = Depends(get_db)
) -> PlanResponse:
    """
    Create a new training plan.

    Args:
        plan_data: Plan creation data (name, description, start_date, end_date)
        db: Database session

    Returns:
        PlanResponse: The created plan with all fields

    Raises:
        HTTPException 400: Invalid data (validation error)
        HTTPException 500: Database error

    Example request body:
        {
            "name": "8-Week Marathon Prep",
            "description": "Boston Marathon training",
            "start_date": "2025-01-01",
            "end_date": "2025-02-28"
        }

    Example response (201):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "8-Week Marathon Prep",
            "description": "Boston Marathon training",
            "start_date": "2025-01-01",
            "end_date": "2025-02-28",
            "status": "DRAFT",
            "duration_days": 58,
            "created_at": "2025-01-14T12:00:00",
            "updated_at": "2025-01-14T12:00:00"
        }
    """
    try:
        logger.info(f"API: Creating plan '{plan_data.name}'")

        # Create plan via service
        service = PlanService()
        plan = service.create_plan(db, plan_data)

        logger.info(f"API: Plan created successfully: {plan.id}")
        return plan

    except ValidationError as e:
        logger.warning(f"Validation error creating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error creating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create plan"
        )

    except Exception as e:
        logger.error(f"Unexpected error creating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "",
    response_model=List[PlanResponse],
    summary="List all training plans",
    response_description="List of training plans"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def list_plans(
    request: Request,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
) -> List[PlanResponse]:
    """
    Retrieve a list of training plans with pagination.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        db: Database session

    Returns:
        List[PlanResponse]: List of plans

    Raises:
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Listing plans (skip={skip}, limit={limit})")

        # Get plans via service
        service = PlanService()
        plans = service.get_all_plans(db, skip=skip, limit=limit)

        logger.info(f"API: Retrieved {len(plans)} plans")
        return plans

    except DatabaseError as e:
        logger.error(f"Database error listing plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plans"
        )

    except Exception as e:
        logger.error(f"Unexpected error listing plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Get a specific training plan",
    response_description="The requested training plan"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def get_plan(
    request: Request,
    plan_id: UUID,
    db: Session = Depends(get_db)
) -> PlanResponse:
    """
    Retrieve a specific training plan by ID.

    Args:
        plan_id: UUID of the plan to retrieve
        db: Database session

    Returns:
        PlanResponse: The requested plan

    Raises:
        HTTPException 404: Plan not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Getting plan {plan_id}")

        # Get plan via service
        service = PlanService()
        plan = service.get_plan(db, plan_id)

        logger.info(f"API: Plan retrieved successfully: {plan_id}")
        return plan

    except NotFoundError as e:
        logger.warning(f"Plan not found: {plan_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error getting plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plan"
        )

    except Exception as e:
        logger.error(f"Unexpected error getting plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Update a training plan",
    response_description="The updated training plan"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def update_plan(
    request: Request,
    plan_id: UUID,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db)
) -> PlanResponse:
    """
    Update an existing training plan.

    Args:
        plan_id: UUID of the plan to update
        plan_data: Plan update data (all fields optional)
        db: Database session

    Returns:
        PlanResponse: The updated plan

    Raises:
        HTTPException 400: Invalid data (validation error)
        HTTPException 404: Plan not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Updating plan {plan_id}")

        # Update plan via service
        service = PlanService()
        plan = service.update_plan(db, plan_id, plan_data)

        logger.info(f"API: Plan updated successfully: {plan_id}")
        return plan

    except ValidationError as e:
        logger.warning(f"Validation error updating plan: {str(e)}")
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
        logger.error(f"Database error updating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update plan"
        )

    except Exception as e:
        logger.error(f"Unexpected error updating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a training plan",
    response_description="Plan deleted successfully"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def delete_plan(
    request: Request,
    plan_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a training plan by ID.

    Args:
        plan_id: UUID of the plan to delete
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: Plan not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Deleting plan {plan_id}")

        # Delete plan via service
        service = PlanService()
        service.delete_plan(db, plan_id)

        logger.info(f"API: Plan deleted successfully: {plan_id}")

    except NotFoundError as e:
        logger.warning(f"Plan not found: {plan_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error deleting plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete plan"
        )

    except Exception as e:
        logger.error(f"Unexpected error deleting plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
