"""
CRUD operations for Workout model.

This module provides database operations for workouts:
- create: Create a new workout
- get: Retrieve a workout by ID
- get_all: Retrieve multiple workouts with pagination
- get_by_plan: Retrieve workouts for a specific plan
- update: Update an existing workout
- delete: Delete a workout
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import exc
from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutUpdate
from app.exceptions import DatabaseError, ValidationError
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


class WorkoutCRUD:
    """
    CRUD operations for Workout model.

    This class encapsulates all database operations for workouts,
    providing a clean interface for the service layer.
    """

    def create(self, db: Session, plan_id: UUID, obj_in: WorkoutCreate) -> Workout:
        """
        Create a new workout in the database.

        Args:
            db: Database session
            plan_id: ID of the parent plan
            obj_in: Workout creation data

        Returns:
            The newly created Workout object

        Raises:
            ValidationError: If workout data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Creating workout: {obj_in.name} for plan {plan_id}")

            # Create Workout instance from schema
            db_workout = Workout(
                plan_id=plan_id,
                name=obj_in.name,
                workout_type=obj_in.workout_type,
                planned_distance=obj_in.planned_distance,
                target_pace_min_sec=obj_in.target_pace_min_sec,
                target_pace_max_sec=obj_in.target_pace_max_sec,
                scheduled_date=obj_in.scheduled_date,
                notes=obj_in.notes,
            )

            # Add to database
            db.add(db_workout)
            db.flush()  # Flush to get the ID without committing

            logger.info(f"Workout created with ID: {db_workout.id}")
            return db_workout

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error creating workout: {e}")
            raise DatabaseError(
                message="Failed to create workout in database",
                details={"error": str(e)}
            )

        except Exception as e:
            logger.error(f"Unexpected error creating workout: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while creating workout",
                details={"error": str(e)}
            )

    def get(self, db: Session, workout_id: UUID) -> Optional[Workout]:
        """
        Retrieve a workout by its ID.

        Args:
            db: Database session
            workout_id: UUID of the workout to retrieve

        Returns:
            The Workout object if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Fetching workout: {workout_id}")

            workout = db.query(Workout).filter(Workout.id == workout_id).first()

            if workout:
                logger.info(f"Workout found: {workout_id}")
            else:
                logger.info(f"Workout not found: {workout_id}")

            return workout

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error fetching workout {workout_id}: {e}")
            raise DatabaseError(
                message=f"Failed to fetch workout {workout_id} from database",
                details={"error": str(e), "workout_id": str(workout_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching workout {workout_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching workout",
                details={"error": str(e), "workout_id": str(workout_id)}
            )

    def get_by_plan(
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
            plan_id: UUID of the parent plan
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of Workout objects

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Fetching workouts for plan {plan_id}: skip={skip}, limit={limit}")

            workouts = (
                db.query(Workout)
                .filter(Workout.plan_id == plan_id)
                .offset(skip)
                .limit(limit)
                .all()
            )

            logger.info(f"Retrieved {len(workouts)} workouts for plan {plan_id}")
            return workouts

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error fetching workouts for plan {plan_id}: {e}")
            raise DatabaseError(
                message="Failed to fetch workouts from database",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching workouts for plan {plan_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching workouts",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

    def get_by_plan_and_id(
        self,
        db: Session,
        plan_id: UUID,
        workout_id: UUID
    ) -> Optional[Workout]:
        """
        Retrieve a workout by plan ID and workout ID.

        Args:
            db: Database session
            plan_id: UUID of the parent plan
            workout_id: UUID of the workout

        Returns:
            The Workout object if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Fetching workout {workout_id} for plan {plan_id}")

            workout = (
                db.query(Workout)
                .filter(Workout.id == workout_id, Workout.plan_id == plan_id)
                .first()
            )

            if workout:
                logger.info(f"Workout found: {workout_id}")
            else:
                logger.info(f"Workout not found: {workout_id} for plan {plan_id}")

            return workout

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error fetching workout: {e}")
            raise DatabaseError(
                message="Failed to fetch workout from database",
                details={"error": str(e), "workout_id": str(workout_id), "plan_id": str(plan_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching workout: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching workout",
                details={"error": str(e), "workout_id": str(workout_id), "plan_id": str(plan_id)}
            )

    def update(
        self,
        db: Session,
        workout_id: UUID,
        obj_in: WorkoutUpdate
    ) -> Optional[Workout]:
        """
        Update an existing workout.

        Args:
            db: Database session
            workout_id: UUID of the workout to update
            obj_in: Workout update data

        Returns:
            The updated Workout object if found, None otherwise

        Raises:
            ValidationError: If update data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Updating workout: {workout_id}")

            # Get existing workout
            workout = self.get(db, workout_id)
            if not workout:
                logger.warning(f"Workout not found for update: {workout_id}")
                return None

            # Update only provided fields
            update_data = obj_in.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(workout, field, value)

            db.flush()  # Flush to validate without committing

            logger.info(f"Workout updated successfully: {workout_id}")
            return workout

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error updating workout {workout_id}: {e}")
            raise DatabaseError(
                message=f"Failed to update workout {workout_id} in database",
                details={"error": str(e), "workout_id": str(workout_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error updating workout {workout_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while updating workout",
                details={"error": str(e), "workout_id": str(workout_id)}
            )

    def delete(self, db: Session, workout_id: UUID) -> bool:
        """
        Delete a workout by its ID.

        Args:
            db: Database session
            workout_id: UUID of the workout to delete

        Returns:
            True if workout was deleted, False if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Deleting workout: {workout_id}")

            # Get existing workout
            workout = self.get(db, workout_id)
            if not workout:
                logger.warning(f"Workout not found for deletion: {workout_id}")
                return False

            # Delete the workout
            db.delete(workout)
            db.flush()  # Flush to validate without committing

            logger.info(f"Workout deleted successfully: {workout_id}")
            return True

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error deleting workout {workout_id}: {e}")
            raise DatabaseError(
                message=f"Failed to delete workout {workout_id} from database",
                details={"error": str(e), "workout_id": str(workout_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error deleting workout {workout_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while deleting workout",
                details={"error": str(e), "workout_id": str(workout_id)}
            )
