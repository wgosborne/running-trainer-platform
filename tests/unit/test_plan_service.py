"""
Unit tests for PlanService.

Tests the business logic in the Plan service layer, including
validation and error handling.
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.services.plan_service import PlanService
from app.schemas.plan import PlanCreate, PlanUpdate
from app.exceptions import ValidationError, NotFoundError
from app.constants import PlanStatus

from tests.fixtures import create_test_plan


class TestPlanService:
    """Test PlanService business logic."""

    @pytest.fixture
    def plan_service(self):
        """Create a PlanService instance for testing."""
        return PlanService()

    def test_validate_plan_dates_valid(self, plan_service):
        """Test that valid dates pass validation."""
        start_date = date.today()
        end_date = date.today() + timedelta(days=7)

        # Should not raise exception
        assert plan_service.validate_plan_dates(start_date, end_date) is True

    def test_validate_plan_dates_invalid_same_date(self, plan_service):
        """Test that same start and end dates fail validation."""
        same_date = date.today()

        with pytest.raises(ValidationError, match="must be after"):
            plan_service.validate_plan_dates(same_date, same_date)

    def test_validate_plan_dates_invalid_reversed(self, plan_service):
        """Test that reversed dates fail validation."""
        start_date = date.today()
        end_date = date.today() - timedelta(days=7)

        with pytest.raises(ValidationError, match="must be after"):
            plan_service.validate_plan_dates(start_date, end_date)

    def test_create_plan_success(self, db_session, plan_service):
        """Test creating a plan with valid data."""
        plan_data = PlanCreate(
            name="Marathon Training",
            description="12-week marathon plan",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=84)
        )

        plan = plan_service.create_plan(db_session, plan_data)

        assert plan.id is not None
        assert plan.name == "Marathon Training"
        assert plan.status == PlanStatus.DRAFT.value
        assert plan.created_at is not None

    def test_create_plan_invalid_dates(self, db_session, plan_service):
        """Test that creating plan with invalid dates fails."""
        plan_data = PlanCreate(
            name="Invalid Plan",
            start_date=date.today(),
            end_date=date.today() - timedelta(days=7)  # Invalid: before start
        )

        with pytest.raises(ValidationError):
            plan_service.create_plan(db_session, plan_data)

    def test_create_plan_same_dates(self, db_session, plan_service):
        """Test that creating plan with same start/end dates fails."""
        same_date = date.today()
        plan_data = PlanCreate(
            name="Same Date Plan",
            start_date=same_date,
            end_date=same_date
        )

        with pytest.raises(ValidationError):
            plan_service.create_plan(db_session, plan_data)

    def test_get_plan_success(self, db_session, plan_service):
        """Test retrieving an existing plan."""
        # Create test plan
        created_plan = create_test_plan(db_session)

        # Retrieve it
        retrieved_plan = plan_service.get_plan(db_session, created_plan.id)

        assert retrieved_plan.id == created_plan.id
        assert retrieved_plan.name == created_plan.name

    def test_get_plan_not_found(self, db_session, plan_service):
        """Test that retrieving non-existent plan raises NotFoundError."""
        fake_id = uuid4()

        with pytest.raises(NotFoundError, match="Plan"):
            plan_service.get_plan(db_session, fake_id)

    def test_get_all_plans_empty(self, db_session, plan_service):
        """Test retrieving plans when none exist."""
        plans = plan_service.get_all_plans(db_session)

        assert plans == []

    def test_get_all_plans_multiple(self, db_session, plan_service):
        """Test retrieving multiple plans."""
        # Create 3 test plans
        for i in range(3):
            create_test_plan(
                db_session,
                name=f"Plan {i + 1}"
            )

        plans = plan_service.get_all_plans(db_session)

        assert len(plans) == 3

    def test_get_all_plans_pagination(self, db_session, plan_service):
        """Test pagination of plan retrieval."""
        # Create 10 plans
        for i in range(10):
            create_test_plan(
                db_session,
                name=f"Plan {i + 1}"
            )

        # Get first 5
        first_page = plan_service.get_all_plans(db_session, skip=0, limit=5)
        assert len(first_page) == 5

        # Get next 5
        second_page = plan_service.get_all_plans(db_session, skip=5, limit=5)
        assert len(second_page) == 5

        # Ensure they're different
        first_ids = {p.id for p in first_page}
        second_ids = {p.id for p in second_page}
        assert first_ids.isdisjoint(second_ids)

    def test_update_plan_success(self, db_session, plan_service):
        """Test updating an existing plan."""
        # Create test plan
        plan = create_test_plan(db_session, name="Original Name")
        original_updated_at = plan.updated_at

        # Update it
        update_data = PlanUpdate(name="Updated Name")
        updated_plan = plan_service.update_plan(db_session, plan.id, update_data)

        assert updated_plan.id == plan.id
        assert updated_plan.name == "Updated Name"
        assert updated_plan.updated_at >= original_updated_at

    def test_update_plan_status(self, db_session, plan_service):
        """Test updating plan status."""
        # Create test plan
        plan = create_test_plan(db_session)
        assert plan.status == PlanStatus.DRAFT.value

        # Update status to ACTIVE
        update_data = PlanUpdate(status=PlanStatus.ACTIVE)
        updated_plan = plan_service.update_plan(db_session, plan.id, update_data)

        assert updated_plan.status == PlanStatus.ACTIVE.value

    def test_update_plan_not_found(self, db_session, plan_service):
        """Test that updating non-existent plan raises NotFoundError."""
        fake_id = uuid4()
        update_data = PlanUpdate(name="Updated Name")

        with pytest.raises(NotFoundError, match="Plan"):
            plan_service.update_plan(db_session, fake_id, update_data)

    def test_delete_plan_success(self, db_session, plan_service):
        """Test deleting an existing plan."""
        # Create test plan
        plan = create_test_plan(db_session)

        # Delete it
        result = plan_service.delete_plan(db_session, plan.id)

        assert result is True

        # Verify it's gone
        with pytest.raises(NotFoundError):
            plan_service.get_plan(db_session, plan.id)

    def test_delete_plan_not_found(self, db_session, plan_service):
        """Test that deleting non-existent plan raises NotFoundError."""
        fake_id = uuid4()

        with pytest.raises(NotFoundError, match="Plan"):
            plan_service.delete_plan(db_session, fake_id)


class TestPlanModel:
    """Test Plan model methods and properties."""

    def test_plan_duration_days(self, db_session):
        """Test plan duration calculation."""
        plan = create_test_plan(
            db_session,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 27)  # 57 days later
        )

        assert plan.duration_days == 57

    def test_plan_is_active(self, db_session):
        """Test is_active() method."""
        # Create ACTIVE plan
        active_plan = create_test_plan(
            db_session,
            status=PlanStatus.ACTIVE.value
        )
        assert active_plan.is_active() is True

        # Create DRAFT plan
        draft_plan = create_test_plan(
            db_session,
            status=PlanStatus.DRAFT.value
        )
        assert draft_plan.is_active() is False

    def test_plan_is_draft(self, db_session):
        """Test is_draft() method."""
        draft_plan = create_test_plan(
            db_session,
            status=PlanStatus.DRAFT.value
        )
        assert draft_plan.is_draft() is True

        active_plan = create_test_plan(
            db_session,
            status=PlanStatus.ACTIVE.value
        )
        assert active_plan.is_draft() is False

    def test_plan_is_completed(self, db_session):
        """Test is_completed() method."""
        completed_plan = create_test_plan(
            db_session,
            status=PlanStatus.COMPLETED.value
        )
        assert completed_plan.is_completed() is True

        active_plan = create_test_plan(
            db_session,
            status=PlanStatus.ACTIVE.value
        )
        assert active_plan.is_completed() is False

    def test_plan_is_abandoned(self, db_session):
        """Test is_abandoned() method."""
        abandoned_plan = create_test_plan(
            db_session,
            status=PlanStatus.ABANDONED.value
        )
        assert abandoned_plan.is_abandoned() is True

        active_plan = create_test_plan(
            db_session,
            status=PlanStatus.ACTIVE.value
        )
        assert active_plan.is_abandoned() is False
