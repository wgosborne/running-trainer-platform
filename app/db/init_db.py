"""
Database initialization utilities.

This module provides functions for creating and dropping database tables.
These utilities are used during application startup, testing, and migrations.
"""

from sqlalchemy import exc

from app.db.database import Base, engine, test_connection
from app.exceptions import DatabaseError
from app.utils.logger import get_logger

# Import models to register them with Base.metadata
# This ensures all tables are created when calling Base.metadata.create_all()
from app.models import Plan, Workout, Run  # noqa: F401


# Get logger for this module
logger = get_logger(__name__)


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This function creates all tables defined in SQLAlchemy models that
    inherit from Base. It's idempotent - running it multiple times
    won't cause errors if tables already exist.

    This should be called:
    - On application startup (in production)
    - At the beginning of test suites
    - When setting up a new environment

    Raises:
        DatabaseError: If table creation fails

    Example:
        >>> from app.db.init_db import init_db
        >>> init_db()
        >>> # All tables are now created
    """
    try:
        logger.info("Initializing database tables...")

        # Test connection first
        if not test_connection():
            raise DatabaseError(
                message="Cannot connect to database",
                operation="init_db"
            )

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("Database tables initialized successfully")

    except exc.SQLAlchemyError as e:
        error_msg = f"Failed to initialize database: {e}"
        logger.error(error_msg)
        raise DatabaseError(
            message=error_msg,
            operation="init_db",
            details={"error": str(e)}
        )


def drop_db() -> None:
    """
    Drop all database tables.

    This function drops all tables defined in SQLAlchemy models that
    inherit from Base. This is a DESTRUCTIVE operation that will
    DELETE ALL DATA.

    This should ONLY be called:
    - During development for quick resets
    - In test cleanup (test databases only)
    - NEVER in production

    Raises:
        DatabaseError: If table dropping fails

    Warning:
        This will permanently delete all data in the database!

    Example:
        >>> from app.db.init_db import drop_db
        >>> drop_db()
        >>> # All tables and data are now deleted
    """
    try:
        logger.warning("Dropping all database tables...")

        # Test connection first
        if not test_connection():
            raise DatabaseError(
                message="Cannot connect to database",
                operation="drop_db"
            )

        # Drop all tables
        Base.metadata.drop_all(bind=engine)

        logger.warning("All database tables dropped successfully")

    except exc.SQLAlchemyError as e:
        error_msg = f"Failed to drop database tables: {e}"
        logger.error(error_msg)
        raise DatabaseError(
            message=error_msg,
            operation="drop_db",
            details={"error": str(e)}
        )


def reset_db() -> None:
    """
    Reset the database by dropping and recreating all tables.

    This is a convenience function that combines drop_db() and init_db().
    It provides a clean slate for development and testing.

    This should ONLY be called:
    - During development for quick resets
    - In test setup (test databases only)
    - NEVER in production

    Raises:
        DatabaseError: If reset fails

    Warning:
        This will permanently delete all data in the database!

    Example:
        >>> from app.db.init_db import reset_db
        >>> reset_db()
        >>> # Database is now fresh with empty tables
    """
    logger.warning("Resetting database (drop + create)...")
    drop_db()
    init_db()
    logger.info("Database reset complete")


def check_db_health() -> bool:
    """
    Check if the database is healthy and accessible.

    This performs a connection test and verifies that the application
    can communicate with the database.

    Returns:
        True if database is healthy, False otherwise

    Example:
        >>> from app.db.init_db import check_db_health
        >>> if check_db_health():
        >>>     print("Database is ready")
    """
    logger.info("Checking database health...")
    is_healthy = test_connection()

    if is_healthy:
        logger.info("Database health check passed")
    else:
        logger.error("Database health check failed")

    return is_healthy
