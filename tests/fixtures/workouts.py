"""
Test fixtures for Workout model.

Provides factory functions for creating test workout instances with
various configurations for use in unit and integration tests.
"""

from datetime import date, timedelta
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.constants import WorkoutType


def create_test_workout(
    db_session: Session,
    plan_id: UUID,
    **kwargs
) -> Workout:
    """
    Create a test workout with default values.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan
        **kwargs: Override default values

    Returns:
        Created Workout instance

    Example:
        >>> workout = create_test_workout(db_session, plan.id, planned_distance=10.0)
    """
    defaults = {
        "plan_id": plan_id,
        "name": "Easy run",
        "workout_type": WorkoutType.EASY.value,
        "planned_distance": 5.0,
        "target_pace_min_sec": 600,  # 10:00/mile
        "target_pace_max_sec": 660,  # 11:00/mile
        "scheduled_date": date.today(),
        "notes": None
    }

    # Merge defaults with provided kwargs
    workout_data = {**defaults, **kwargs}

    # Create workout
    workout = Workout(**workout_data)

    # Add to database
    db_session.add(workout)
    db_session.flush()  # Use flush instead of commit to maintain transaction isolation
    db_session.refresh(workout)

    return workout


def create_tempo_workout(db_session: Session, plan_id: UUID) -> Workout:
    """
    Create a test tempo workout.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Workout instance with TEMPO type
    """
    return create_test_workout(
        db_session,
        plan_id,
        name="Tempo run",
        workout_type=WorkoutType.TEMPO.value,
        planned_distance=8.0,
        target_pace_min_sec=480,  # 8:00/mile
        target_pace_max_sec=540,  # 9:00/mile
        notes="Comfortably hard pace"
    )


def create_long_run_workout(db_session: Session, plan_id: UUID) -> Workout:
    """
    Create a test long run workout.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Workout instance with LONG type
    """
    return create_test_workout(
        db_session,
        plan_id,
        name="Long run",
        workout_type=WorkoutType.LONG.value,
        planned_distance=16.0,
        target_pace_min_sec=540,  # 9:00/mile
        target_pace_max_sec=600,  # 10:00/mile
        notes="Maintain steady conversational pace"
    )


def create_speed_workout(db_session: Session, plan_id: UUID) -> Workout:
    """
    Create a test speed workout.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Workout instance with SPEED type
    """
    return create_test_workout(
        db_session,
        plan_id,
        name="Speed intervals",
        workout_type=WorkoutType.SPEED.value,
        planned_distance=6.0,
        target_pace_min_sec=360,  # 6:00/mile
        target_pace_max_sec=420,  # 7:00/mile
        notes="8x800m with 400m recovery jog"
    )


def create_recovery_workout(db_session: Session, plan_id: UUID) -> Workout:
    """
    Create a test recovery workout.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan

    Returns:
        Created Workout instance with RECOVERY type
    """
    return create_test_workout(
        db_session,
        plan_id,
        name="Recovery run",
        workout_type=WorkoutType.RECOVERY.value,
        planned_distance=3.0,
        target_pace_min_sec=660,  # 11:00/mile
        target_pace_max_sec=720,  # 12:00/mile
        notes="Very easy, conversational pace"
    )


def create_workouts_for_plan(
    db_session: Session,
    plan_id: UUID,
    count: int = 3
) -> List[Workout]:
    """
    Create multiple test workouts for a plan.

    Creates a variety of workout types with different distances and dates.

    Args:
        db_session: Database session
        plan_id: ID of the parent plan
        count: Number of workouts to create

    Returns:
        List of created Workout instances

    Example:
        >>> workouts = create_workouts_for_plan(db_session, plan.id, count=5)
        >>> len(workouts)
        5
    """
    workouts = []
    workout_types = [
        WorkoutType.EASY,
        WorkoutType.TEMPO,
        WorkoutType.LONG,
        WorkoutType.SPEED,
        WorkoutType.RECOVERY
    ]

    for i in range(count):
        # Cycle through workout types
        workout_type = workout_types[i % len(workout_types)]

        # Vary distance based on type
        if workout_type == WorkoutType.LONG:
            distance = 12.0 + i
        elif workout_type == WorkoutType.RECOVERY:
            distance = 3.0
        elif workout_type == WorkoutType.SPEED:
            distance = 5.0 + i * 0.5
        else:
            distance = 6.0 + i

        workout = create_test_workout(
            db_session,
            plan_id,
            name=f"{workout_type.value.title()} run {i + 1}",
            workout_type=workout_type.value,
            planned_distance=distance,
            scheduled_date=date.today() + timedelta(days=i * 2)
        )
        workouts.append(workout)

    return workouts
