"""
Test fixtures for Plan model.

Provides factory functions for creating test plan instances with
various configurations for use in unit and integration tests.
"""

from datetime import date, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.constants import PlanStatus


def create_test_plan(db_session: Session, **kwargs) -> Plan:
    """
    Create a test plan with default values.

    Args:
        db_session: Database session
        **kwargs: Override default values

    Returns:
        Created Plan instance

    Example:
        >>> plan = create_test_plan(db_session, name="Custom Plan")
    """
    defaults = {
        "name": "Test Marathon Plan",
        "description": "Test plan for marathon training",
        "start_date": date.today(),
        "end_date": date.today() + timedelta(days=56),  # 8 weeks
        "status": PlanStatus.DRAFT.value
    }

    # Merge defaults with provided kwargs
    plan_data = {**defaults, **kwargs}

    # Create plan
    plan = Plan(**plan_data)

    # Add to database
    db_session.add(plan)
    db_session.flush()  # Use flush instead of commit to maintain transaction isolation
    db_session.refresh(plan)

    return plan


def create_active_plan(db_session: Session) -> Plan:
    """
    Create a test plan with ACTIVE status.

    Args:
        db_session: Database session

    Returns:
        Created Plan instance with ACTIVE status
    """
    return create_test_plan(
        db_session,
        name="Active Training Plan",
        status=PlanStatus.ACTIVE.value,
        start_date=date.today() - timedelta(days=7),
        end_date=date.today() + timedelta(days=49)  # 7 weeks remaining
    )


def create_completed_plan(db_session: Session) -> Plan:
    """
    Create a test plan with COMPLETED status.

    Args:
        db_session: Database session

    Returns:
        Created Plan instance with COMPLETED status
    """
    return create_test_plan(
        db_session,
        name="Completed Training Plan",
        status=PlanStatus.COMPLETED.value,
        start_date=date.today() - timedelta(days=56),
        end_date=date.today() - timedelta(days=1)  # Ended yesterday
    )


def create_abandoned_plan(db_session: Session) -> Plan:
    """
    Create a test plan with ABANDONED status.

    Args:
        db_session: Database session

    Returns:
        Created Plan instance with ABANDONED status
    """
    return create_test_plan(
        db_session,
        name="Abandoned Training Plan",
        status=PlanStatus.ABANDONED.value,
        start_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=26)  # Would have ended in future
    )


def create_plans_multiple(db_session: Session, count: int = 3) -> List[Plan]:
    """
    Create multiple test plans with different dates.

    Args:
        db_session: Database session
        count: Number of plans to create

    Returns:
        List of created Plan instances

    Example:
        >>> plans = create_plans_multiple(db_session, count=5)
        >>> len(plans)
        5
    """
    plans = []

    for i in range(count):
        plan = create_test_plan(
            db_session,
            name=f"Test Plan {i + 1}",
            description=f"Test plan number {i + 1}",
            start_date=date.today() + timedelta(days=i * 7),
            end_date=date.today() + timedelta(days=(i + 1) * 7 + 49)
        )
        plans.append(plan)

    return plans
