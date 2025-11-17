"""
Training Plan model.

A training plan represents a complete training cycle with a defined start and end date.
It contains multiple workouts and tracks actual runs completed during the plan period.

Migrations will be handled by alembic in Phase 3. For Phase 1, tables are created
on app startup via Base.metadata.create_all()
"""

from datetime import date
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, String, Text, Date, Index
from sqlalchemy.orm import relationship, Mapped

from app.constants import PlanStatus
from app.models.base import Base, BaseMixin

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from app.models.workout import Workout
    from app.models.run import Run


class Plan(Base, BaseMixin):
    """
    Training plan model representing a complete training cycle.

    A plan is a time-bound training program that contains:
    - Multiple planned workouts (one-to-many)
    - Multiple actual runs (one-to-many)

    The plan has a defined lifecycle through statuses:
    - DRAFT: Being created/edited
    - ACTIVE: Currently being followed
    - COMPLETED: Successfully finished
    - ABANDONED: Stopped before completion

    Attributes:
        id: Unique identifier (UUID)
        name: Human-readable name for the plan
        description: Optional detailed description
        start_date: When the plan begins
        end_date: When the plan ends
        status: Current lifecycle status
        created_at: When the record was created
        updated_at: When the record was last modified
        workouts: Collection of planned workouts
        runs: Collection of actual runs
    """

    __tablename__ = "plans"

    # Core fields
    name = Column(
        String(255),
        nullable=False,
        doc="Name of the training plan (e.g., 'Marathon Training Spring 2024')"
    )

    description = Column(
        Text,
        nullable=True,
        doc="Optional detailed description of the plan goals and structure"
    )

    start_date = Column(
        Date,
        nullable=False,
        doc="Date when the training plan starts"
    )

    end_date = Column(
        Date,
        nullable=False,
        doc="Date when the training plan ends"
    )

    status = Column(
        String(50),
        nullable=False,
        default=PlanStatus.DRAFT.value,
        doc="Current status of the plan (DRAFT, ACTIVE, COMPLETED, ABANDONED)"
    )

    # Relationships
    # One-to-many with Workout - if plan deleted, delete all workouts
    workouts: Mapped[List["Workout"]] = relationship(
        "Workout",
        back_populates="plan",
        cascade="all, delete-orphan"
    )

    # One-to-many with Run - if plan deleted, delete all runs
    runs: Mapped[List["Run"]] = relationship(
        "Run",
        back_populates="plan",
        cascade="all, delete-orphan"
    )

    # Table-level constraints and indexes
    __table_args__ = (
        # Index for common queries
        Index("ix_plans_name", "name"),
        Index("ix_plans_status", "status"),
        Index("ix_plans_dates", "start_date", "end_date"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Plan(id={self.id}, name='{self.name}', "
            f"status={self.status}, dates={self.start_date} to {self.end_date})>"
        )

    # Validation methods

    def validate_dates(self) -> None:
        """
        Validate that start_date comes before end_date.

        Raises:
            ValueError: If end_date is before or equal to start_date
        """
        if self.end_date <= self.start_date:
            raise ValueError(
                f"Plan end_date ({self.end_date}) must be after "
                f"start_date ({self.start_date})"
            )

    # Properties and helper methods

    @property
    def duration_days(self) -> int:
        """
        Calculate the duration of the plan in days.

        Returns:
            Number of days between start_date and end_date (inclusive)

        Example:
            >>> plan = Plan(start_date=date(2024, 1, 1), end_date=date(2024, 1, 8))
            >>> plan.duration_days
            7
        """
        return (self.end_date - self.start_date).days

    def is_active(self) -> bool:
        """
        Check if the plan is currently active.

        Returns:
            True if status is ACTIVE, False otherwise

        Example:
            >>> plan = Plan(status=PlanStatus.ACTIVE.value)
            >>> plan.is_active()
            True
        """
        return self.status == PlanStatus.ACTIVE.value

    def is_draft(self) -> bool:
        """
        Check if the plan is in draft status.

        Returns:
            True if status is DRAFT, False otherwise
        """
        return self.status == PlanStatus.DRAFT.value

    def is_completed(self) -> bool:
        """
        Check if the plan is completed.

        Returns:
            True if status is COMPLETED, False otherwise
        """
        return self.status == PlanStatus.COMPLETED.value

    def is_abandoned(self) -> bool:
        """
        Check if the plan was abandoned.

        Returns:
            True if status is ABANDONED, False otherwise
        """
        return self.status == PlanStatus.ABANDONED.value
