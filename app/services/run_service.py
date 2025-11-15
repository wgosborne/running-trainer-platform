"""
Business logic for runs.

This module contains the service layer for run operations.
Services handle business logic, validation, and coordinate between
API endpoints and CRUD operations.
"""

from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.run import RunCRUD
from app.crud.plan import PlanCRUD
from app.crud.workout import WorkoutCRUD
from app.models.run import Run
from app.schemas.run import RunCreate, RunUpdate
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


class RunService:
    """
    Service class for run business logic.

    This class handles business logic for run operations including
    validation, authorization, and coordinating CRUD operations.
    """

    def __init__(self):
        """Initialize the service with CRUD instances."""
        self.crud = RunCRUD()
        self.plan_crud = PlanCRUD()
        self.workout_crud = WorkoutCRUD()

    def create_run(
        self,
        db: Session,
        plan_id: UUID,
        run_data: RunCreate
    ) -> Run:
        """
        Create a new run for a plan.

        Args:
            db: Database session
            plan_id: ID of the parent plan
            run_data: Run creation data

        Returns:
            The newly created Run object

        Raises:
            NotFoundError: If plan or workout does not exist
            ValidationError: If run data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Creating run for plan {plan_id}")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # If workout_id provided, verify it exists and belongs to this plan
            if run_data.workout_id:
                workout = self.workout_crud.get_by_plan_and_id(
                    db, plan_id, run_data.workout_id
                )
                if not workout:
                    logger.warning(
                        f"Workout not found or doesn't belong to plan: {run_data.workout_id}"
                    )
                    raise NotFoundError(
                        resource_type="Workout",
                        resource_id=str(run_data.workout_id)
                    )

            # Create run via CRUD
            run = self.crud.create(db, plan_id, run_data)

            logger.info(f"Run created successfully: {run.id}")
            return run

        except NotFoundError:
            raise

        except ValidationError as e:
            logger.warning(f"Validation error creating run: {str(e)}")
            raise

        except DatabaseError as e:
            logger.error(f"Database error creating run: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error creating run: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while creating run",
                details={"error": str(e)}
            )

    def get_run(self, db: Session, run_id: UUID) -> Run:
        """
        Retrieve a run by ID.

        Args:
            db: Database session
            run_id: UUID of the run to retrieve

        Returns:
            The Run object

        Raises:
            NotFoundError: If run does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Fetching run {run_id}")

            run = self.crud.get(db, run_id)

            if not run:
                logger.warning(f"Run not found: {run_id}")
                raise NotFoundError(
                    resource_type="Run",
                    resource_id=str(run_id)
                )

            logger.info(f"Run retrieved successfully: {run_id}")
            return run

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(f"Database error fetching run: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error fetching run: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching run",
                details={"error": str(e)}
            )

    def get_runs_for_plan(
        self,
        db: Session,
        plan_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Run]:
        """
        Retrieve runs for a specific plan with pagination.

        Args:
            db: Database session
            plan_id: ID of the parent plan
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Run objects

        Raises:
            NotFoundError: If plan does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Fetching runs for plan {plan_id} (skip={skip}, limit={limit})")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Get runs
            runs = self.crud.get_by_plan(db, plan_id, skip=skip, limit=limit)

            logger.info(f"Retrieved {len(runs)} runs for plan {plan_id}")
            return runs

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(f"Database error fetching runs: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error fetching runs: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching runs",
                details={"error": str(e)}
            )

    def get_all_runs(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Run]:
        """
        Retrieve all runs with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Run objects

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Fetching all runs (skip={skip}, limit={limit})")

            runs = self.crud.get_all(db, skip=skip, limit=limit)

            logger.info(f"Retrieved {len(runs)} runs")
            return runs

        except DatabaseError as e:
            logger.error(f"Database error fetching runs: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error fetching runs: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching runs",
                details={"error": str(e)}
            )

    def update_run(
        self,
        db: Session,
        run_id: UUID,
        run_data: RunUpdate
    ) -> Run:
        """
        Update an existing run.

        Args:
            db: Database session
            run_id: UUID of the run to update
            run_data: Run update data

        Returns:
            The updated Run object

        Raises:
            NotFoundError: If run or workout does not exist
            ValidationError: If update data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Updating run {run_id}")

            # Get existing run
            run = self.crud.get(db, run_id)
            if not run:
                logger.warning(f"Run not found: {run_id}")
                raise NotFoundError(
                    resource_type="Run",
                    resource_id=str(run_id)
                )

            # If workout_id is being updated, verify it exists and belongs to run's plan
            if run_data.workout_id is not None:
                workout = self.workout_crud.get_by_plan_and_id(
                    db, run.plan_id, run_data.workout_id
                )
                if not workout:
                    logger.warning(
                        f"Workout not found or doesn't belong to run's plan: {run_data.workout_id}"
                    )
                    raise NotFoundError(
                        resource_type="Workout",
                        resource_id=str(run_data.workout_id)
                    )

            # Update run via CRUD
            updated_run = self.crud.update(db, run_id, run_data)

            logger.info(f"Run updated successfully: {run_id}")
            return updated_run

        except NotFoundError:
            raise

        except ValidationError as e:
            logger.warning(f"Validation error updating run: {str(e)}")
            raise

        except DatabaseError as e:
            logger.error(f"Database error updating run: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error updating run: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while updating run",
                details={"error": str(e)}
            )

    def delete_run(self, db: Session, run_id: UUID) -> bool:
        """
        Delete a run by ID.

        Args:
            db: Database session
            run_id: UUID of the run to delete

        Returns:
            True if run was deleted

        Raises:
            NotFoundError: If run does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Deleting run {run_id}")

            # Verify run exists
            run = self.crud.get(db, run_id)
            if not run:
                logger.warning(f"Run not found: {run_id}")
                raise NotFoundError(
                    resource_type="Run",
                    resource_id=str(run_id)
                )

            # Delete run
            deleted = self.crud.delete(db, run_id)

            logger.info(f"Run deleted successfully: {run_id}")
            return deleted

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(f"Database error deleting run: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error deleting run: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while deleting run",
                details={"error": str(e)}
            )
