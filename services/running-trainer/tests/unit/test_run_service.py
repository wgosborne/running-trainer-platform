"""
Unit tests for RunService.

Tests the business logic in the Run service layer.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.services.run_service import RunService
from app.schemas.run import RunCreate, RunUpdate
from app.exceptions import ValidationError, NotFoundError
from app.constants import RunSource

from tests.fixtures import (
    create_test_plan,
    create_test_workout,
    create_test_run
)


class TestRunService:
    """Test RunService business logic."""

    @pytest.fixture
    def run_service(self):
        """Create a RunService instance for testing."""
        return RunService()

    def test_create_run_success(self, db_session, run_service):
        """Test creating a run with valid data."""
        plan = create_test_plan(db_session)

        run_data = RunCreate(
            distance_miles=5.0,
            pace_sec_per_mile=600,  # 10:00/mile
            date=datetime.now(timezone.utc),
            source=RunSource.MANUAL
        )

        run = run_service.create_run(db_session, plan.id, run_data)

        assert run.id is not None
        assert run.distance_miles == 5.0
        assert run.pace_sec_per_mile == 600
        assert run.source == RunSource.MANUAL.value

    def test_create_run_with_workout_link(self, db_session, run_service):
        """Test creating a run linked to a workout."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(db_session, plan.id)

        run_data = RunCreate(
            distance_miles=5.0,
            pace_sec_per_mile=600,
            date=datetime.now(timezone.utc),
            source=RunSource.MANUAL,
            workout_id=workout.id
        )

        run = run_service.create_run(db_session, plan.id, run_data)

        assert run.workout_id == workout.id

    def test_create_run_invalid_plan(self, db_session, run_service):
        """Test creating run for non-existent plan fails."""
        fake_plan_id = uuid4()

        run_data = RunCreate(
            distance_miles=5.0,
            pace_sec_per_mile=600,
            date=datetime.now(timezone.utc),
            source=RunSource.MANUAL
        )

        with pytest.raises(NotFoundError, match="Plan"):
            run_service.create_run(db_session, fake_plan_id, run_data)

    def test_create_run_invalid_workout(self, db_session, run_service):
        """Test creating run with non-existent workout fails."""
        plan = create_test_plan(db_session)
        fake_workout_id = uuid4()

        run_data = RunCreate(
            distance_miles=5.0,
            pace_sec_per_mile=600,
            date=datetime.now(timezone.utc),
            source=RunSource.MANUAL,
            workout_id=fake_workout_id
        )

        with pytest.raises(NotFoundError, match="Workout"):
            run_service.create_run(db_session, plan.id, run_data)

    def test_get_run_success(self, db_session, run_service):
        """Test retrieving an existing run."""
        plan = create_test_plan(db_session)
        created_run = create_test_run(db_session, plan.id)

        retrieved_run = run_service.get_run(db_session, created_run.id)

        assert retrieved_run.id == created_run.id
        assert retrieved_run.distance_miles == created_run.distance_miles

    def test_get_run_not_found(self, db_session, run_service):
        """Test that retrieving non-existent run raises NotFoundError."""
        fake_id = uuid4()

        with pytest.raises(NotFoundError, match="Run"):
            run_service.get_run(db_session, fake_id)

    def test_update_run_success(self, db_session, run_service):
        """Test updating an existing run."""
        plan = create_test_plan(db_session)
        run = create_test_run(db_session, plan.id, distance_miles=5.0)

        update_data = RunUpdate(distance_miles=6.0)
        updated_run = run_service.update_run(db_session, run.id, update_data)

        assert updated_run.distance_miles == 6.0

    def test_delete_run_success(self, db_session, run_service):
        """Test deleting an existing run."""
        plan = create_test_plan(db_session)
        run = create_test_run(db_session, plan.id)

        result = run_service.delete_run(db_session, run.id)

        assert result is True

        with pytest.raises(NotFoundError):
            run_service.get_run(db_session, run.id)


class TestRunModel:
    """Test Run model methods and properties."""

    def test_run_pace_str_formatting(self, db_session):
        """Test run pace string formatting."""
        plan = create_test_plan(db_session)
        run = create_test_run(db_session, plan.id, pace_sec_per_mile=600)

        assert run.pace_str == "10:00/mile"

    def test_run_total_time_minutes(self, db_session):
        """Test total time calculation."""
        plan = create_test_plan(db_session)
        run = create_test_run(
            db_session,
            plan.id,
            distance_miles=5.0,
            pace_sec_per_mile=600  # 10:00/mile
        )

        # 5 miles * 10 minutes = 50 minutes
        assert run.total_time_minutes == 50.0

    def test_run_is_manual(self, db_session):
        """Test is_manual() method."""
        plan = create_test_plan(db_session)
        run = create_test_run(
            db_session,
            plan.id,
            source=RunSource.MANUAL.value
        )

        assert run.is_manual() is True
        assert run.is_from_strava() is False
