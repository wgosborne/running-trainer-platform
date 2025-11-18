"""
Auth Service - Simple JWT authentication with SQLite.

This service provides user registration, login, and token verification endpoints.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import FastAPI, Depends, HTTPException, Header
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from models import User, get_db, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Auth Service",
    description="Simple JWT authentication service",
    version="1.0.0"
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 86400  # 24 hours


# Pydantic models
class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response model for user data."""
    user_id: str
    email: str


class TokenResponse(BaseModel):
    """Response model for login."""
    token: str
    user_id: str


class VerifyResponse(BaseModel):
    """Response model for token verification."""
    user_id: str
    valid: bool


# Helper functions
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(user_id: str) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_id: User's unique identifier

    Returns:
        JWT token string
    """
    expiration = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION_SECONDS)
    payload = {
        "user_id": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_jwt_token(token: str) -> str:
    """
    Verify a JWT token and extract user_id.

    Args:
        token: JWT token string

    Returns:
        User ID from token

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Invalid token payload")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")


# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Auth service started successfully")


# API Endpoints
@app.post("/register", response_model=UserResponse, status_code=201)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.

    Args:
        request: Registration request with email and password
        db: Database session

    Returns:
        User ID and email

    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            logger.warning(f"Registration failed: Email already exists - {request.email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password
        password_hash = hash_password(request.password)

        # Create user
        user = User(
            email=request.email,
            password_hash=password_hash
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User registered successfully: {user.email} (ID: {user.id})")

        return UserResponse(user_id=user.id, email=user.email)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@app.post("/login", response_model=TokenResponse, status_code=200)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Login and receive JWT token.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        JWT token and user ID

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.warning(f"Login failed: User not found - {request.email}")
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # Verify password
        if not verify_password(request.password, user.password_hash):
            logger.warning(f"Login failed: Invalid password - {request.email}")
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # Create JWT token
        token = create_jwt_token(user.id)

        logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")

        return TokenResponse(token=token, user_id=user.id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


@app.get("/verify", response_model=VerifyResponse, status_code=200)
def verify(
    authorization: Annotated[str | None, Header()] = None
) -> VerifyResponse:
    """
    Verify JWT token validity.

    Args:
        authorization: Authorization header with Bearer token

    Returns:
        User ID and validity status

    Raises:
        HTTPException: If token is missing or invalid
    """
    try:
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid authorization header format")

        token = parts[1]

        # Verify token
        user_id = verify_jwt_token(token)

        logger.info(f"Token verified successfully for user ID: {user_id}")

        return VerifyResponse(user_id=user_id, valid=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Auth Service"}
