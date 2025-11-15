"""
Business logic for training plans.

This module contains the service layer for training plan operations.
Services handle business logic, validation, and coordinate between
API endpoints and CRUD operations.
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.plan import PlanCRUD
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate
from app.exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


class PlanService:
    """
    Service class for training plan business logic.

    This class handles business logic for plan operations including
    validation, authorization, and coordinating CRUD operations.
    """

    def __init__(self):
        """Initialize the service with a CRUD instance."""
        self.crud = PlanCRUD()

    def validate_plan_dates(self, start_date: date, end_date: date) -> bool:
        """
        Validate that plan dates are logical.

        Args:
            start_date: Plan start date
            end_date: Plan end date

        Returns:
            True if dates are valid

        Raises:
            ValidationError: If dates are invalid
        """
        logger.debug(f"Validating plan dates: {start_date} to {end_date}")

        if end_date <= start_date:
            error_msg = f"Plan end_date ({end_date}) must be after start_date ({start_date})"
            logger.warning(f"Date validation failed: {error_msg}")
            raise ValidationError(message=error_msg)

        logger.debug("Plan dates are valid")
        return True

    def create_plan(self, db: Session, plan_data: PlanCreate) -> Plan:
        """
        Create a new training plan.

        Args:
            db: Database session
            plan_data: Plan creation data

        Returns:
            The newly created Plan object

        Raises:
            ValidationError: If plan data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Creating plan '{plan_data.name}'")

            # Validate dates
            self.validate_plan_dates(plan_data.start_date, plan_data.end_date)

            # Create plan via CRUD
            plan = self.crud.create(db, plan_data)

            logger.info(f"Plan created successfully: {plan.id}")
            return plan

        except ValidationError as e:
            logger.warning(f"Validation error creating plan: {str(e)}")
            raise

        except DatabaseError as e:
            logger.error(f"Database error creating plan: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error creating plan: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while creating plan",
                details={"error": str(e)}
            )

    def get_plan(self, db: Session, plan_id: UUID) -> Plan:
        """
        Retrieve a plan by ID.

        Args:
            db: Database session
            plan_id: UUID of the plan to retrieve

        Returns:
            The Plan object

        Raises:
            NotFoundError: If plan does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Fetching plan {plan_id}")

            plan = self.crud.get(db, plan_id)

            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            logger.info(f"Plan retrieved successfully: {plan_id}")
            return plan

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(f"Database error fetching plan: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error fetching plan: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching plan",
                details={"error": str(e)}
            )

    def get_all_plans(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Plan]:
        """
        Retrieve multiple plans with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Plan objects

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Fetching plans (skip={skip}, limit={limit})")

            plans = self.crud.get_all(db, skip=skip, limit=limit)

            logger.info(f"Retrieved {len(plans)} plans")
            return plans

        except DatabaseError as e:
            logger.error(f"Database error fetching plans: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error fetching plans: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while fetching plans",
                details={"error": str(e)}
            )

    def update_plan(
        self,
        db: Session,
        plan_id: UUID,
        plan_data: PlanUpdate
    ) -> Plan:
        """
        Update an existing plan.

        Args:
            db: Database session
            plan_id: UUID of the plan to update
            plan_data: Plan update data

        Returns:
            The updated Plan object

        Raises:
            NotFoundError: If plan does not exist
            ValidationError: If update data is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Updating plan {plan_id}")

            # Get existing plan to validate dates
            existing_plan = self.crud.get(db, plan_id)
            if not existing_plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Validate dates if both are being updated or one is being updated
            start_date = plan_data.start_date if plan_data.start_date is not None else existing_plan.start_date
            end_date = plan_data.end_date if plan_data.end_date is not None else existing_plan.end_date

            # Validate the combined dates
            self.validate_plan_dates(start_date, end_date)

            # Update plan via CRUD
            plan = self.crud.update(db, plan_id, plan_data)

            logger.info(f"Plan updated successfully: {plan_id}")
            return plan

        except NotFoundError:
            raise

        except ValidationError as e:
            logger.warning(f"Validation error updating plan: {str(e)}")
            raise

        except DatabaseError as e:
            logger.error(f"Database error updating plan: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error updating plan: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while updating plan",
                details={"error": str(e)}
            )

    def delete_plan(self, db: Session, plan_id: UUID) -> bool:
        """
        Delete a plan by ID.

        Args:
            db: Database session
            plan_id: UUID of the plan to delete

        Returns:
            True if plan was deleted

        Raises:
            NotFoundError: If plan does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Service: Deleting plan {plan_id}")

            deleted = self.crud.delete(db, plan_id)

            if not deleted:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            logger.info(f"Plan deleted successfully: {plan_id}")
            return True

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(f"Database error deleting plan: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error deleting plan: {str(e)}")
            raise DatabaseError(
                message="An unexpected error occurred while deleting plan",
                details={"error": str(e)}
            )
