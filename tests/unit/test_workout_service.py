"""
Unit tests for WorkoutService.

Tests the business logic in the Workout service layer.
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.services.workout_service import WorkoutService
from app.schemas.workout import WorkoutCreate, WorkoutUpdate
from app.exceptions import ValidationError, NotFoundError
from app.constants import WorkoutType

from tests.fixtures import (
    create_test_plan,
    create_test_workout
)


class TestWorkoutService:
    """Test WorkoutService business logic."""

    @pytest.fixture
    def workout_service(self):
        """Create a WorkoutService instance for testing."""
        return WorkoutService()

    def test_create_workout_success(self, db_session, workout_service):
        """Test creating a workout with valid data."""
        plan = create_test_plan(db_session)

        workout_data = WorkoutCreate(
            name="Easy run",
            workout_type=WorkoutType.EASY,
            planned_distance=5.0,
            target_pace_min_sec=600,
            target_pace_max_sec=660,
            scheduled_date=date.today()
        )

        workout = workout_service.create_workout(db_session, plan.id, workout_data)

        assert workout.id is not None
        assert workout.name == "Easy run"
        assert workout.workout_type == WorkoutType.EASY.value
        assert workout.planned_distance == 5.0

    def test_create_workout_invalid_plan(self, db_session, workout_service):
        """Test creating workout for non-existent plan fails."""
        fake_plan_id = uuid4()

        workout_data = WorkoutCreate(
            name="Easy run",
            workout_type=WorkoutType.EASY,
            planned_distance=5.0
        )

        with pytest.raises(NotFoundError, match="Plan"):
            workout_service.create_workout(db_session, fake_plan_id, workout_data)

    def test_create_workout_all_types(self, db_session, workout_service):
        """Test creating workouts of all types."""
        plan = create_test_plan(db_session)

        workout_types = [
            WorkoutType.EASY,
            WorkoutType.TEMPO,
            WorkoutType.LONG,
            WorkoutType.SPEED,
            WorkoutType.RECOVERY
        ]

        for workout_type in workout_types:
            workout_data = WorkoutCreate(
                name=f"{workout_type.value} workout",
                workout_type=workout_type,
                planned_distance=5.0
            )

            workout = workout_service.create_workout(db_session, plan.id, workout_data)
            assert workout.workout_type == workout_type.value

    def test_get_workout_success(self, db_session, workout_service):
        """Test retrieving an existing workout."""
        plan = create_test_plan(db_session)
        created_workout = create_test_workout(db_session, plan.id)

        retrieved_workout = workout_service.get_workout(
            db_session,
            plan.id,
            created_workout.id
        )

        assert retrieved_workout.id == created_workout.id
        assert retrieved_workout.name == created_workout.name

    def test_get_workout_not_found(self, db_session, workout_service):
        """Test that retrieving non-existent workout raises NotFoundError."""
        plan = create_test_plan(db_session)
        fake_id = uuid4()

        with pytest.raises(NotFoundError, match="Workout"):
            workout_service.get_workout(db_session, plan.id, fake_id)

    def test_get_workouts_for_plan(self, db_session, workout_service):
        """Test retrieving all workouts for a plan."""
        plan = create_test_plan(db_session)

        # Create 3 workouts
        for i in range(3):
            create_test_workout(db_session, plan.id, name=f"Workout {i + 1}")

        workouts = workout_service.get_workouts_for_plan(db_session, plan.id)

        assert len(workouts) == 3

    def test_update_workout_success(self, db_session, workout_service):
        """Test updating an existing workout."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(db_session, plan.id, planned_distance=5.0)

        update_data = WorkoutUpdate(planned_distance=6.0)
        updated_workout = workout_service.update_workout(
            db_session,
            plan.id,
            workout.id,
            update_data
        )

        assert updated_workout.planned_distance == 6.0

    def test_delete_workout_success(self, db_session, workout_service):
        """Test deleting an existing workout."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(db_session, plan.id)

        result = workout_service.delete_workout(db_session, plan.id, workout.id)

        assert result is True

        with pytest.raises(NotFoundError):
            workout_service.get_workout(db_session, plan.id, workout.id)


class TestWorkoutModel:
    """Test Workout model methods and properties."""

    def test_workout_pace_range_str(self, db_session):
        """Test pace range string formatting."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(
            db_session,
            plan.id,
            target_pace_min_sec=600,  # 10:00
            target_pace_max_sec=660   # 11:00
        )

        assert workout.pace_range_str == "10:00-11:00/mile"

    def test_workout_has_target_pace(self, db_session):
        """Test has_target_pace() method."""
        plan = create_test_plan(db_session)

        workout_with_pace = create_test_workout(
            db_session,
            plan.id,
            target_pace_min_sec=600,
            target_pace_max_sec=660
        )
        assert workout_with_pace.has_target_pace() is True

        workout_no_pace = create_test_workout(
            db_session,
            plan.id,
            target_pace_min_sec=None,
            target_pace_max_sec=None
        )
        assert workout_no_pace.has_target_pace() is False

    def test_workout_is_rest_day(self, db_session):
        """Test is_rest_day() method."""
        plan = create_test_plan(db_session)

        rest_workout = create_test_workout(
            db_session,
            plan.id,
            workout_type=WorkoutType.REST.value
        )
        assert rest_workout.is_rest_day() is True

        easy_workout = create_test_workout(
            db_session,
            plan.id,
            workout_type=WorkoutType.EASY.value
        )
        assert easy_workout.is_rest_day() is False
