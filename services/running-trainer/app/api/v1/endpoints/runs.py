"""
API endpoints for run operations.

This module defines all REST API endpoints for managing runs:
- POST /plans/{plan_id}/runs - Create a new run for a plan
- GET /plans/{plan_id}/runs - List runs for a plan
- GET /runs - List all runs
- GET /runs/{run_id} - Get a specific run
- PATCH /runs/{run_id} - Update a run
- DELETE /runs/{run_id} - Delete a run
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_db
from app.constants import API_CONSTANTS
from app.schemas.run import RunCreate, RunUpdate, RunResponse
from app.services.run_service import RunService
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.logger import get_logger

# Initialize router and logger
router = APIRouter()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/plans/{plan_id}/runs",
    response_model=RunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new run for a plan",
    response_description="The created run"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def create_run(
    request: Request,
    plan_id: UUID,
    run_data: RunCreate,
    db: Session = Depends(get_db)
) -> RunResponse:
    """
    Log a new run for a training plan.

    Args:
        plan_id: UUID of the parent plan
        run_data: Run creation data
        db: Database session

    Returns:
        RunResponse: The created run

    Raises:
        HTTPException 400: Invalid data (validation error)
        HTTPException 404: Plan or workout not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Creating run for plan {plan_id}")

        service = RunService()
        run = service.create_run(db, plan_id, run_data)

        logger.info(f"API: Run created successfully: {run.id}")
        return run

    except ValidationError as e:
        logger.warning(f"Validation error creating run: {str(e)}")
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
        logger.error(f"Database error creating run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create run"
        )

    except Exception as e:
        logger.error(f"Unexpected error creating run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/plans/{plan_id}/runs",
    response_model=List[RunResponse],
    summary="List runs for a plan",
    response_description="List of runs"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def list_runs_for_plan(
    request: Request,
    plan_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[RunResponse]:
    """
    Retrieve runs for a specific plan with pagination.

    Args:
        plan_id: UUID of the parent plan
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        db: Database session

    Returns:
        List[RunResponse]: List of runs

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

        logger.info(f"API: Listing runs for plan {plan_id} (skip={skip}, limit={limit})")

        service = RunService()
        runs = service.get_runs_for_plan(db, plan_id, skip=skip, limit=limit)

        logger.info(f"API: Retrieved {len(runs)} runs")
        return runs

    except ValidationError as e:
        logger.warning(f"Validation error listing runs: {str(e)}")
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
        logger.error(f"Database error listing runs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve runs"
        )

    except Exception as e:
        logger.error(f"Unexpected error listing runs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/runs",
    response_model=List[RunResponse],
    summary="List all runs",
    response_description="List of all runs"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def list_all_runs(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[RunResponse]:
    """
    Retrieve all runs across all plans with pagination.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        db: Database session

    Returns:
        List[RunResponse]: List of runs

    Raises:
        HTTPException 400: Invalid pagination parameters
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

        logger.info(f"API: Listing all runs (skip={skip}, limit={limit})")

        service = RunService()
        runs = service.get_all_runs(db, skip=skip, limit=limit)

        logger.info(f"API: Retrieved {len(runs)} runs")
        return runs

    except ValidationError as e:
        logger.warning(f"Validation error listing runs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error listing runs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve runs"
        )

    except Exception as e:
        logger.error(f"Unexpected error listing runs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/runs/{run_id}",
    response_model=RunResponse,
    summary="Get a specific run",
    response_description="The requested run"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_READ_OPS)
async def get_run(
    request: Request,
    run_id: UUID,
    db: Session = Depends(get_db)
) -> RunResponse:
    """
    Retrieve a specific run by ID.

    Args:
        run_id: UUID of the run to retrieve
        db: Database session

    Returns:
        RunResponse: The requested run

    Raises:
        HTTPException 404: Run not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Getting run {run_id}")

        service = RunService()
        run = service.get_run(db, run_id)

        logger.info(f"API: Run retrieved successfully: {run_id}")
        return run

    except NotFoundError as e:
        logger.warning(f"Run not found: {run_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error getting run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve run"
        )

    except Exception as e:
        logger.error(f"Unexpected error getting run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch(
    "/runs/{run_id}",
    response_model=RunResponse,
    summary="Update a run",
    response_description="The updated run"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def update_run(
    request: Request,
    run_id: UUID,
    run_data: RunUpdate,
    db: Session = Depends(get_db)
) -> RunResponse:
    """
    Update an existing run (partial update).

    Args:
        run_id: UUID of the run to update
        run_data: Run update data (all fields optional)
        db: Database session

    Returns:
        RunResponse: The updated run

    Raises:
        HTTPException 400: Invalid data (validation error)
        HTTPException 404: Run or workout not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Updating run {run_id}")

        service = RunService()
        run = service.update_run(db, run_id, run_data)

        logger.info(f"API: Run updated successfully: {run_id}")
        return run

    except ValidationError as e:
        logger.warning(f"Validation error updating run: {str(e)}")
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
        logger.error(f"Database error updating run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update run"
        )

    except Exception as e:
        logger.error(f"Unexpected error updating run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/runs/{run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a run",
    response_description="Run deleted successfully"
)
@limiter.limit(API_CONSTANTS.RATE_LIMIT_WRITE_OPS)
async def delete_run(
    request: Request,
    run_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a run by ID.

    Args:
        run_id: UUID of the run to delete
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: Run not found
        HTTPException 500: Database error
    """
    try:
        logger.info(f"API: Deleting run {run_id}")

        service = RunService()
        service.delete_run(db, run_id)

        logger.info(f"API: Run deleted successfully: {run_id}")

    except NotFoundError as e:
        logger.warning(f"Run not found: {run_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except DatabaseError as e:
        logger.error(f"Database error deleting run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete run"
        )

    except Exception as e:
        logger.error(f"Unexpected error deleting run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
