"""
Base model classes for SQLAlchemy ORM.

This module provides the declarative base and common mixin for all models.
All database models should inherit from both Base and BaseMixin.

Migrations will be handled by alembic in Phase 3. For Phase 1, tables are created
on app startup via Base.metadata.create_all()
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class BaseMixin:
    """
    Base mixin class providing common fields for all models.

    All models should inherit from this mixin to get:
    - id: UUID primary key
    - created_at: Timestamp of record creation
    - updated_at: Timestamp of last update (auto-updated)
    """

    # Primary key - UUID for distributed systems and security
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        doc="Unique identifier for this record"
    )

    # Timestamp fields
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="UTC timestamp when this record was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="UTC timestamp when this record was last updated"
    )

    def __repr__(self) -> str:
        """
        String representation of the model for debugging.

        Returns:
            String representation showing class name and id
        """
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model

        Note:
            This is a basic implementation. Relationships are not included.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert UUID and datetime to string for JSON serialization
            if isinstance(value, uuid.UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
