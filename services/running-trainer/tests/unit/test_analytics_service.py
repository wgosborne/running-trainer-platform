"""
Unit tests for AnalyticsService.

Tests the analytics and reporting logic.
"""

import pytest
from datetime import datetime, timedelta

from app.services.analytics_service import AnalyticsService

from tests.fixtures import (
    create_test_plan,
    create_test_workout,
    create_test_run,
    create_workouts_for_plan,
    create_runs_for_plan
)


class TestAnalyticsService:
    """Test AnalyticsService business logic."""

    @pytest.fixture
    def analytics_service(self):
        """Create an AnalyticsService instance for testing."""
        return AnalyticsService()

    def test_plan_progress_no_runs(self, db_session, analytics_service):
        """Test plan progress calculation with no runs."""
        plan = create_test_plan(db_session)
        workouts = create_workouts_for_plan(db_session, plan.id, count=3)

        progress = analytics_service.get_plan_progress(db_session, plan.id)

        assert progress["total_workouts"] == 3
        assert progress["completed_workouts"] == 0
        assert progress["adherence_percentage"] == 0.0

    def test_plan_progress_some_runs(self, db_session, analytics_service):
        """Test plan progress calculation with some runs."""
        plan = create_test_plan(db_session)
        workouts = create_workouts_for_plan(db_session, plan.id, count=3)

        # Create runs linked to 2 workouts
        create_test_run(db_session, plan.id, workout_id=workouts[0].id)
        create_test_run(db_session, plan.id, workout_id=workouts[1].id)

        progress = analytics_service.get_plan_progress(db_session, plan.id)

        assert progress["total_workouts"] == 3
        assert progress["completed_workouts"] == 2
        assert progress["adherence_percentage"] == pytest.approx(66.67, rel=0.1)

    def test_plan_progress_all_runs(self, db_session, analytics_service):
        """Test plan progress calculation with all runs completed."""
        plan = create_test_plan(db_session)
        workouts = create_workouts_for_plan(db_session, plan.id, count=3)

        # Create runs for all workouts
        for workout in workouts:
            create_test_run(db_session, plan.id, workout_id=workout.id)

        progress = analytics_service.get_plan_progress(db_session, plan.id)

        assert progress["total_workouts"] == 3
        assert progress["completed_workouts"] == 3
        assert progress["adherence_percentage"] == 100.0

    def test_weekly_summary(self, db_session, analytics_service):
        """Test weekly summary calculation."""
        plan = create_test_plan(db_session)

        # Create runs with dates in the first week
        for i in range(3):
            create_test_run(
                db_session,
                plan.id,
                distance_miles=5.0,
                date=plan.start_date + timedelta(days=i)
            )

        summary = analytics_service.get_weekly_summary(
            db_session,
            plan.id,
            week_number=1
        )

        assert summary["week_number"] == 1
        # Should have runs in this week
        assert summary["total_distance"] > 0

    def test_weekly_summary_mileage(self, db_session, analytics_service):
        """Test weekly summary mileage calculation."""
        plan = create_test_plan(db_session)

        # Create runs totaling 30 miles in week 1
        distances = [10.0, 8.0, 12.0]
        for i, distance in enumerate(distances):
            create_test_run(
                db_session,
                plan.id,
                distance_miles=distance,
                date=plan.start_date + timedelta(days=i)
            )

        summary = analytics_service.get_weekly_summary(
            db_session,
            plan.id,
            week_number=1
        )

        assert summary["total_distance"] == 30.0

    def test_plan_progress_invalid_plan(self, db_session, analytics_service):
        """Test that progress for non-existent plan raises error."""
        from uuid import uuid4
        from app.exceptions import NotFoundError

        fake_id = uuid4()

        with pytest.raises(NotFoundError):
            analytics_service.get_plan_progress(db_session, fake_id)
