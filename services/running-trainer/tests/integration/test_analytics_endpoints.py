"""
Integration tests for Analytics API endpoints.

Tests the analytics and reporting endpoints.
"""

import pytest
from datetime import datetime, timedelta, date
from uuid import uuid4

from tests.fixtures import (
    create_test_plan,
    create_test_workout,
    create_test_run,
    create_workouts_for_plan,
    create_runs_for_plan
)


class TestAnalyticsEndpoints:
    """Integration tests for /api/v1/plans/{plan_id}/... analytics endpoints."""

    def test_plan_progress_no_runs(self, client, db_session):
        """Test GET /api/v1/plans/{plan_id}/progress with no runs."""
        plan = create_test_plan(db_session)
        create_workouts_for_plan(db_session, plan.id, count=3)

        response = client.get(f"/api/v1/plans/{plan.id}/progress")

        assert response.status_code == 200
        data = response.json()
        assert "total_workouts" in data
        assert "completed_workouts" in data
        assert "adherence_percentage" in data
        assert data["total_workouts"] == 3
        assert data["completed_workouts"] == 0
        assert data["adherence_percentage"] == 0.0

    def test_plan_progress_with_runs(self, client, db_session):
        """Test GET /api/v1/plans/{plan_id}/progress with some runs."""
        plan = create_test_plan(db_session)
        workouts = create_workouts_for_plan(db_session, plan.id, count=3)

        # Create runs linked to 2 workouts
        create_test_run(db_session, plan.id, workout_id=workouts[0].id)
        create_test_run(db_session, plan.id, workout_id=workouts[1].id)

        response = client.get(f"/api/v1/plans/{plan.id}/progress")

        assert response.status_code == 200
        data = response.json()
        assert data["total_workouts"] == 3
        assert data["completed_workouts"] == 2
        # Should be approximately 66.67%
        assert 60 < data["adherence_percentage"] < 70

    def test_plan_progress_all_completed(self, client, db_session):
        """Test GET /api/v1/plans/{plan_id}/progress with all runs."""
        plan = create_test_plan(db_session)
        workouts = create_workouts_for_plan(db_session, plan.id, count=3)

        # Create runs for all workouts
        for workout in workouts:
            create_test_run(db_session, plan.id, workout_id=workout.id)

        response = client.get(f"/api/v1/plans/{plan.id}/progress")

        assert response.status_code == 200
        data = response.json()
        assert data["total_workouts"] == 3
        assert data["completed_workouts"] == 3
        assert data["adherence_percentage"] == 100.0

    def test_plan_progress_invalid_plan(self, client):
        """Test GET /api/v1/plans/{plan_id}/progress with invalid plan ID."""
        fake_id = uuid4()

        response = client.get(f"/api/v1/plans/{fake_id}/progress")

        assert response.status_code == 404

    def test_weekly_summary(self, client, db_session):
        """Test GET /api/v1/plans/{plan_id}/weekly-summary."""
        plan = create_test_plan(
            db_session,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=56)
        )

        # Create runs in the first week
        for i in range(3):
            create_test_run(
                db_session,
                plan.id,
                distance_miles=5.0,
                date=plan.start_date + timedelta(days=i)
            )

        response = client.get(
            f"/api/v1/plans/{plan.id}/weekly-summary?week_number=1"
        )

        assert response.status_code == 200
        data = response.json()
        assert "week_number" in data
        assert data["week_number"] == 1
        assert "total_distance" in data
        assert data["total_distance"] > 0

    def test_weekly_summary_mileage_calculation(self, client, db_session):
        """Test weekly summary mileage calculation."""
        plan = create_test_plan(
            db_session,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=56)
        )

        # Create runs totaling 30 miles in week 1
        distances = [10.0, 8.0, 12.0]
        for i, distance in enumerate(distances):
            create_test_run(
                db_session,
                plan.id,
                distance_miles=distance,
                date=plan.start_date + timedelta(days=i)
            )

        response = client.get(
            f"/api/v1/plans/{plan.id}/weekly-summary?week_number=1"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_distance"] == 30.0

    def test_weekly_summary_invalid_plan(self, client):
        """Test GET weekly-summary with invalid plan ID."""
        fake_id = uuid4()

        response = client.get(
            f"/api/v1/plans/{fake_id}/weekly-summary?week_number=1"
        )

        assert response.status_code == 404

    def test_weekly_summary_invalid_week(self, client, db_session):
        """Test GET weekly-summary with invalid week number."""
        plan = create_test_plan(db_session)

        # Week number way beyond plan duration
        response = client.get(
            f"/api/v1/plans/{plan.id}/weekly-summary?week_number=100"
        )

        assert response.status_code == 400

    def test_weekly_summary_no_week_param(self, client, db_session):
        """Test GET weekly-summary without week_number parameter."""
        plan = create_test_plan(db_session)

        response = client.get(f"/api/v1/plans/{plan.id}/weekly-summary")

        # Should either default to week 1 or require the parameter
        assert response.status_code in [200, 400, 422]

    def test_plan_progress_with_unlinked_runs(self, client, db_session):
        """Test progress calculation ignores unlinked runs."""
        plan = create_test_plan(db_session)
        workouts = create_workouts_for_plan(db_session, plan.id, count=3)

        # Create runs NOT linked to workouts
        create_test_run(db_session, plan.id, workout_id=None)
        create_test_run(db_session, plan.id, workout_id=None)

        response = client.get(f"/api/v1/plans/{plan.id}/progress")

        assert response.status_code == 200
        data = response.json()
        # Unlinked runs shouldn't count as completed workouts
        assert data["completed_workouts"] == 0

    def test_weekly_summary_empty_week(self, client, db_session):
        """Test weekly summary for a week with no runs."""
        plan = create_test_plan(
            db_session,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=56)
        )

        # Don't create any runs

        response = client.get(
            f"/api/v1/plans/{plan.id}/weekly-summary?week_number=1"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_distance"] == 0.0

    def test_weekly_summary_multiple_weeks(self, client, db_session):
        """Test weekly summaries for multiple weeks."""
        plan = create_test_plan(
            db_session,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=56)
        )

        # Create runs in week 1
        create_test_run(
            db_session,
            plan.id,
            distance_miles=10.0,
            date=plan.start_date + timedelta(days=1)
        )

        # Create runs in week 2
        create_test_run(
            db_session,
            plan.id,
            distance_miles=15.0,
            date=plan.start_date + timedelta(days=8)
        )

        # Check week 1
        response_week1 = client.get(
            f"/api/v1/plans/{plan.id}/weekly-summary?week_number=1"
        )
        assert response_week1.status_code == 200
        data_week1 = response_week1.json()
        assert data_week1["total_distance"] == 10.0

        # Check week 2
        response_week2 = client.get(
            f"/api/v1/plans/{plan.id}/weekly-summary?week_number=2"
        )
        assert response_week2.status_code == 200
        data_week2 = response_week2.json()
        assert data_week2["total_distance"] == 15.0
