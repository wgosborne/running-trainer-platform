"""
FastAPI dependency injection functions.

This module provides dependency functions that can be injected into
FastAPI route handlers using the Depends() mechanism. These dependencies
handle common concerns like database session management, authentication,
and request validation.
"""

from typing import Generator

from sqlalchemy.orm import Session
from sqlalchemy import exc

from app.db.database import SessionLocal
from app.exceptions import DatabaseError
from app.utils.logger import get_logger


# Get logger for this module
logger = get_logger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for FastAPI routes.

    This dependency function creates a database session for each request
    and ensures it's properly closed after the request completes. If an
    error occurs during the request, the transaction is rolled back.

    Yields:
        SQLAlchemy Session object

    Raises:
        DatabaseError: If session creation or management fails

    Example:
        >>> from fastapi import APIRouter, Depends
        >>> from app.api.deps import get_db
        >>>
        >>> router = APIRouter()
        >>>
        >>> @router.get("/items")
        >>> def get_items(db: Session = Depends(get_db)):
        >>>     return db.query(Item).all()

    Note:
        The session is automatically committed if the request completes
        successfully, and rolled back if an exception occurs.
    """
    db = None
    try:
        # Create new session
        db = SessionLocal()
        logger.debug("Database session created for request")

        # Yield session to route handler
        yield db

        # If we get here, the request was successful
        # Commit any pending transactions
        db.commit()
        logger.debug("Database session committed")

    except exc.SQLAlchemyError as e:
        # Database error occurred during request
        logger.error(f"Database error in request: {e}")

        # Rollback any pending transactions
        if db is not None:
            db.rollback()
            logger.debug("Database session rolled back")

        # Re-raise as application error
        raise DatabaseError(
            message="A database error occurred while processing the request",
            details={"error": str(e)}
        )

    except Exception as e:
        # Non-database error occurred
        logger.error(f"Error in request: {e}")

        # Rollback any pending transactions
        if db is not None:
            db.rollback()
            logger.debug("Database session rolled back due to non-database error")

        # Re-raise the original exception
        raise

    finally:
        # Always close the session
        if db is not None:
            db.close()
            logger.debug("Database session closed")


# Placeholder for future authentication dependency
# def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
#     """
#     Get the current authenticated user from the request.
#
#     This will be implemented when authentication is added.
#
#     Args:
#         token: JWT token from Authorization header
#
#     Returns:
#         Current authenticated user
#
#     Raises:
#         AuthenticationError: If token is invalid or expired
#     """
#     pass


# Placeholder for future authorization dependency
# def require_permissions(*required_permissions: str):
#     """
#     Dependency factory for requiring specific permissions.
#
#     This will be implemented when authorization is added.
#
#     Args:
#         required_permissions: Permission strings required for the endpoint
#
#     Returns:
#         Dependency function that checks permissions
#
#     Example:
#         >>> @router.delete("/plans/{plan_id}")
#         >>> def delete_plan(
#         >>>     plan_id: int,
#         >>>     user: User = Depends(require_permissions("plans:delete"))
#         >>> ):
#         >>>     pass
#     """
#     pass
