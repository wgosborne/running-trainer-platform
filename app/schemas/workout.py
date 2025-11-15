"""
Pydantic schemas for Workout model.

These schemas handle validation and serialization for workout data:
- WorkoutCreate: Validates data for creating a new workout
- WorkoutUpdate: Validates data for updating an existing workout
- WorkoutResponse: Serializes workout data for API responses
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, model_validator

from app.constants import WORKOUT_VALIDATION, WorkoutType


class WorkoutCreate(BaseModel):
    """
    Schema for creating a new workout.

    Attributes:
        name: Workout name (required)
        workout_type: Type of workout (EASY, TEMPO, LONG, etc.)
        planned_distance: Target distance in miles
        target_pace_min_sec: Minimum target pace in seconds per mile (optional)
        target_pace_max_sec: Maximum target pace in seconds per mile (optional)
        scheduled_date: Optional date when workout should be performed
        notes: Optional notes about the workout

    Validation:
        - workout_type must be a valid WorkoutType enum value
        - planned_distance must be > 0
        - If pace is provided, both min and max must be set
        - target_pace_min_sec must be <= target_pace_max_sec
    """

    name: str
    workout_type: str
    planned_distance: float
    target_pace_min_sec: Optional[int] = None
    target_pace_max_sec: Optional[int] = None
    scheduled_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate workout name is not empty."""
        if not v or not v.strip():
            raise ValueError("Workout name cannot be empty")
        return v.strip()

    @field_validator("workout_type")
    @classmethod
    def validate_workout_type(cls, v: str) -> str:
        """Validate workout type is a valid enum value."""
        valid_types = [wt.value for wt in WorkoutType]
        if v not in valid_types:
            raise ValueError(
                f"Invalid workout_type '{v}'. Must be one of: {', '.join(valid_types)}"
            )
        return v

    @field_validator("planned_distance")
    @classmethod
    def validate_distance(cls, v: float) -> float:
        """Validate planned distance is positive and within range."""
        if v < WORKOUT_VALIDATION.MIN_DISTANCE:
            raise ValueError(
                f"Planned distance must be at least {WORKOUT_VALIDATION.MIN_DISTANCE} miles"
            )
        if v > WORKOUT_VALIDATION.MAX_DISTANCE:
            raise ValueError(
                f"Planned distance cannot exceed {WORKOUT_VALIDATION.MAX_DISTANCE} miles"
            )
        return v

    @model_validator(mode="after")
    def validate_pace_range(self) -> "WorkoutCreate":
        """Validate pace range if provided."""
        min_pace = self.target_pace_min_sec
        max_pace = self.target_pace_max_sec

        # Both None is valid
        if min_pace is None and max_pace is None:
            return self

        # Both must be set if one is set
        if (min_pace is None) != (max_pace is None):
            raise ValueError(
                "Both target_pace_min_sec and target_pace_max_sec must be provided, or both must be omitted"
            )

        # Validate min pace
        if min_pace < WORKOUT_VALIDATION.MIN_PACE_SEC:
            raise ValueError(
                f"target_pace_min_sec cannot be faster than {WORKOUT_VALIDATION.MIN_PACE_SEC} seconds/mile"
            )
        if min_pace > WORKOUT_VALIDATION.MAX_PACE_SEC:
            raise ValueError(
                f"target_pace_min_sec cannot be slower than {WORKOUT_VALIDATION.MAX_PACE_SEC} seconds/mile"
            )

        # Validate max pace
        if max_pace < WORKOUT_VALIDATION.MIN_PACE_SEC:
            raise ValueError(
                f"target_pace_max_sec cannot be faster than {WORKOUT_VALIDATION.MIN_PACE_SEC} seconds/mile"
            )
        if max_pace > WORKOUT_VALIDATION.MAX_PACE_SEC:
            raise ValueError(
                f"target_pace_max_sec cannot be slower than {WORKOUT_VALIDATION.MAX_PACE_SEC} seconds/mile"
            )

        # Min must be <= max
        if min_pace > max_pace:
            raise ValueError(
                f"target_pace_min_sec ({min_pace}) must be <= target_pace_max_sec ({max_pace})"
            )

        return self

    model_config = {"from_attributes": True}


class WorkoutUpdate(BaseModel):
    """
    Schema for updating an existing workout.

    All fields are optional - only provided fields will be updated.

    Attributes:
        name: Optional new workout name
        workout_type: Optional new workout type
        planned_distance: Optional new planned distance
        target_pace_min_sec: Optional new minimum target pace
        target_pace_max_sec: Optional new maximum target pace
        scheduled_date: Optional new scheduled date
        notes: Optional new notes

    Validation:
        - Same validations as WorkoutCreate for non-None fields
    """

    name: Optional[str] = None
    workout_type: Optional[str] = None
    planned_distance: Optional[float] = None
    target_pace_min_sec: Optional[int] = None
    target_pace_max_sec: Optional[int] = None
    scheduled_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate workout name if provided."""
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Workout name cannot be empty")
        return v.strip()

    @field_validator("workout_type")
    @classmethod
    def validate_workout_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate workout type if provided."""
        if v is None:
            return v
        valid_types = [wt.value for wt in WorkoutType]
        if v not in valid_types:
            raise ValueError(
                f"Invalid workout_type '{v}'. Must be one of: {', '.join(valid_types)}"
            )
        return v

    @field_validator("planned_distance")
    @classmethod
    def validate_distance(cls, v: Optional[float]) -> Optional[float]:
        """Validate planned distance if provided."""
        if v is None:
            return v
        if v < WORKOUT_VALIDATION.MIN_DISTANCE:
            raise ValueError(
                f"Planned distance must be at least {WORKOUT_VALIDATION.MIN_DISTANCE} miles"
            )
        if v > WORKOUT_VALIDATION.MAX_DISTANCE:
            raise ValueError(
                f"Planned distance cannot exceed {WORKOUT_VALIDATION.MAX_DISTANCE} miles"
            )
        return v

    model_config = {"from_attributes": True}


class WorkoutResponse(BaseModel):
    """
    Schema for workout data in API responses.

    Includes all workout fields plus computed properties.

    Attributes:
        id: Unique workout identifier
        plan_id: Parent plan ID
        name: Workout name
        workout_type: Type of workout
        planned_distance: Target distance in miles
        target_pace_min_sec: Minimum target pace (optional)
        target_pace_max_sec: Maximum target pace (optional)
        scheduled_date: Scheduled date (optional)
        notes: Notes about the workout (optional)
        pace_range_str: Computed formatted pace range
        created_at: When the workout was created
        updated_at: When the workout was last modified
    """

    id: UUID
    plan_id: UUID
    name: str
    workout_type: str
    planned_distance: float
    target_pace_min_sec: Optional[int]
    target_pace_max_sec: Optional[int]
    scheduled_date: Optional[date]
    notes: Optional[str]
    pace_range_str: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
