"""
Application configuration management.

This module handles loading and validating configuration from environment variables.
Uses Pydantic BaseSettings for type-safe configuration with validation.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


# Load environment variables from .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All critical configuration should be defined here to ensure
    type safety and validation at startup.
    """

    # Database configuration
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database connection URL"
    )

    MAX_POOL_SIZE: int = Field(
        default=20,
        description="Maximum number of database connections in pool"
    )

    POOL_RECYCLE: int = Field(
        default=3600,
        description="Recycle database connections after N seconds"
    )

    # Logging configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    USE_JSON_LOGS: bool = Field(
        default=True,
        description="Use JSON formatting for logs (recommended for production)"
    )

    # Application metadata
    APP_NAME: str = Field(
        default="Running Trainer API",
        description="Application name for logging and documentation"
    )

    API_TITLE: str = Field(
        default="Running Training Tracker API",
        description="API title for OpenAPI documentation"
    )

    API_VERSION: str = Field(
        default="1.0.0",
        description="API version number"
    )

    API_DESCRIPTION: str = Field(
        default="A production-ready microservice for managing running training plans",
        description="API description for documentation"
    )

    # Development/Debug settings
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode (more verbose logging, detailed errors)"
    )

    # CORS configuration
    ALLOWED_ORIGINS: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins"
    )

    # Request configuration
    REQUEST_TIMEOUT: int = Field(
        default=30,
        description="Maximum request processing time in seconds"
    )

    # Health check configuration
    HEALTH_CHECK_INTERVAL: int = Field(
        default=30,
        description="Health check interval in seconds"
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Validate that DATABASE_URL is properly formatted.

        Args:
            v: The database URL string

        Returns:
            The validated database URL

        Raises:
            ValueError: If DATABASE_URL is missing or improperly formatted
        """
        if not v:
            raise ValueError("DATABASE_URL environment variable is required")

        if not v.startswith(("postgresql://", "postgresql+psycopg2://")):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://' or 'postgresql+psycopg2://'"
            )

        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """
        Validate that LOG_LEVEL is a valid logging level.

        Args:
            v: The log level string

        Returns:
            The validated log level in uppercase

        Raises:
            ValueError: If LOG_LEVEL is not a valid level
        """
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()

        if v_upper not in valid_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of {valid_levels}, got '{v}'"
            )

        return v_upper

    def get_allowed_origins(self) -> List[str]:
        """
        Parse ALLOWED_ORIGINS into a list.

        Returns:
            List of allowed origin URLs
        """
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    def validate_config(self) -> None:
        """
        Validate configuration on startup.

        Checks that all required directories exist and configuration
        values are sensible.

        Raises:
            ValueError: If configuration is invalid
        """
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Warn if DEBUG is enabled (shouldn't be in production)
        if self.DEBUG:
            print("WARNING: DEBUG mode is enabled - not recommended for production")

        # Warn if using wildcard CORS origins in production
        if not self.DEBUG and self.ALLOWED_ORIGINS == "*":
            print("WARNING: CORS allows all origins (*) - not recommended for production")

        # Validate pool size is reasonable
        if self.MAX_POOL_SIZE < 5:
            raise ValueError("MAX_POOL_SIZE should be at least 5")

        if self.MAX_POOL_SIZE > 100:
            print(f"WARNING: MAX_POOL_SIZE is very high ({self.MAX_POOL_SIZE})")

    def log_config(self, hide_secrets: bool = True) -> dict:
        """
        Get configuration as dict for logging.

        Args:
            hide_secrets: Whether to hide sensitive values

        Returns:
            Configuration dictionary
        """
        config_dict = {
            "app_name": self.APP_NAME,
            "api_version": self.API_VERSION,
            "debug": self.DEBUG,
            "log_level": self.LOG_LEVEL,
            "use_json_logs": self.USE_JSON_LOGS,
            "max_pool_size": self.MAX_POOL_SIZE,
            "pool_recycle": self.POOL_RECYCLE,
            "request_timeout": self.REQUEST_TIMEOUT,
            "health_check_interval": self.HEALTH_CHECK_INTERVAL,
            "allowed_origins": self.get_allowed_origins() if not hide_secrets else "***",
        }

        if hide_secrets:
            config_dict["database_url"] = "***"
        else:
            # Still partially hide database credentials
            db_url = self.DATABASE_URL
            if "@" in db_url:
                parts = db_url.split("@")
                config_dict["database_url"] = f"***@{parts[1]}"
            else:
                config_dict["database_url"] = "***"

        return config_dict

    class Config:
        """Pydantic configuration."""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
# This is initialized once at module import and reused throughout the application
try:
    settings = Settings()
except Exception as e:
    # If settings fail to load, log the error and re-raise
    # This ensures the application fails fast on misconfiguration
    print(f"ERROR: Failed to load application settings: {e}")
    raise


# Convenience function for accessing settings
def get_settings() -> Settings:
    """
    Get the global settings instance.

    Returns:
        The application settings object
    """
    return settings
