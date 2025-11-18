"""
Application constants and enums.

This module defines all enums and validation constants used throughout the application.
Centralizing these values ensures consistency and makes updates easier.
"""

from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================


class PlanStatus(str, Enum):
    """
    Status of a training plan.

    DRAFT: Plan is being created/edited, not yet active
    ACTIVE: Plan is currently being followed by the user
    COMPLETED: User has finished the plan successfully
    ABANDONED: User stopped following the plan before completion
    """
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class WorkoutType(str, Enum):
    """
    Type of workout or run.

    EASY: Easy-paced recovery or base-building run
    TEMPO: Moderate-to-hard sustained effort run
    LONG: Extended distance run for endurance
    SPEED: High-intensity intervals or track work
    RECOVERY: Very easy run for active recovery
    CROSS_TRAINING: Non-running cardio (cycling, swimming, etc.)
    REST: Complete rest day, no activity
    """
    EASY = "EASY"
    TEMPO = "TEMPO"
    LONG = "LONG"
    SPEED = "SPEED"
    RECOVERY = "RECOVERY"
    CROSS_TRAINING = "CROSS_TRAINING"
    REST = "REST"


class RunSource(str, Enum):
    """
    Source of run data.

    MANUAL: User manually entered the run data
    STRAVA: Run imported from Strava integration
    """
    MANUAL = "MANUAL"
    STRAVA = "STRAVA"


# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================


class RUN_VALIDATION:
    """
    Validation constants for run data.

    These constraints ensure data quality and prevent obviously invalid entries.
    """

    # Distance constraints (in kilometers)
    MIN_DISTANCE: float = 0.1  # Minimum run distance: 100 meters
    MAX_DISTANCE: float = 100.0  # Maximum run distance: 100 km (ultra territory)

    # Pace constraints (in seconds per kilometer)
    MIN_PACE_SEC: int = 180  # Fastest pace: 3:00/km (world-class speed)
    MAX_PACE_SEC: int = 3000  # Slowest pace: 50:00/km (very slow walking)


class WORKOUT_VALIDATION:
    """
    Validation constants for planned workout data.

    Uses same constraints as runs since workouts represent planned runs.
    """

    # Distance constraints (in kilometers)
    MIN_DISTANCE: float = 0.1  # Minimum workout distance: 100 meters
    MAX_DISTANCE: float = 100.0  # Maximum workout distance: 100 km

    # Pace constraints (in seconds per kilometer)
    MIN_PACE_SEC: int = 180  # Fastest target pace: 3:00/km
    MAX_PACE_SEC: int = 3000  # Slowest target pace: 50:00/km


class PLAN_VALIDATION:
    """
    Validation constants for training plan data.

    These constraints ensure plans are reasonable and well-formed.
    """

    # Plan name constraints
    MIN_NAME_LENGTH: int = 1  # Plan name must have at least 1 character
    MAX_NAME_LENGTH: int = 255  # Maximum plan name length

    # Duration constraints (in days)
    MIN_DAYS: int = 1  # Minimum plan duration: 1 day
    MAX_DAYS: int = 365  # Maximum plan duration: 1 year


# ============================================================================
# APPLICATION CONSTANTS
# ============================================================================


class API_CONSTANTS:
    """
    Constants related to API behavior and limits.

    These can be adjusted based on performance and business requirements.
    """

    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 20  # Default number of items per page
    MAX_PAGE_SIZE: int = 100  # Maximum items that can be requested per page

    # API rate limiting
    RATE_LIMIT_READ_OPS: str = "100/minute"  # Read operations (GET)
    RATE_LIMIT_WRITE_OPS: str = "100/minute"  # Write operations (POST, PUT, PATCH, DELETE) - increased for PDF imports
    RATE_LIMIT_STRICT: str = "10/minute"  # Very strict limit for sensitive operations

    # Request size limits
    MAX_REQUEST_SIZE_BYTES: int = 10_000_000  # 10MB maximum request body size


# ============================================================================
# DATABASE CONSTANTS
# ============================================================================


class DB_CONSTANTS:
    """
    Constants related to database configuration and behavior.

    These affect connection pooling and query behavior.
    """

    # Connection pool settings
    POOL_SIZE: int = 5  # Number of permanent connections in the pool
    MAX_OVERFLOW: int = 10  # Maximum overflow connections beyond pool_size
    POOL_TIMEOUT: int = 30  # Seconds to wait before giving up on getting a connection
    POOL_RECYCLE: int = 3600  # Seconds before recycling connections (1 hour)
