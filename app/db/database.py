"""
Database connection and session management.

This module sets up SQLAlchemy engine, session factory, and declarative base.
It handles connection pooling, error recovery, and provides utilities for
database session management in the application.
"""

from typing import Generator

from sqlalchemy import create_engine, event, exc, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import get_settings
from app.constants import DB_CONSTANTS
from app.exceptions import DatabaseError
from app.utils.logger import get_logger


# Get logger for this module
logger = get_logger(__name__)

# Get application settings
settings = get_settings()


# ============================================================================
# SQLAlchemy Engine Configuration
# ============================================================================

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=DB_CONSTANTS.POOL_SIZE,
    max_overflow=DB_CONSTANTS.MAX_OVERFLOW,
    pool_timeout=DB_CONSTANTS.POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=DB_CONSTANTS.POOL_RECYCLE,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)


# ============================================================================
# Session Factory
# ============================================================================

# Create session factory
# autocommit=False: Transactions must be explicitly committed
# autoflush=False: Changes are not automatically flushed to DB
# bind=engine: Sessions are bound to our engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================================
# Declarative Base
# ============================================================================

# Create declarative base class for all models
# All database models should inherit from this
Base = declarative_base()


# ============================================================================
# Database Session Management
# ============================================================================


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields a database session.

    This is used with FastAPI's dependency injection system to provide
    database sessions to route handlers. The session is automatically
    closed after the request is complete, even if an exception occurs.

    Yields:
        Database session

    Raises:
        DatabaseError: If session creation fails

    Example:
        >>> from fastapi import Depends
        >>> @app.get("/items")
        >>> def get_items(db: Session = Depends(get_db)):
        >>>     return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except exc.SQLAlchemyError as e:
        logger.error(f"Database error during session: {e}")
        db.rollback()
        raise DatabaseError(
            message="Database operation failed",
            details={"error": str(e)}
        )
    finally:
        db.close()
        logger.debug("Database session closed")


def test_connection() -> bool:
    """
    Test the database connection.

    Attempts to connect to the database and execute a simple query.
    Useful for health checks and startup validation.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except exc.SQLAlchemyError as e:
        logger.error(f"Database connection test failed: {e}")
        return False


# ============================================================================
# Event Listeners
# ============================================================================


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Event listener for new database connections.

    This is called whenever a new connection is established.
    Can be used to set connection-level settings.

    Note: Currently a no-op for PostgreSQL, but useful for SQLite
    if switching databases for testing.

    Args:
        dbapi_conn: The raw DBAPI connection
        connection_record: Connection record from the pool
    """
    # For PostgreSQL, we might want to set timezone or other settings
    # cursor = dbapi_conn.cursor()
    # cursor.execute("SET timezone='UTC'")
    # cursor.close()
    pass


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Event listener for connection checkout from pool.

    Called whenever a connection is retrieved from the pool.
    Useful for logging and monitoring connection usage.

    Args:
        dbapi_conn: The raw DBAPI connection
        connection_record: Connection record from the pool
        connection_proxy: Proxy for the connection
    """
    logger.debug("Database connection checked out from pool")


@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """
    Event listener for connection checkin to pool.

    Called whenever a connection is returned to the pool.
    Useful for logging and monitoring connection usage.

    Args:
        dbapi_conn: The raw DBAPI connection
        connection_record: Connection record from the pool
    """
    logger.debug("Database connection returned to pool")


# ============================================================================
# Initialization
# ============================================================================

# Log database configuration on module load
logger.info(f"Database engine configured: {settings.DATABASE_URL.split('@')[-1]}")
logger.info(
    f"Connection pool: size={DB_CONSTANTS.POOL_SIZE}, "
    f"max_overflow={DB_CONSTANTS.MAX_OVERFLOW}"
)
