"""
Business logic for workouts.

This module contains the service layer for workout operations.
Services handle business logic, validation, and coordinate between
API endpoints and CRUD operations.
"""

from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.workout import WorkoutCRUD
from app.crud.plan import PlanCRUD
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutUpdate
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


class WorkoutService:
    """
    Service class for workout business logic.

    This class handles business logic for workout operations including
    validation, authorization, and coordinating CRUD operations.
    """

    def __init__(self):
        """Initialize the service with CRUD instances."""
        self.crud = WorkoutCRUD()
        self.plan_crud = PlanCRUD()

    def create_workout(
        self,
        db: Session,
        plan_id: UUID,
        workout_data: WorkoutCreate
    ) -> Workout:
        """
        Create a new workout for a plan.

        Args:
            db: Database session
            plan_id: ID of the parent plan
            workout_data: Workout creation data

        Returns:
            The newly created Workout object

        Raises:
            NotFoundError: If plan does not exist
            ValidationError: If workout data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Creating workout for plan {plan_id}")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Create workout via CRUD
            workout = self.crud.create(db, plan_id, workout_data)

            logger.info(f"Workout created successfully: {workout.id}")
            return workout

        except NotFoundError:
            raise

        except ValidationError as e:
            logger.warning(f"Validation error creating workout: {str(e)}")
            raise

        except DatabaseError as e:
            logger.error(f"Database error creating workout: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error creating workout: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while creating workout",
                details={"error": str(e)}
            )

    def get_workout(
        self,
        db: Session,
        plan_id: UUID,
        workout_id: UUID
    ) -> Workout:
        """
        Retrieve a workout by ID.

        Args:
            db: Database session
            plan_id: ID of the parent plan
            workout_id: UUID of the workout to retrieve

        Returns:
            The Workout object

        Raises:
            NotFoundError: If plan or workout does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Fetching workout {workout_id} for plan {plan_id}")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Get workout
            workout = self.crud.get_by_plan_and_id(db, plan_id, workout_id)

            if not workout:
                logger.warning(f"Workout not found: {workout_id}")
                raise NotFoundError(
                    resource_type="Workout",
                    resource_id=str(workout_id)
                )

            logger.info(f"Workout retrieved successfully: {workout_id}")
            return workout

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(f"Database error fetching workout: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error fetching workout: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching workout",
                details={"error": str(e)}
            )

    def get_workouts_for_plan(
        self,
        db: Session,
        plan_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Workout]:
        """
        Retrieve workouts for a specific plan with pagination.

        Args:
            db: Database session
            plan_id: ID of the parent plan
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Workout objects

        Raises:
            NotFoundError: If plan does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Fetching workouts for plan {plan_id} (skip={skip}, limit={limit})")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Get workouts
            workouts = self.crud.get_by_plan(db, plan_id, skip=skip, limit=limit)

            logger.info(f"Retrieved {len(workouts)} workouts for plan {plan_id}")
            return workouts

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(f"Database error fetching workouts: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error fetching workouts: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching workouts",
                details={"error": str(e)}
            )

    def update_workout(
        self,
        db: Session,
        plan_id: UUID,
        workout_id: UUID,
        workout_data: WorkoutUpdate
    ) -> Workout:
        """
        Update an existing workout.

        Args:
            db: Session
            plan_id: ID of the parent plan
            workout_id: UUID of the workout to update
            workout_data: Workout update data

        Returns:
            The updated Workout object

        Raises:
            NotFoundError: If plan or workout does not exist
            ValidationError: If update data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Updating workout {workout_id} for plan {plan_id}")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Verify workout exists and belongs to plan
            workout = self.crud.get_by_plan_and_id(db, plan_id, workout_id)
            if not workout:
                logger.warning(f"Workout not found: {workout_id}")
                raise NotFoundError(
                    resource_type="Workout",
                    resource_id=str(workout_id)
                )

            # Update workout via CRUD
            updated_workout = self.crud.update(db, workout_id, workout_data)

            logger.info(f"Workout updated successfully: {workout_id}")
            return updated_workout

        except NotFoundError:
            raise

        except ValidationError as e:
            logger.warning(f"Validation error updating workout: {str(e)}")
            raise

        except DatabaseError as e:
            logger.error(f"Database error updating workout: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error updating workout: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while updating workout",
                details={"error": str(e)}
            )

    def delete_workout(
        self,
        db: Session,
        plan_id: UUID,
        workout_id: UUID
    ) -> bool:
        """
        Delete a workout by ID.

        Args:
            db: Database session
            plan_id: ID of the parent plan
            workout_id: UUID of the workout to delete

        Returns:
            True if workout was deleted

        Raises:
            NotFoundError: If plan or workout does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Deleting workout {workout_id} for plan {plan_id}")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Verify workout exists and belongs to plan
            workout = self.crud.get_by_plan_and_id(db, plan_id, workout_id)
            if not workout:
                logger.warning(f"Workout not found: {workout_id}")
                raise NotFoundError(
                    resource_type="Workout",
                    resource_id=str(workout_id)
                )

            # Delete workout
            deleted = self.crud.delete(db, workout_id)

            logger.info(f"Workout deleted successfully: {workout_id}")
            return deleted

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(f"Database error deleting workout: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error deleting workout: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while deleting workout",
                details={"error": str(e)}
            )
