"""
Workout model for planned training activities.

A workout represents a planned training activity within a training plan.
It specifies the type, distance, target pace, and scheduled date.

Migrations will be handled by alembic in Phase 3. For Phase 1, tables are created
on app startup via Base.metadata.create_all()
"""

from datetime import date
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.constants import WorkoutType
from app.models.base import Base, BaseMixin

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from app.models.plan import Plan
    from app.models.run import Run


class Workout(Base, BaseMixin):
    """
    Workout model representing a planned training activity.

    A workout is a single planned activity within a training plan. It specifies:
    - What type of workout (easy, tempo, long, etc.)
    - How far to run (planned_distance)
    - Target pace range (optional)
    - When to do it (scheduled_date, optional)

    Multiple runs can be associated with a single workout to track completion.

    Attributes:
        id: Unique identifier (UUID)
        plan_id: Foreign key to parent Plan
        name: Human-readable name for the workout
        workout_type: Type of workout (EASY, TEMPO, LONG, etc.)
        planned_distance: Target distance in miles
        target_pace_min_sec: Minimum target pace in seconds per mile
        target_pace_max_sec: Maximum target pace in seconds per mile
        scheduled_date: Optional date when workout should be performed
        notes: Optional notes about the workout
        created_at: When the record was created
        updated_at: When the record was last modified
        plan: Parent training plan
        runs: Collection of runs associated with this workout
    """

    __tablename__ = "workouts"

    # Foreign key to Plan
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the parent training plan"
    )

    # Core fields
    name = Column(
        String(255),
        nullable=False,
        doc="Name of the workout (e.g., 'Tuesday easy run', 'Long run #3')"
    )

    workout_type = Column(
        String(50),
        nullable=False,
        doc="Type of workout (EASY, TEMPO, LONG, SPEED, RECOVERY, CROSS_TRAINING, REST)"
    )

    planned_distance = Column(
        Float,
        nullable=False,
        doc="Target distance in miles"
    )

    target_pace_min_sec = Column(
        Integer,
        nullable=True,
        doc="Minimum target pace in seconds per mile (e.g., 600 = 10:00/mile)"
    )

    target_pace_max_sec = Column(
        Integer,
        nullable=True,
        doc="Maximum target pace in seconds per mile (e.g., 660 = 11:00/mile)"
    )

    scheduled_date = Column(
        Date,
        nullable=True,
        doc="Optional scheduled date for this workout"
    )

    notes = Column(
        String,
        nullable=True,
        doc="Optional notes about the workout (terrain, weather, etc.)"
    )

    # Relationships
    # Many-to-one with Plan
    plan: Mapped["Plan"] = relationship(
        "Plan",
        back_populates="workouts"
    )

    # One-to-many with Run
    # No cascade delete - if workout deleted, runs remain with workout_id=None
    runs: Mapped[List["Run"]] = relationship(
        "Run",
        back_populates="workout"
    )

    # Table-level constraints and indexes
    __table_args__ = (
        Index("ix_workouts_plan_id", "plan_id"),
        Index("ix_workouts_scheduled_date", "scheduled_date"),
        Index("ix_workouts_plan_scheduled", "plan_id", "scheduled_date"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Workout(id={self.id}, name='{self.name}', "
            f"type={self.workout_type}, distance={self.planned_distance}mi)>"
        )

    # Validation methods

    def validate_pace(self) -> None:
        """
        Validate that target pace range is valid.

        Ensures that if both min and max paces are set, min <= max.
        Both can be None (no target pace), or both can be set.

        Raises:
            ValueError: If min_pace > max_pace or only one is set
        """
        min_pace = self.target_pace_min_sec
        max_pace = self.target_pace_max_sec

        # Both None is valid (no target pace)
        if min_pace is None and max_pace is None:
            return

        # Both must be set if one is set
        if (min_pace is None) != (max_pace is None):
            raise ValueError(
                "Both target_pace_min_sec and target_pace_max_sec must be set, "
                "or both must be None"
            )

        # Min must be <= max
        if min_pace > max_pace:
            raise ValueError(
                f"target_pace_min_sec ({min_pace}) must be <= "
                f"target_pace_max_sec ({max_pace})"
            )

    def validate_distance(self) -> None:
        """
        Validate that planned distance is positive.

        Raises:
            ValueError: If distance is <= 0
        """
        if self.planned_distance <= 0:
            raise ValueError(
                f"planned_distance must be positive, got {self.planned_distance}"
            )

    # Properties and helper methods

    @property
    def pace_range_str(self) -> Optional[str]:
        """
        Format pace range as human-readable string.

        Returns:
            Formatted pace range (e.g., "10:00-11:00/mile") or None if no target

        Example:
            >>> workout = Workout(target_pace_min_sec=600, target_pace_max_sec=660)
            >>> workout.pace_range_str
            '10:00-11:00/mile'
        """
        if self.target_pace_min_sec is None or self.target_pace_max_sec is None:
            return None

        min_minutes = self.target_pace_min_sec // 60
        min_seconds = self.target_pace_min_sec % 60
        max_minutes = self.target_pace_max_sec // 60
        max_seconds = self.target_pace_max_sec % 60

        return f"{min_minutes}:{min_seconds:02d}-{max_minutes}:{max_seconds:02d}/mile"

    def has_target_pace(self) -> bool:
        """
        Check if this workout has a target pace defined.

        Returns:
            True if both min and max target paces are set, False otherwise
        """
        return (
            self.target_pace_min_sec is not None and
            self.target_pace_max_sec is not None
        )

    def is_rest_day(self) -> bool:
        """
        Check if this workout is a rest day.

        Returns:
            True if workout_type is REST, False otherwise
        """
        return self.workout_type == WorkoutType.REST.value

    def is_cross_training(self) -> bool:
        """
        Check if this workout is cross training.

        Returns:
            True if workout_type is CROSS_TRAINING, False otherwise
        """
        return self.workout_type == WorkoutType.CROSS_TRAINING.value
