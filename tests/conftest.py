"""
Pytest configuration and fixtures for test suite.

This module provides shared pytest fixtures for test database setup,
session management, and FastAPI test client configuration.
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.config import get_settings
from app.db.database import Base
from app.api.deps import get_db
from app.main import app


# Get settings
settings = get_settings()

# Create test database URL
# For testing, we'll use a separate test database
# Replace 'running_tracker_dev' with 'running_tracker_test' in the database name
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "running_tracker_dev",
    "running_tracker_test"
)


@pytest.fixture(scope="session")
def test_engine():
    """
    Create test database engine for the entire test session.

    This fixture is session-scoped, meaning it's created once for all tests.
    It creates all tables at the start and drops them at the end.

    Yields:
        SQLAlchemy engine instance
    """
    # Create engine for test database
    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        echo=False  # Set to True for SQL query debugging
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after tests complete
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Create a test database session for each test.

    This fixture is function-scoped, meaning a new session is created for
    each test. After each test, the transaction is rolled back to keep
    the database clean.

    Args:
        test_engine: The test database engine fixture

    Yields:
        SQLAlchemy Session object
    """
    # Create a connection
    connection = test_engine.connect()

    # Begin a transaction
    transaction = connection.begin()

    # Create a session bound to the connection
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection
    )
    session = TestSessionLocal()

    yield session

    # Rollback the transaction to keep database clean
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """
    Create FastAPI test client with dependency override.

    This fixture provides a test client that uses the test database session
    instead of the production database.

    Args:
        db_session: The test database session fixture

    Returns:
        FastAPI TestClient instance
    """
    def override_get_db():
        """Override get_db dependency to use test session."""
        try:
            yield db_session
        finally:
            pass  # Session cleanup handled by db_session fixture

    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Clear dependency overrides
    app.dependency_overrides.clear()
