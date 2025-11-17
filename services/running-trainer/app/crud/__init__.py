"""
CRUD operations for database models.

This package contains classes that handle Create, Read, Update, Delete
operations for each database model. CRUD classes encapsulate all database
queries and provide a clean interface for the service layer.
"""

from app.crud.plan import PlanCRUD
from app.crud.workout import WorkoutCRUD
from app.crud.run import RunCRUD

__all__ = [
    "PlanCRUD",
    "WorkoutCRUD",
    "RunCRUD",
]
