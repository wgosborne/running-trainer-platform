"""
CRUD operations for Plan model.

This module provides database operations for training plans:
- create: Create a new plan
- get: Retrieve a plan by ID
- get_all: Retrieve multiple plans with pagination
- update: Update an existing plan
- delete: Delete a plan
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import exc
from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate
from app.exceptions import DatabaseError, ValidationError
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


class PlanCRUD:
    """
    CRUD operations for Plan model.

    This class encapsulates all database operations for training plans,
    providing a clean interface for the service layer.
    """

    def create(self, db: Session, obj_in: PlanCreate) -> Plan:
        """
        Create a new training plan in the database.

        Args:
            db: Database session
            obj_in: Plan creation data

        Returns:
            The newly created Plan object

        Raises:
            ValidationError: If plan data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Creating plan: {obj_in.name}")

            # Create Plan instance from schema
            # Date validation is handled by the service layer
            db_plan = Plan(
                name=obj_in.name,
                description=obj_in.description,
                start_date=obj_in.start_date,
                end_date=obj_in.end_date,
            )

            # Add to database
            db.add(db_plan)
            db.flush()  # Flush to get the ID without committing

            logger.info(f"Plan created with ID: {db_plan.id}")
            return db_plan

        except ValidationError:
            # Re-raise validation errors as-is
            raise

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error creating plan: {e}")
            raise DatabaseError(
                message="Failed to create plan in database",
                details={"error": str(e)}
            )

        except Exception as e:
            logger.error(f"Unexpected error creating plan: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while creating plan",
                details={"error": str(e)}
            )

    def get(self, db: Session, plan_id: UUID) -> Optional[Plan]:
        """
        Retrieve a plan by its ID.

        Args:
            db: Database session
            plan_id: UUID of the plan to retrieve

        Returns:
            The Plan object if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Fetching plan: {plan_id}")

            plan = db.query(Plan).filter(Plan.id == plan_id).first()

            if plan:
                logger.info(f"Plan found: {plan_id}")
            else:
                logger.info(f"Plan not found: {plan_id}")

            return plan

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error fetching plan {plan_id}: {e}")
            raise DatabaseError(
                message=f"Failed to fetch plan {plan_id} from database",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching plan {plan_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching plan",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Plan]:
        """
        Retrieve multiple plans with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of Plan objects

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Fetching plans: skip={skip}, limit={limit}")

            plans = db.query(Plan).offset(skip).limit(limit).all()

            logger.info(f"Retrieved {len(plans)} plans")
            return plans

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error fetching plans: {e}")
            raise DatabaseError(
                message="Failed to fetch plans from database",
                details={"error": str(e)}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching plans: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching plans",
                details={"error": str(e)}
            )

    def update(
        self,
        db: Session,
        plan_id: UUID,
        obj_in: PlanUpdate
    ) -> Optional[Plan]:
        """
        Update an existing plan.

        Args:
            db: Database session
            plan_id: UUID of the plan to update
            obj_in: Plan update data

        Returns:
            The updated Plan object if found, None otherwise

        Raises:
            ValidationError: If update data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Updating plan: {plan_id}")

            # Get existing plan
            plan = self.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found for update: {plan_id}")
                return None

            # Update only provided fields
            update_data = obj_in.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(plan, field, value)

            # Date validation is handled by the service layer
            db.flush()  # Flush to validate without committing

            logger.info(f"Plan updated successfully: {plan_id}")
            return plan

        except ValidationError:
            # Re-raise validation errors as-is
            raise

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error updating plan {plan_id}: {e}")
            raise DatabaseError(
                message=f"Failed to update plan {plan_id} in database",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error updating plan {plan_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while updating plan",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

    def delete(self, db: Session, plan_id: UUID) -> bool:
        """
        Delete a plan by its ID.

        Args:
            db: Database session
            plan_id: UUID of the plan to delete

        Returns:
            True if plan was deleted, False if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Deleting plan: {plan_id}")

            # Get existing plan
            plan = self.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found for deletion: {plan_id}")
                return False

            # Delete the plan
            db.delete(plan)
            db.flush()  # Flush to validate without committing

            logger.info(f"Plan deleted successfully: {plan_id}")
            return True

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error deleting plan {plan_id}: {e}")
            raise DatabaseError(
                message=f"Failed to delete plan {plan_id} from database",
                details={"error": str(e), "plan_id": str(plan_id)}
            )

        except Exception as e:
            logger.error(f"Unexpected error deleting plan {plan_id}: {e}")
            raise DatabaseError(
                message="An unexpected error occurred while deleting plan",
                details={"error": str(e), "plan_id": str(plan_id)}
            )
