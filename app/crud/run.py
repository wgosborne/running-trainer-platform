"""
CRUD operations for Run model.

This module provides database operations for runs:
- create: Create a new run
- get: Retrieve a run by ID
- get_all: Retrieve multiple runs with pagination
- get_by_plan: Retrieve runs for a specific plan
- update: Update an existing run
- delete: Delete a run
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import exc
from sqlalchemy.orm import Session

from app.models.run import Run
from app.schemas.run import RunCreate, RunUpdate
from app.exceptions import DatabaseError
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


class RunCRUD:
    """
    CRUD operations for Run model.

    This class encapsulates all database operations for runs,
    providing a clean interface for the service layer.
    """

    def create(self, db: Session, plan_id: UUID, obj_in: RunCreate) -> Run:
        """
        Create a new run in the database.

        Args:
            db: Database session
            plan_id: ID of the parent plan
            obj_in: Run creation data

        Returns:
            The newly created Run object

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Creating run for plan {plan_id}")

            # Create Run instance from schema
            db_run = Run(
                plan_id=plan_id,
                workout_id=obj_in.workout_id,
                distance_miles=obj_in.distance_miles,
                pace_sec_per_mile=obj_in.pace_sec_per_mile,
                date=obj_in.date,
                notes=obj_in.notes,
            )

            # Add to database
            db.add(db_run)
            db.flush()  # Flush to get the ID without committing

            logger.info(f"Run created with ID: {db_run.id}")
            return db_run

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error creating run: {e}")
            raise DatabaseError(
                message="Failed to create run in database",
                details={"error": str(e)}
            )

        except Exception as e:
            logger.error(f"Unexpected error creating run: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while creating run",
                details={"error": str(e)}
            )

    def get(self, db: Session, run_id: UUID) -> Optional[Run]:
        """
        Retrieve a run by its ID.

        Args:
            db: Database session
            run_id: UUID of the run to retrieve

        Returns:
            The Run object if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Fetching run: {run_id}")

            run = db.query(Run).filter(Run.id == run_id).first()

            if run:
                logger.info(f"Run found: {run_id}")
            else:
                logger.info(f"Run not found: {run_id}")

            return run

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error fetching run {run_id}: {e}")
            raise DatabaseError(
                message=f"Failed to fetch run {run_id} from database",
                details={"error": str(e), "run_id": str(run_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching run {run_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching run",
                details={"error": str(e), "run_id": str(run_id)}
            )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Run]:
        """
        Retrieve multiple runs with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of Run objects

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Fetching runs: skip={skip}, limit={limit}")

            runs = db.query(Run).offset(skip).limit(limit).all()

            logger.info(f"Retrieved {len(runs)} runs")
            return runs

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error fetching runs: {e}")
            raise DatabaseError(
                message="Failed to fetch runs from database",
                details={"error": str(e)}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching runs: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching runs",
                details={"error": str(e)}
            )

    def get_by_plan(
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
            plan_id: UUID of the parent plan
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of Run objects

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Fetching runs for plan {plan_id}: skip={skip}, limit={limit}")

            runs = (
                db.query(Run)
                .filter(Run.plan_id == plan_id)
                .offset(skip)
                .limit(limit)
                .all()
            )

            logger.info(f"Retrieved {len(runs)} runs for plan {plan_id}")
            return runs

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error fetching runs for plan {plan_id}: {e}")
            raise DatabaseError(
                message="Failed to fetch runs from database",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching runs for plan {plan_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching runs",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

    def update(
        self,
        db: Session,
        run_id: UUID,
        obj_in: RunUpdate
    ) -> Optional[Run]:
        """
        Update an existing run.

        Args:
            db: Database session
            run_id: UUID of the run to update
            obj_in: Run update data

        Returns:
            The updated Run object if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Updating run: {run_id}")

            # Get existing run
            run = self.get(db, run_id)
            if not run:
                logger.warning(f"Run not found for update: {run_id}")
                return None

            # Update only provided fields
            update_data = obj_in.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(run, field, value)

            db.flush()  # Flush to validate without committing

            logger.info(f"Run updated successfully: {run_id}")
            return run

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error updating run {run_id}: {e}")
            raise DatabaseError(
                message=f"Failed to update run {run_id} in database",
                details={"error": str(e), "run_id": str(run_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error updating run {run_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while updating run",
                details={"error": str(e), "run_id": str(run_id)}
            )

    def delete(self, db: Session, run_id: UUID) -> bool:
        """
        Delete a run by its ID.

        Args:
            db: Database session
            run_id: UUID of the run to delete

        Returns:
            True if run was deleted, False if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Deleting run: {run_id}")

            # Get existing run
            run = self.get(db, run_id)
            if not run:
                logger.warning(f"Run not found for deletion: {run_id}")
                return False

            # Delete the run
            db.delete(run)
            db.flush()  # Flush to validate without committing

            logger.info(f"Run deleted successfully: {run_id}")
            return True

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error deleting run {run_id}: {e}")
            raise DatabaseError(
                message=f"Failed to delete run {run_id} from database",
                details={"error": str(e), "run_id": str(run_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error deleting run {run_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while deleting run",
                details={"error": str(e), "run_id": str(run_id)}
            )
