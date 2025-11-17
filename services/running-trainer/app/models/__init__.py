"""
Database models package.

This package contains all SQLAlchemy ORM models for the Running Training Tracker.

Models:
    - Plan: Training plan with start/end dates and status
    - Workout: Planned training activity within a plan
    - Run: Actual completed training activity

All models inherit from Base (declarative base) and BaseMixin (common fields).

Usage:
    >>> from app.models import Plan, Workout, Run, Base
    >>> from app.db.database import engine
    >>> Base.metadata.create_all(engine)
"""

# Import Base first to avoid circular imports
from app.models.base import Base, BaseMixin

# Import models in dependency order
from app.models.plan import Plan
from app.models.workout import Workout
from app.models.run import Run

# Export all models and Base
__all__ = [
    "Base",
    "BaseMixin",
    "Plan",
    "Workout",
    "Run",
]
