"""
Run model for actual completed activities.

A run represents an actual completed training activity. It tracks the actual
distance, pace, and date of a run, and can optionally be associated with
a planned workout.

Migrations will be handled by alembic in Phase 3. For Phase 1, tables are created
on app startup via Base.metadata.create_all()
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.constants import RunSource
from app.models.base import Base, BaseMixin

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from app.models.plan import Plan
    from app.models.workout import Workout


class Run(Base, BaseMixin):
    """
    Run model representing an actual completed training activity.

    A run is the actual recorded activity data. It can be:
    - Manually entered by the user
    - Imported from Strava (Phase 2)

    Runs are associated with a plan (required) and optionally with a
    specific planned workout.

    Attributes:
        id: Unique identifier (UUID)
        plan_id: Foreign key to parent Plan
        workout_id: Optional foreign key to associated Workout
        distance_miles: Actual distance run in miles
        pace_sec_per_mile: Actual pace in seconds per mile
        date: When the run was performed
        source: How the run data was recorded (MANUAL, STRAVA)
        notes: Optional notes about the run
        external_id: Optional external ID (e.g., Strava activity ID)
        created_at: When the record was created
        updated_at: When the record was last modified
        plan: Parent training plan
        workout: Associated planned workout (optional)
    """

    __tablename__ = "runs"

    # Foreign keys
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the parent training plan"
    )

    workout_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workouts.id", ondelete="SET NULL"),
        nullable=True,
        doc="Optional foreign key to associated workout"
    )

    # Core fields
    distance_miles = Column(
        Float,
        nullable=False,
        doc="Actual distance run in miles"
    )

    pace_sec_per_mile = Column(
        Integer,
        nullable=False,
        doc="Actual pace in seconds per mile (e.g., 600 = 10:00/mile)"
    )

    date = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="When the run was performed (UTC)"
    )

    source = Column(
        String(50),
        nullable=False,
        default=RunSource.MANUAL.value,
        doc="Source of run data (MANUAL, STRAVA)"
    )

    notes = Column(
        String,
        nullable=True,
        doc="Optional notes about the run (how it felt, weather, etc.)"
    )

    external_id = Column(
        String(255),
        nullable=True,
        unique=True,
        doc="External ID for imported runs (e.g., Strava activity ID)"
    )

    # Relationships
    # Many-to-one with Plan
    plan: Mapped["Plan"] = relationship(
        "Plan",
        back_populates="runs"
    )

    # Many-to-one with Workout (optional)
    workout: Mapped[Optional["Workout"]] = relationship(
        "Workout",
        back_populates="runs"
    )

    # Table-level constraints and indexes
    __table_args__ = (
        Index("ix_runs_plan_id", "plan_id"),
        Index("ix_runs_date", "date"),
        Index("ix_runs_plan_date", "plan_id", "date"),
        Index("ix_runs_external_id", "external_id"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Run(id={self.id}, distance={self.distance_miles}mi, "
            f"pace={self.pace_str}, date={self.date.date()})>"
        )

    # Properties and helper methods

    @property
    def pace_str(self) -> str:
        """
        Format pace as human-readable string.

        Returns:
            Formatted pace (e.g., "10:00/mile")

        Example:
            >>> run = Run(pace_sec_per_mile=600)
            >>> run.pace_str
            '10:00/mile'
        """
        minutes = self.pace_sec_per_mile // 60
        seconds = self.pace_sec_per_mile % 60
        return f"{minutes}:{seconds:02d}/mile"

    @property
    def total_time_minutes(self) -> float:
        """
        Calculate total run time in minutes.

        Returns:
            Total time in minutes

        Example:
            >>> run = Run(distance_miles=5.0, pace_sec_per_mile=600)
            >>> run.total_time_minutes
            50.0
        """
        total_seconds = self.distance_miles * self.pace_sec_per_mile
        return total_seconds / 60

    def is_within_target(self, workout: "Workout", tolerance_sec: int = 30) -> bool:
        """
        Check if run pace is within target pace range of a workout.

        Args:
            workout: The workout to compare against
            tolerance_sec: Additional tolerance in seconds per mile (default: 30)

        Returns:
            True if pace is within target range (with tolerance), False otherwise
            Returns True if workout has no target pace (any pace is acceptable)

        Example:
            >>> workout = Workout(target_pace_min_sec=600, target_pace_max_sec=660)
            >>> run_slow = Run(pace_sec_per_mile=700)
            >>> run_slow.is_within_target(workout)
            False
            >>> run_good = Run(pace_sec_per_mile=630)
            >>> run_good.is_within_target(workout)
            True
        """
        # If workout has no target pace, any pace is acceptable
        if not workout.has_target_pace():
            return True

        # Check if pace is within range (with tolerance)
        min_acceptable = workout.target_pace_min_sec - tolerance_sec
        max_acceptable = workout.target_pace_max_sec + tolerance_sec

        return min_acceptable <= self.pace_sec_per_mile <= max_acceptable

    def is_within_distance(
        self,
        workout: "Workout",
        tolerance_percent: float = 10.0
    ) -> bool:
        """
        Check if run distance is within tolerance of workout planned distance.

        Args:
            workout: The workout to compare against
            tolerance_percent: Acceptable deviation percentage (default: 10%)

        Returns:
            True if distance is within tolerance, False otherwise

        Example:
            >>> workout = Workout(planned_distance=10.0)
            >>> run_short = Run(distance_miles=8.5)
            >>> run_short.is_within_distance(workout)
            False
            >>> run_good = Run(distance_miles=9.5)
            >>> run_good.is_within_distance(workout)
            True
        """
        min_acceptable = workout.planned_distance * (1 - tolerance_percent / 100)
        max_acceptable = workout.planned_distance * (1 + tolerance_percent / 100)

        return min_acceptable <= self.distance_miles <= max_acceptable

    def is_from_strava(self) -> bool:
        """
        Check if this run was imported from Strava.

        Returns:
            True if source is STRAVA, False otherwise
        """
        return self.source == RunSource.STRAVA.value

    def is_manual(self) -> bool:
        """
        Check if this run was manually entered.

        Returns:
            True if source is MANUAL, False otherwise
        """
        return self.source == RunSource.MANUAL.value

    def matches_workout(self, workout: "Workout") -> bool:
        """
        Check if this run is a good match for a workout.

        A run matches a workout if both pace and distance are within acceptable ranges.

        Args:
            workout: The workout to compare against

        Returns:
            True if both pace and distance match, False otherwise
        """
        return (
            self.is_within_target(workout) and
            self.is_within_distance(workout)
        )
