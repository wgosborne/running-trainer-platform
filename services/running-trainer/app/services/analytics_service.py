"""
Business logic for analytics and reporting.

This module contains the service layer for analytics operations.
Services calculate metrics, progress tracking, and training summaries.
"""

from datetime import timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.plan import PlanCRUD
from app.models.workout import Workout
from app.models.run import Run
from app.exceptions import NotFoundError, ValidationError, DatabaseError
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


class AnalyticsService:
    """
    Service class for analytics and reporting.

    This class handles calculations for plan progress, adherence metrics,
    and training summaries.
    """

    def __init__(self):
        """Initialize the service with CRUD instances."""
        self.plan_crud = PlanCRUD()

    def get_plan_progress(self, db: Session, plan_id: UUID) -> Dict[str, Any]:
        """
        Calculate progress metrics for a training plan.

        Args:
            db: Database session
            plan_id: UUID of the plan

        Returns:
            Dict containing:
                - total_workouts: Total planned workouts
                - completed_workouts: Workouts with at least one linked run
                - pending_workouts: Workouts without any runs
                - total_planned_distance: Sum of all workout distances
                - total_actual_distance: Sum of all run distances
                - adherence_percentage: Percentage of workouts completed

        Raises:
            NotFoundError: If plan does not exist
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Analytics: Calculating progress for plan {plan_id}")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Count total workouts
            total_workouts = (
                db.query(func.count(Workout.id))
                .filter(Workout.plan_id == plan_id)
                .scalar()
            ) or 0

            # Count completed workouts (workouts that have at least one run)
            completed_workouts = (
                db.query(func.count(func.distinct(Run.workout_id)))
                .filter(
                    Run.plan_id == plan_id,
                    Run.workout_id.isnot(None)
                )
                .scalar()
            ) or 0

            # Calculate pending workouts
            pending_workouts = total_workouts - completed_workouts

            # Calculate total planned distance
            total_planned_distance = (
                db.query(func.sum(Workout.planned_distance))
                .filter(Workout.plan_id == plan_id)
                .scalar()
            ) or 0.0

            # Calculate total actual distance
            total_actual_distance = (
                db.query(func.sum(Run.distance_miles))
                .filter(Run.plan_id == plan_id)
                .scalar()
            ) or 0.0

            # Calculate adherence percentage
            adherence_percentage = 0.0
            if total_workouts > 0:
                adherence_percentage = (completed_workouts / total_workouts) * 100

            result = {
                "total_workouts": total_workouts,
                "completed_workouts": completed_workouts,
                "pending_workouts": pending_workouts,
                "total_planned_distance": round(total_planned_distance, 2),
                "total_actual_distance": round(total_actual_distance, 2),
                "adherence_percentage": round(adherence_percentage, 1),
            }

            logger.info(f"Analytics: Progress calculated for plan {plan_id}: {result}")
            return result

        except NotFoundError:
            raise

        except Exception as e:
            logger.error(f"Error calculating plan progress: {e}")
            raise DatabaseError(
                message="Failed to calculate plan progress",
                details={"error": str(e)}
            )

    def get_weekly_summary(
        self,
        db: Session,
        plan_id: UUID,
        week_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get weekly summary for a plan.

        Args:
            db: Database session
            plan_id: UUID of the plan
            week_number: Optional week number (1-indexed). If None, returns current week.

        Returns:
            Dict containing:
                - week_number: Week number
                - start_date: Start date of the week
                - end_date: End date of the week
                - planned_distance: Total planned distance for the week
                - actual_distance: Total actual distance for the week
                - planned_runs: Number of planned workouts
                - completed_runs: Number of completed runs
                - runs: List of run details

        Raises:
            NotFoundError: If plan does not exist
            ValidationError: If week_number is invalid
            DatabaseError: If database operation fails
        """
        try:
            logger.info(f"Analytics: Getting weekly summary for plan {plan_id}, week {week_number}")

            # Verify plan exists
            plan = self.plan_crud.get(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id}")
                raise NotFoundError(
                    resource_type="Plan",
                    resource_id=str(plan_id)
                )

            # Calculate plan duration in weeks
            plan_duration_days = (plan.end_date - plan.start_date).days
            plan_duration_weeks = (plan_duration_days // 7) + 1

            # Default to week 1 if not specified
            if week_number is None:
                week_number = 1

            # Validate week number
            if week_number < 1 or week_number > plan_duration_weeks:
                raise ValidationError(
                    message=f"Invalid week_number. Must be between 1 and {plan_duration_weeks}"
                )

            # Calculate week start and end dates
            week_start_date = plan.start_date + timedelta(days=(week_number - 1) * 7)
            week_end_date = week_start_date + timedelta(days=6)

            # Don't extend beyond plan end date
            if week_end_date > plan.end_date:
                week_end_date = plan.end_date

            # Get workouts for the week
            week_workouts = (
                db.query(Workout)
                .filter(
                    Workout.plan_id == plan_id,
                    Workout.scheduled_date >= week_start_date,
                    Workout.scheduled_date <= week_end_date
                )
                .all()
            )

            # Calculate planned distance
            planned_distance = sum(w.planned_distance for w in week_workouts)
            planned_runs = len(week_workouts)

            # Get runs for the week
            week_runs = (
                db.query(Run)
                .filter(
                    Run.plan_id == plan_id,
                    func.date(Run.date) >= week_start_date,
                    func.date(Run.date) <= week_end_date
                )
                .all()
            )

            # Calculate actual distance
            actual_distance = sum(r.distance_miles for r in week_runs)
            completed_runs = len(week_runs)

            # Format run details
            run_details = [
                {
                    "id": str(run.id),
                    "date": run.date.isoformat(),
                    "distance_miles": run.distance_miles,
                    "pace_str": run.pace_str,
                    "notes": run.notes,
                }
                for run in week_runs
            ]

            result = {
                "week_number": week_number,
                "start_date": week_start_date.isoformat(),
                "end_date": week_end_date.isoformat(),
                "planned_distance": round(planned_distance, 2),
                "total_distance": round(actual_distance, 2),
                "planned_runs": planned_runs,
                "completed_runs": completed_runs,
                "runs": run_details,
            }

            logger.info(f"Analytics: Weekly summary calculated for plan {plan_id}, week {week_number}")
            return result

        except NotFoundError:
            raise

        except ValidationError:
            raise

        except Exception as e:
            logger.error(f"Error calculating weekly summary: {e}")
            raise DatabaseError(
                message="Failed to calculate weekly summary",
                details={"error": str(e)}
            )
