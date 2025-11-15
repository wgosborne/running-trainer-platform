"""
Integration tests for Plan API endpoints.

Tests the full request/response cycle for plan operations including
HTTP status codes, response data, and database state.
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.constants import PlanStatus

from tests.fixtures import (
    create_test_plan,
    create_plans_multiple,
    create_test_workout
)


class TestPlansEndpoints:
    """Integration tests for /api/v1/plans endpoints."""

    def test_create_plan_success(self, client, db_session):
        """Test POST /api/v1/plans with valid data."""
        plan_data = {
            "name": "Marathon Training",
            "description": "12-week marathon plan",
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=84))
        }

        response = client.post("/api/v1/plans", json=plan_data)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Marathon Training"
        assert data["status"] == PlanStatus.DRAFT.value
        assert "created_at" in data

    def test_create_plan_missing_name(self, client):
        """Test POST /api/v1/plans without name."""
        plan_data = {
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=84))
        }

        response = client.post("/api/v1/plans", json=plan_data)

        assert response.status_code == 422

    def test_create_plan_missing_dates(self, client):
        """Test POST /api/v1/plans without dates."""
        plan_data = {"name": "Test Plan"}

        response = client.post("/api/v1/plans", json=plan_data)

        assert response.status_code == 422

    def test_create_plan_invalid_dates(self, client):
        """Test POST /api/v1/plans with start_date > end_date."""
        plan_data = {
            "name": "Invalid Plan",
            "start_date": str(date.today()),
            "end_date": str(date.today() - timedelta(days=7))
        }

        response = client.post("/api/v1/plans", json=plan_data)

        assert response.status_code == 400
        data = response.json()
        assert "must be after" in data["detail"].lower()

    def test_create_plan_same_dates(self, client):
        """Test POST /api/v1/plans with same start/end dates."""
        same_date = str(date.today())
        plan_data = {
            "name": "Same Date Plan",
            "start_date": same_date,
            "end_date": same_date
        }

        response = client.post("/api/v1/plans", json=plan_data)

        assert response.status_code == 400

    def test_list_plans_empty(self, client, db_session):
        """Test GET /api/v1/plans when no plans exist."""
        response = client.get("/api/v1/plans")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_plans_multiple(self, client, db_session):
        """Test GET /api/v1/plans with multiple plans."""
        # Create 3 plans
        create_plans_multiple(db_session, count=3)

        response = client.get("/api/v1/plans")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_plans_pagination(self, client, db_session):
        """Test GET /api/v1/plans with pagination."""
        # Create 10 plans
        create_plans_multiple(db_session, count=10)

        # Get first 5
        response = client.get("/api/v1/plans?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Get next 5
        response = client.get("/api/v1/plans?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_plans_invalid_pagination(self, client):
        """Test GET /api/v1/plans with invalid pagination parameters."""
        # Negative skip
        response = client.get("/api/v1/plans?skip=-1")
        assert response.status_code == 422

        # Zero limit
        response = client.get("/api/v1/plans?limit=0")
        assert response.status_code == 422

    def test_get_plan_success(self, client, db_session):
        """Test GET /api/v1/plans/{id} with valid ID."""
        plan = create_test_plan(db_session)

        response = client.get(f"/api/v1/plans/{plan.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(plan.id)
        assert data["name"] == plan.name

    def test_get_plan_not_found(self, client):
        """Test GET /api/v1/plans/{id} with invalid ID."""
        fake_id = uuid4()

        response = client.get(f"/api/v1/plans/{fake_id}")

        assert response.status_code == 404

    def test_update_plan_success(self, client, db_session):
        """Test PATCH /api/v1/plans/{id} with valid data."""
        plan = create_test_plan(db_session, name="Original Name")

        update_data = {"name": "Updated Name"}
        response = client.patch(f"/api/v1/plans/{plan.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["updated_at"] != data["created_at"]

    def test_update_plan_status(self, client, db_session):
        """Test PATCH /api/v1/plans/{id} to change status."""
        plan = create_test_plan(db_session)

        update_data = {"status": PlanStatus.ACTIVE.value}
        response = client.patch(f"/api/v1/plans/{plan.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == PlanStatus.ACTIVE.value

    def test_update_plan_invalid_status(self, client, db_session):
        """Test PATCH /api/v1/plans/{id} with invalid status."""
        plan = create_test_plan(db_session)

        update_data = {"status": "INVALID_STATUS"}
        response = client.patch(f"/api/v1/plans/{plan.id}", json=update_data)

        assert response.status_code in [400, 422]

    def test_update_plan_dates_invalid(self, client, db_session):
        """Test PATCH /api/v1/plans/{id} with invalid dates."""
        plan = create_test_plan(db_session)

        update_data = {
            "start_date": str(date.today()),
            "end_date": str(date.today() - timedelta(days=7))
        }
        response = client.patch(f"/api/v1/plans/{plan.id}", json=update_data)

        assert response.status_code == 400

    def test_update_plan_not_found(self, client):
        """Test PATCH /api/v1/plans/{id} with non-existent ID."""
        fake_id = uuid4()

        update_data = {"name": "Updated Name"}
        response = client.patch(f"/api/v1/plans/{fake_id}", json=update_data)

        assert response.status_code == 404

    def test_delete_plan_success(self, client, db_session):
        """Test DELETE /api/v1/plans/{id}."""
        plan = create_test_plan(db_session)

        response = client.delete(f"/api/v1/plans/{plan.id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/plans/{plan.id}")
        assert get_response.status_code == 404

    def test_delete_plan_cascade(self, client, db_session):
        """Test DELETE /api/v1/plans/{id} cascades to workouts."""
        plan = create_test_plan(db_session)
        workout = create_test_workout(db_session, plan.id)

        response = client.delete(f"/api/v1/plans/{plan.id}")

        assert response.status_code == 204

        # Verify workout is also deleted
        workout_response = client.get(
            f"/api/v1/plans/{plan.id}/workouts/{workout.id}"
        )
        assert workout_response.status_code == 404

    def test_delete_plan_not_found(self, client):
        """Test DELETE /api/v1/plans/{id} with non-existent ID."""
        fake_id = uuid4()

        response = client.delete(f"/api/v1/plans/{fake_id}")

        assert response.status_code == 404
