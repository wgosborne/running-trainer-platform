"""
Test fixtures for Run model.

Provides factory functions for creating test run instances with
various configurations for use in unit and integration tests.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.run import Run
from app.constants import RunSource


def create_test_run(
    db_session: Session,
    plan_id: UUID,
    workout_id: Optional[UUID] = None,
    **kwargs
) -> Run:
    """
    Create a test run with default values.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan
        workout_id: Optional ID of associated workout
        **kwargs: Override default values

    Returns:
        Created Run instance

    Example:
        >>> run = create_test_run(db_session, plan.id, distance_miles=10.0)
    """
    defaults = {
        "plan_id": plan_id,
        "workout_id": workout_id,
        "distance_miles": 5.0,
        "pace_sec_per_mile": 600,  # 10:00/mile
        "date": datetime.now(timezone.utc),
        "source": RunSource.MANUAL.value,
        "notes": None,
        "external_id": None
    }

    # Merge defaults with provided kwargs
    run_data = {**defaults, **kwargs}

    # Create run
    run = Run(**run_data)

    # Add to database
    db_session.add(run)
    db_session.flush()  # Use flush instead of commit to maintain transaction isolation
    db_session.refresh(run)

    return run


def create_runs_for_plan(
    db_session: Session,
    plan_id: UUID,
    count: int = 5
) -> List[Run]:
    """
    Create multiple test runs for a plan.

    Creates runs with varying distances, paces, and dates.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan
        count: Number of runs to create

    Returns:
        List of created Run instances

    Example:
        >>> runs = create_runs_for_plan(db_session, plan.id, count=10)
        >>> len(runs)
        10
    """
    runs = []

    for i in range(count):
        # Vary distance: 3-10 miles
        distance = 3.0 + (i % 8)

        # Vary pace: 8:00-11:00/mile
        pace = 480 + (i % 4) * 60

        # Vary dates: spread across last week
        run_date = datetime.now(timezone.utc) - timedelta(days=count - i)

        run = create_test_run(
            db_session,
            plan_id,
            distance_miles=distance,
            pace_sec_per_mile=pace,
            date=run_date,
            notes=f"Test run {i + 1}"
        )
        runs.append(run)

    return runs


def create_slow_run(db_session: Session, plan_id: UUID) -> Run:
    """
    Create a test run at walking pace.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Run instance with slow pace
    """
    return create_test_run(
        db_session,
        plan_id,
        distance_miles=2.0,
        pace_sec_per_mile=2400,  # 40:00/mile (very slow walking)
        notes="Walking pace recovery"
    )


def create_fast_run(db_session: Session, plan_id: UUID) -> Run:
    """
    Create a test run at racing pace.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Run instance with fast pace
    """
    return create_test_run(
        db_session,
        plan_id,
        distance_miles=5.0,
        pace_sec_per_mile=300,  # 5:00/mile (racing pace)
        notes="Fast tempo effort"
    )


def create_strava_run(db_session: Session, plan_id: UUID) -> Run:
    """
    Create a test run from Strava import.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Run instance with STRAVA source
    """
    return create_test_run(
        db_session,
        plan_id,
        distance_miles=6.2,  # 10K
        pace_sec_per_mile=540,  # 9:00/mile
        source=RunSource.STRAVA.value,
        external_id="strava_12345678",
        notes="Morning run - imported from Strava"
    )


def create_long_run(db_session: Session, plan_id: UUID) -> Run:
    """
    Create a test long run.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Run instance with long distance
    """
    return create_test_run(
        db_session,
        plan_id,
        distance_miles=20.0,
        pace_sec_per_mile=600,  # 10:00/mile
        notes="Long Sunday run"
    )


def create_short_run(db_session: Session, plan_id: UUID) -> Run:
    """
    Create a test short recovery run.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Run instance with short distance
    """
    return create_test_run(
        db_session,
        plan_id,
        distance_miles=2.0,
        pace_sec_per_mile=720,  # 12:00/mile
        notes="Easy recovery run"
    )


def create_runs_with_workout(
    db_session: Session,
    plan_id: UUID,
    workout_id: UUID,
    count: int = 3
) -> List[Run]:
    """
    Create multiple runs associated with a specific workout.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan
        workout_id: ID of the associated workout
        count: Number of runs to create

    Returns:
        List of created Run instances

    Example:
        >>> runs = create_runs_with_workout(db_session, plan.id, workout.id, count=2)
        >>> all(run.workout_id == workout.id for run in runs)
        True
    """
    runs = []

    for i in range(count):
        run = create_test_run(
            db_session,
            plan_id,
            workout_id=workout_id,
            distance_miles=5.0 + i,
            pace_sec_per_mile=600 + i * 30,
            date=datetime.now(timezone.utc) - timedelta(days=i),
            notes=f"Workout attempt {i + 1}"
        )
        runs.append(run)

    return runs
