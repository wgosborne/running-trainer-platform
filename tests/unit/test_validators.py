"""
Unit tests for validation logic.

Tests validation methods in model classes and service layers to ensure
proper validation of user input and business rules.
"""

import pytest
from datetime import date, timedelta

from app.models.plan import Plan
from app.models.workout import Workout
from app.models.run import Run
from app.constants import RUN_VALIDATION, WORKOUT_VALIDATION


class TestPlanValidation:
    """Test Plan model validation methods."""

    def test_validate_plan_dates_valid(self):
        """Test that valid plan dates pass validation."""
        plan = Plan(
            name="Test Plan",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )

        # Should not raise exception
        plan.validate_dates()

    def test_validate_plan_dates_invalid_same_date(self):
        """Test that same start and end dates fail validation."""
        plan = Plan(
            name="Test Plan",
            start_date=date.today(),
            end_date=date.today()
        )

        with pytest.raises(ValueError, match="must be after"):
            plan.validate_dates()

    def test_validate_plan_dates_invalid_reversed(self):
        """Test that reversed dates fail validation."""
        plan = Plan(
            name="Test Plan",
            start_date=date.today(),
            end_date=date.today() - timedelta(days=7)
        )

        with pytest.raises(ValueError, match="must be after"):
            plan.validate_dates()

    def test_plan_duration_days(self):
        """Test plan duration calculation."""
        plan = Plan(
            name="Test Plan",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 8)
        )

        assert plan.duration_days == 7


class TestWorkoutValidation:
    """Test Workout model validation methods."""

    def test_validate_workout_pace_valid(self):
        """Test that valid pace range passes validation."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=600,
            target_pace_max_sec=660
        )

        # Should not raise exception
        workout.validate_pace()

    def test_validate_workout_pace_invalid(self):
        """Test that invalid pace range fails validation."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=660,
            target_pace_max_sec=600  # min > max is invalid
        )

        with pytest.raises(ValueError, match="must be <="):
            workout.validate_pace()

    def test_validate_workout_pace_both_none(self):
        """Test that both None is valid (no target pace)."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=None,
            target_pace_max_sec=None
        )

        # Should not raise exception
        workout.validate_pace()

    def test_validate_workout_pace_only_one_set(self):
        """Test that only one pace value fails validation."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=600,
            target_pace_max_sec=None
        )

        with pytest.raises(ValueError, match="Both .* must be set"):
            workout.validate_pace()

    def test_validate_workout_distance_valid(self):
        """Test that positive distance passes validation."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=5.0
        )

        # Should not raise exception
        workout.validate_distance()

    def test_validate_workout_distance_invalid(self):
        """Test that zero or negative distance fails validation."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=0.0
        )

        with pytest.raises(ValueError, match="must be positive"):
            workout.validate_distance()

        workout.planned_distance = -1.0
        with pytest.raises(ValueError, match="must be positive"):
            workout.validate_distance()

    def test_workout_pace_range_str(self):
        """Test pace range string formatting."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=600,  # 10:00
            target_pace_max_sec=660   # 11:00
        )

        assert workout.pace_range_str == "10:00-11:00/mile"

    def test_workout_pace_range_str_with_seconds(self):
        """Test pace range string formatting with seconds."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=625,  # 10:25
            target_pace_max_sec=685   # 11:25
        )

        assert workout.pace_range_str == "10:25-11:25/mile"

    def test_workout_pace_range_str_none(self):
        """Test pace range string when no target pace."""
        workout = Workout(
            name="Test Workout",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=None,
            target_pace_max_sec=None
        )

        assert workout.pace_range_str is None


class TestRunValidation:
    """Test Run model validation and helper methods."""

    def test_run_pace_str_formatting(self):
        """Test run pace string formatting."""
        run = Run(
            distance_miles=5.0,
            pace_sec_per_mile=600  # 10:00/mile
        )

        assert run.pace_str == "10:00/mile"

    def test_run_pace_str_formatting_with_seconds(self):
        """Test run pace string formatting with seconds."""
        run = Run(
            distance_miles=5.0,
            pace_sec_per_mile=625  # 10:25/mile
        )

        assert run.pace_str == "10:25/mile"

    def test_run_total_time_minutes(self):
        """Test total time calculation."""
        run = Run(
            distance_miles=5.0,
            pace_sec_per_mile=600  # 10:00/mile
        )

        # 5 miles * 10 minutes = 50 minutes
        assert run.total_time_minutes == 50.0

    def test_run_is_within_target_no_target(self):
        """Test run pace validation when workout has no target."""
        run = Run(
            distance_miles=5.0,
            pace_sec_per_mile=600
        )

        workout = Workout(
            name="Test",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=None,
            target_pace_max_sec=None
        )

        # Any pace is acceptable when no target
        assert run.is_within_target(workout) is True

    def test_run_is_within_target_within_range(self):
        """Test run pace validation when within target range."""
        run = Run(
            distance_miles=5.0,
            pace_sec_per_mile=630  # 10:30/mile
        )

        workout = Workout(
            name="Test",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=600,  # 10:00/mile
            target_pace_max_sec=660   # 11:00/mile
        )

        assert run.is_within_target(workout) is True

    def test_run_is_within_target_outside_range(self):
        """Test run pace validation when outside target range."""
        run = Run(
            distance_miles=5.0,
            pace_sec_per_mile=500  # Too fast
        )

        workout = Workout(
            name="Test",
            workout_type="EASY",
            planned_distance=5.0,
            target_pace_min_sec=600,  # 10:00/mile
            target_pace_max_sec=660   # 11:00/mile
        )

        assert run.is_within_target(workout) is False

    def test_run_is_within_distance_within_tolerance(self):
        """Test run distance validation within tolerance."""
        run = Run(
            distance_miles=9.5,
            pace_sec_per_mile=600
        )

        workout = Workout(
            name="Test",
            workout_type="LONG",
            planned_distance=10.0
        )

        # 9.5 is within 10% of 10.0
        assert run.is_within_distance(workout) is True

    def test_run_is_within_distance_outside_tolerance(self):
        """Test run distance validation outside tolerance."""
        run = Run(
            distance_miles=8.5,
            pace_sec_per_mile=600
        )

        workout = Workout(
            name="Test",
            workout_type="LONG",
            planned_distance=10.0
        )

        # 8.5 is outside 10% of 10.0
        assert run.is_within_distance(workout) is False

    def test_run_matches_workout(self):
        """Test complete run/workout matching."""
        run = Run(
            distance_miles=9.8,
            pace_sec_per_mile=620
        )

        workout = Workout(
            name="Test",
            workout_type="LONG",
            planned_distance=10.0,
            target_pace_min_sec=600,
            target_pace_max_sec=660
        )

        # Both distance and pace match
        assert run.matches_workout(workout) is True
