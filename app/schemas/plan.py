"""
Pydantic schemas for Plan model.

These schemas handle validation and serialization for training plan data:
- PlanCreate: Validates data for creating a new plan
- PlanUpdate: Validates data for updating an existing plan
- PlanResponse: Serializes plan data for API responses
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, model_validator

from app.constants import PLAN_VALIDATION, PlanStatus


class PlanCreate(BaseModel):
    """
    Schema for creating a new training plan.

    Attributes:
        name: Plan name (1-255 characters)
        description: Optional detailed description
        start_date: When the plan begins
        end_date: When the plan ends

    Validation:
        - name must be 1-255 characters
        - start_date must be before end_date
        - dates must be valid date objects
    """

    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate plan name length.

        Args:
            v: The name value to validate

        Returns:
            The validated name

        Raises:
            ValueError: If name is empty or exceeds maximum length
        """
        if not v or not v.strip():
            raise ValueError("Plan name cannot be empty")

        if len(v) < PLAN_VALIDATION.MIN_NAME_LENGTH:
            raise ValueError(
                f"Plan name must be at least {PLAN_VALIDATION.MIN_NAME_LENGTH} character"
            )

        if len(v) > PLAN_VALIDATION.MAX_NAME_LENGTH:
            raise ValueError(
                f"Plan name cannot exceed {PLAN_VALIDATION.MAX_NAME_LENGTH} characters"
            )

        return v.strip()

    @model_validator(mode="after")
    def validate_dates(self) -> "PlanCreate":
        """
        Validate plan duration.

        Date ordering validation is handled by the service layer.

        Returns:
            The validated model instance

        Raises:
            ValueError: If duration exceeds maximum
        """
        duration = (self.end_date - self.start_date).days
        if duration > PLAN_VALIDATION.MAX_DAYS:
            raise ValueError(
                f"Plan duration cannot exceed {PLAN_VALIDATION.MAX_DAYS} days (got {duration} days)"
            )

        return self

    model_config = {"from_attributes": True}


class PlanUpdate(BaseModel):
    """
    Schema for updating an existing training plan.

    All fields are optional - only provided fields will be updated.

    Attributes:
        name: Optional new plan name
        description: Optional new description
        start_date: Optional new start date
        end_date: Optional new end date
        status: Optional new status

    Validation:
        - If name provided, must be 1-255 characters
        - If both dates provided, start_date must be before end_date
    """

    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate plan name length if provided.

        Args:
            v: The name value to validate

        Returns:
            The validated name or None

        Raises:
            ValueError: If name is empty or exceeds maximum length
        """
        if v is None:
            return v

        if not v or not v.strip():
            raise ValueError("Plan name cannot be empty")

        if len(v) < PLAN_VALIDATION.MIN_NAME_LENGTH:
            raise ValueError(
                f"Plan name must be at least {PLAN_VALIDATION.MIN_NAME_LENGTH} character"
            )

        if len(v) > PLAN_VALIDATION.MAX_NAME_LENGTH:
            raise ValueError(
                f"Plan name cannot exceed {PLAN_VALIDATION.MAX_NAME_LENGTH} characters"
            )

        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate plan status if provided.

        Args:
            v: The status value to validate

        Returns:
            The validated status or None

        Raises:
            ValueError: If status is not a valid PlanStatus value
        """
        if v is None:
            return v

        valid_statuses = [status.value for status in PlanStatus]
        if v not in valid_statuses:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(valid_statuses)}"
            )

        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "PlanUpdate":
        """
        Validate plan duration if both dates are provided.

        Date ordering validation is handled by the service layer.

        Returns:
            The validated model instance

        Raises:
            ValueError: If duration exceeds maximum
        """
        # Only validate if both dates are provided
        if self.start_date is not None and self.end_date is not None:
            duration = (self.end_date - self.start_date).days
            if duration > PLAN_VALIDATION.MAX_DAYS:
                raise ValueError(
                    f"Plan duration cannot exceed {PLAN_VALIDATION.MAX_DAYS} days (got {duration} days)"
                )

        return self

    model_config = {"from_attributes": True}


class PlanResponse(BaseModel):
    """
    Schema for plan data in API responses.

    Includes all plan fields plus computed properties.

    Attributes:
        id: Unique plan identifier
        name: Plan name
        description: Optional description
        start_date: When the plan begins
        end_date: When the plan ends
        status: Current plan status
        created_at: When the plan was created
        updated_at: When the plan was last modified
        duration_days: Computed plan duration in days
    """

    id: UUID
    name: str
    description: Optional[str]
    start_date: date
    end_date: date
    status: str
    created_at: datetime
    updated_at: datetime
    duration_days: int

    model_config = {"from_attributes": True}
