"""
Pydantic schemas for Run model.

These schemas handle validation and serialization for run data:
- RunCreate: Validates data for creating a new run
- RunUpdate: Validates data for updating an existing run
- RunResponse: Serializes run data for API responses
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.constants import RUN_VALIDATION


class RunCreate(BaseModel):
    """
    Schema for creating a new run.

    Attributes:
        workout_id: Optional workout ID this run is associated with
        distance_miles: Actual distance run in miles
        pace_sec_per_mile: Actual pace in seconds per mile
        date: When the run was performed
        notes: Optional notes about the run

    Validation:
        - distance_miles must be 0.1-100 miles
        - pace_sec_per_mile must be 180-3000 seconds/mile
        - date must be valid datetime
    """

    workout_id: Optional[UUID] = None
    distance_miles: float
    pace_sec_per_mile: int
    date: datetime
    notes: Optional[str] = None

    @field_validator("distance_miles")
    @classmethod
    def validate_distance(cls, v: float) -> float:
        """Validate run distance is within acceptable range."""
        if v < RUN_VALIDATION.MIN_DISTANCE:
            raise ValueError(
                f"Distance must be at least {RUN_VALIDATION.MIN_DISTANCE} miles"
            )
        if v > RUN_VALIDATION.MAX_DISTANCE:
            raise ValueError(
                f"Distance cannot exceed {RUN_VALIDATION.MAX_DISTANCE} miles"
            )
        return v

    @field_validator("pace_sec_per_mile")
    @classmethod
    def validate_pace(cls, v: int) -> int:
        """Validate run pace is within acceptable range."""
        if v < RUN_VALIDATION.MIN_PACE_SEC:
            raise ValueError(
                f"Pace cannot be faster than {RUN_VALIDATION.MIN_PACE_SEC} seconds/mile"
            )
        if v > RUN_VALIDATION.MAX_PACE_SEC:
            raise ValueError(
                f"Pace cannot be slower than {RUN_VALIDATION.MAX_PACE_SEC} seconds/mile"
            )
        return v

    model_config = {"from_attributes": True}


class RunUpdate(BaseModel):
    """
    Schema for updating an existing run.

    All fields are optional - only provided fields will be updated.

    Attributes:
        workout_id: Optional new workout ID (can be set to None to unlink)
        distance_miles: Optional new distance
        pace_sec_per_mile: Optional new pace
        date: Optional new date
        notes: Optional new notes

    Validation:
        - Same validations as RunCreate for non-None fields
    """

    workout_id: Optional[UUID] = None
    distance_miles: Optional[float] = None
    pace_sec_per_mile: Optional[int] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("distance_miles")
    @classmethod
    def validate_distance(cls, v: Optional[float]) -> Optional[float]:
        """Validate run distance if provided."""
        if v is None:
            return v
        if v < RUN_VALIDATION.MIN_DISTANCE:
            raise ValueError(
                f"Distance must be at least {RUN_VALIDATION.MIN_DISTANCE} miles"
            )
        if v > RUN_VALIDATION.MAX_DISTANCE:
            raise ValueError(
                f"Distance cannot exceed {RUN_VALIDATION.MAX_DISTANCE} miles"
            )
        return v

    @field_validator("pace_sec_per_mile")
    @classmethod
    def validate_pace(cls, v: Optional[int]) -> Optional[int]:
        """Validate run pace if provided."""
        if v is None:
            return v
        if v < RUN_VALIDATION.MIN_PACE_SEC:
            raise ValueError(
                f"Pace cannot be faster than {RUN_VALIDATION.MIN_PACE_SEC} seconds/mile"
            )
        if v > RUN_VALIDATION.MAX_PACE_SEC:
            raise ValueError(
                f"Pace cannot be slower than {RUN_VALIDATION.MAX_PACE_SEC} seconds/mile"
            )
        return v

    model_config = {"from_attributes": True}


class RunResponse(BaseModel):
    """
    Schema for run data in API responses.

    Includes all run fields plus computed properties.

    Attributes:
        id: Unique run identifier
        plan_id: Parent plan ID
        workout_id: Associated workout ID (optional)
        distance_miles: Actual distance run
        pace_sec_per_mile: Actual pace
        date: When the run was performed
        source: Source of run data (MANUAL, STRAVA)
        notes: Notes about the run (optional)
        pace_str: Computed formatted pace string
        created_at: When the run was created
        updated_at: When the run was last modified
    """

    id: UUID
    plan_id: UUID
    workout_id: Optional[UUID]
    distance_miles: float
    pace_sec_per_mile: int
    date: datetime
    source: str
    notes: Optional[str]
    pace_str: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
