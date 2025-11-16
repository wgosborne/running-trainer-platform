"""
Integration tests for Workout API endpoints.

Tests the full request/response cycle for workout operations.
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.constants import WorkoutType

from tests.fixtures import (
    create_test_plan,
    create_test_workout,
    create_workouts_for_plan
)


class TestWorkoutsEndpoints:
    """Integration tests for /api/v1/plans/{plan_id}/workouts endpoints."""

    def test_create_workout_success(self, client, db_session):
        """Test POST /api/v1/plans/{plan_id}/workouts with valid data."""
        plan = create_test_plan(db_session)

        workout_data = {
            "name": "Easy run",
            "workout_type": WorkoutType.EASY.value,
            "planned_distance": 5.0,
            "target_pace_min_sec": 600,
            "target_pace_max_sec": 660,
            "scheduled_date": str(date.today())
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/workouts",
            json=workout_data
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Easy run"
        assert data["workout_type"] == WorkoutType.EASY.value
        assert data["planned_distance"] == 5.0

    def test_create_workout_missing_fields(self, client, db_session):
        """Test POST /api/v1/plans/{plan_id}/workouts without required fields."""
        plan = create_test_plan(db_session)

        workout_data = {"name": "Incomplete workout"}

        response = client.post(
            f"/api/v1/plans/{plan.id}/workouts",
            json=workout_data
        )

        assert response.status_code == 422

    def test_create_workout_invalid_plan_id(self, client):
        """Test POST /api/v1/plans/{plan_id}/workouts with invalid plan ID."""
        fake_id = uuid4()

        workout_data = {
            "name": "Easy run",
            "workout_type": WorkoutType.EASY.value,
            "planned_distance": 5.0
        }

        response = client.post(
            f"/api/v1/plans/{fake_id}/workouts",
            json=workout_data
        )

        assert response.status_code == 404

    def test_create_workout_invalid_pace(self, client, db_session):
        """Test POST with min_pace > max_pace."""
        plan = create_test_plan(db_session)

        workout_data = {
            "name": "Invalid workout",
            "workout_type": WorkoutType.EASY.value,
            "planned_distance": 5.0,
            "target_pace_min_sec": 660,  # Slower (invalid as min)
            "target_pace_max_sec": 600   # Faster (invalid as max)
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/workouts",
            json=workout_data
        )

        assert response.status_code == 422  # Pydantic validation returns 422

    def test_list_workouts_for_plan(self, client, db_session):
        """Test GET /api/v1/plans/{plan_id}/workouts."""
        plan = create_test_plan(db_session)
        create_workouts_for_plan(db_session, plan.id, count=3)

        response = client.get(f"/api/v1/plans/{plan.id}/workouts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_workouts_invalid_plan(self, client):
        """Test GET /api/v1/plans/{plan_id}/workouts with invalid plan ID."""
        fake_id = uuid4()

        response = client.get(f"/api/v1/plans/{fake_id}/workouts")

        assert response.status_code == 404

    def test_get_workout_success(self, client, db_session):
        """Test GET /api/v1/plans/{plan_id}/workouts/{workout_id}."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(db_session, plan.id)

        response = client.get(
            f"/api/v1/plans/{plan.id}/workouts/{workout.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(workout.id)
        assert data["name"] == workout.name

    def test_get_workout_not_found(self, client, db_session):
        """Test GET with non-existent workout ID."""
        plan = create_test_plan(db_session)
        fake_id = uuid4()

        response = client.get(
            f"/api/v1/plans/{plan.id}/workouts/{fake_id}"
        )

        assert response.status_code == 404

    def test_update_workout_success(self, client, db_session):
        """Test PATCH /api/v1/plans/{plan_id}/workouts/{workout_id}."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(db_session, plan.id, planned_distance=5.0)

        update_data = {"planned_distance": 6.0}
        response = client.patch(
            f"/api/v1/plans/{plan.id}/workouts/{workout.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["planned_distance"] == 6.0

    def test_update_workout_not_found(self, client, db_session):
        """Test PATCH with non-existent workout ID."""
        plan = create_test_plan(db_session)
        fake_id = uuid4()

        update_data = {"planned_distance": 6.0}
        response = client.patch(
            f"/api/v1/plans/{plan.id}/workouts/{fake_id}",
            json=update_data
        )

        assert response.status_code == 404

    def test_delete_workout_success(self, client, db_session):
        """Test DELETE /api/v1/plans/{plan_id}/workouts/{workout_id}."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(db_session, plan.id)

        response = client.delete(
            f"/api/v1/plans/{plan.id}/workouts/{workout.id}"
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/plans/{plan.id}/workouts/{workout.id}"
        )
        assert get_response.status_code == 404

    def test_delete_workout_not_found(self, client, db_session):
        """Test DELETE with non-existent workout ID."""
        plan = create_test_plan(db_session)
        fake_id = uuid4()

        response = client.delete(
            f"/api/v1/plans/{plan.id}/workouts/{fake_id}"
        )

        assert response.status_code == 404

    def test_create_workout_all_types(self, client, db_session):
        """Test creating workouts of all valid types."""
        plan = create_test_plan(db_session)

        workout_types = [
            WorkoutType.EASY,
            WorkoutType.TEMPO,
            WorkoutType.LONG,
            WorkoutType.SPEED,
            WorkoutType.RECOVERY,
            WorkoutType.CROSS_TRAINING,
            WorkoutType.REST
        ]

        for workout_type in workout_types:
            workout_data = {
                "name": f"{workout_type.value} workout",
                "workout_type": workout_type.value,
                "planned_distance": 5.0
            }

            response = client.post(
                f"/api/v1/plans/{plan.id}/workouts",
                json=workout_data
            )

            assert response.status_code == 201
            data = response.json()
            assert data["workout_type"] == workout_type.value

    def test_create_workout_impossible_pace_range(self, client, db_session):
        """Test POST with impossibly fast pace (below minimum allowed)."""
        plan = create_test_plan(db_session)

        workout_data = {
            "name": "Impossible pace workout",
            "workout_type": WorkoutType.SPEED.value,
            "planned_distance": 5.0,
            "target_pace_min_sec": 100,  # Too fast (below 180 sec/km minimum)
            "target_pace_max_sec": 150   # Also too fast
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/workouts",
            json=workout_data
        )

        # Should fail validation
        assert response.status_code == 422

    def test_create_workout_impossibly_slow_pace(self, client, db_session):
        """Test POST with impossibly slow pace (above maximum allowed)."""
        plan = create_test_plan(db_session)

        workout_data = {
            "name": "Too slow workout",
            "workout_type": WorkoutType.EASY.value,
            "planned_distance": 5.0,
            "target_pace_min_sec": 3500,  # Too slow (above 3000 sec/km maximum)
            "target_pace_max_sec": 4000   # Way too slow
        }

        response = client.post(
            f"/api/v1/plans/{plan.id}/workouts",
            json=workout_data
        )

        # Should fail validation
        assert response.status_code == 422
