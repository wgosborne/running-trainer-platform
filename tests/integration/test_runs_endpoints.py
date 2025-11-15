"""
Integration tests for Run API endpoints.

Tests the full request/response cycle for run operations.
"""

import pytest
from datetime import datetime, timedelta, date, timezone
from uuid import uuid4

from app.constants import RunSource

from tests.fixtures import (
    create_test_plan,
    create_test_workout,
    create_test_run,
    create_runs_for_plan
)


class TestRunsEndpoints:
    """Integration tests for Run endpoints."""

    def test_create_run_success(self, client, db_session):
        """Test POST /api/v1/plans/{plan_id}/runs with valid data."""
        plan = create_test_plan(db_session)

        run_data = {
            "distance_miles": 5.0,
            "pace_sec_per_mile": 600,  # 10:00/mile
            "date": datetime.now(timezone.utc).isoformat(),
            "source": RunSource.MANUAL.value
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/runs",
            json=run_data
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["distance_miles"] == 5.0
        assert data["pace_sec_per_mile"] == 600
        assert data["source"] == RunSource.MANUAL.value

    def test_create_run_invalid_distance(self, client, db_session):
        """Test POST with distance too high."""
        plan = create_test_plan(db_session)

        run_data = {
            "distance_miles": 150.0,  # Way too high
            "pace_sec_per_mile": 600,
            "date": datetime.now(timezone.utc).isoformat(),
            "source": RunSource.MANUAL.value
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/runs",
            json=run_data
        )

        assert response.status_code == 422  # Pydantic validation returns 422

    def test_create_run_invalid_pace(self, client, db_session):
        """Test POST with pace too fast."""
        plan = create_test_plan(db_session)

        run_data = {
            "distance_miles": 5.0,
            "pace_sec_per_mile": 100,  # Impossibly fast
            "date": datetime.now(timezone.utc).isoformat(),
            "source": RunSource.MANUAL.value
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/runs",
            json=run_data
        )

        assert response.status_code == 422  # Pydantic validation returns 422

    def test_create_run_with_workout_link(self, client, db_session):
        """Test POST with workout_id linking run to workout."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(db_session, plan.id)

        run_data = {
            "distance_miles": 5.0,
            "pace_sec_per_mile": 600,
            "date": datetime.now(timezone.utc).isoformat(),
            "source": RunSource.MANUAL.value,
            "workout_id": str(workout.id)
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/runs",
            json=run_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["workout_id"] == str(workout.id)

    def test_create_run_with_invalid_workout(self, client, db_session):
        """Test POST with non-existent workout_id."""
        plan = create_test_plan(db_session)
        fake_workout_id = uuid4()

        run_data = {
            "distance_miles": 5.0,
            "pace_sec_per_mile": 600,
            "date": datetime.now(timezone.utc).isoformat(),
            "source": RunSource.MANUAL.value,
            "workout_id": str(fake_workout_id)
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/runs",
            json=run_data
        )

        assert response.status_code in [400, 404]

    def test_create_run_outside_plan_dates(self, client, db_session):
        """Test POST with date outside plan range (should be allowed)."""
        plan = create_test_plan(
            db_session,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 28)
        )

        # Run date before plan starts (logged but allowed)
        run_data = {
            "distance_miles": 5.0,
            "pace_sec_per_mile": 600,
            "date": datetime(2023, 12, 25).isoformat(),
            "source": RunSource.MANUAL.value
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/runs",
            json=run_data
        )

        # Should still be created (just logged as outside range)
        assert response.status_code == 201

    def test_list_runs_for_plan(self, client, db_session):
        """Test GET /api/v1/plans/{plan_id}/runs."""
        plan = create_test_plan(db_session)
        create_runs_for_plan(db_session, plan.id, count=3)

        response = client.get(f"/api/v1/plans/{plan.id}/runs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_all_runs(self, client, db_session):
        """Test GET /api/v1/runs (all runs across plans)."""
        plan1 = create_test_plan(db_session, name="Plan 1")
        plan2 = create_test_plan(db_session, name="Plan 2")

        create_runs_for_plan(db_session, plan1.id, count=2)
        create_runs_for_plan(db_session, plan2.id, count=2)

        response = client.get("/api/v1/runs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_get_run_success(self, client, db_session):
        """Test GET /api/v1/runs/{run_id}."""
        plan = create_test_plan(db_session)
        run = create_test_run(db_session, plan.id)

        response = client.get(f"/api/v1/runs/{run.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(run.id)
        assert data["distance_miles"] == run.distance_miles

    def test_get_run_not_found(self, client):
        """Test GET /api/v1/runs/{run_id} with invalid ID."""
        fake_id = uuid4()

        response = client.get(f"/api/v1/runs/{fake_id}")

        assert response.status_code == 404

    def test_update_run_success(self, client, db_session):
        """Test PATCH /api/v1/runs/{run_id}."""
        plan = create_test_plan(db_session)
        run = create_test_run(db_session, plan.id, distance_miles=5.0)

        update_data = {"distance_miles": 6.0}
        response = client.patch(f"/api/v1/runs/{run.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["distance_miles"] == 6.0

    def test_update_run_not_found(self, client):
        """Test PATCH with non-existent run ID."""
        fake_id = uuid4()

        update_data = {"distance_miles": 6.0}
        response = client.patch(f"/api/v1/runs/{fake_id}", json=update_data)

        assert response.status_code == 404

    def test_delete_run_success(self, client, db_session):
        """Test DELETE /api/v1/runs/{run_id}."""
        plan = create_test_plan(db_session)
        run = create_test_run(db_session, plan.id)

        response = client.delete(f"/api/v1/runs/{run.id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/runs/{run.id}")
        assert get_response.status_code == 404

    def test_delete_run_not_found(self, client):
        """Test DELETE with non-existent run ID."""
        fake_id = uuid4()

        response = client.delete(f"/api/v1/runs/{fake_id}")

        assert response.status_code == 404

    def test_create_run_missing_fields(self, client, db_session):
        """Test POST without required fields."""
        plan = create_test_plan(db_session)

        run_data = {"distance_miles": 5.0}  # Missing required fields

        response = client.post(
            f"/api/v1/plans/{plan.id}/runs",
            json=run_data
        )

        assert response.status_code == 422

    def test_create_run_invalid_plan(self, client):
        """Test POST with non-existent plan ID."""
        fake_id = uuid4()

        run_data = {
            "distance_miles": 5.0,
            "pace_sec_per_mile": 600,
            "date": datetime.now(timezone.utc).isoformat(),
            "source": RunSource.MANUAL.value
        }

        response = client.post(
            f"/api/v1/plans/{fake_id}/runs",
            json=run_data
        )

        assert response.status_code == 404
