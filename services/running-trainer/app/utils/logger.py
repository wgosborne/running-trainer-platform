"""
Logging configuration and utilities.

This module sets up structured logging for the application with JSON-formatted
output for easy parsing by log aggregators (ELK, Splunk, CloudWatch, etc.).
Includes request context tracking for correlation.
"""

import logging
import json
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any
from contextvars import ContextVar


# Directory for log files
LOG_DIR = Path("logs")

# Log file configuration
LOG_FILE = LOG_DIR / "app.log"
LOG_MAX_BYTES = 50 * 1024 * 1024  # 50 MB
LOG_BACKUP_COUNT = 10  # Keep 10 backup files

# Context variables for request tracking (thread-safe)
request_context_var: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    'request_context',
    default=None
)


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.

    Each log entry is a single JSON object with consistent fields,
    making it easy to parse and search in log aggregation tools.

    Fields:
        - timestamp: ISO 8601 formatted timestamp
        - level: Log level (INFO, WARNING, ERROR, etc.)
        - logger_name: Name of the logger (module path)
        - message: The log message
        - request_id: Request correlation ID (if available)
        - user_id: User ID (if available)
        - exception: Exception information (if available)
        - extra: Any additional context fields
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON string representing the log entry
        """
        # Get request context if available
        context = request_context_var.get()

        # Build base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
        }

        # Add request context if available
        if context:
            log_entry["request_id"] = context.get("request_id")
            log_entry["user_id"] = context.get("user_id")
            log_entry["method"] = context.get("method")
            log_entry["path"] = context.get("path")

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add any extra fields from record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info"
            ]:
                extra_fields[key] = value

        if extra_fields:
            log_entry["extra"] = extra_fields

        # Add source location in debug mode
        if record.levelno == logging.DEBUG:
            log_entry["source"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName
            }

        return json.dumps(log_entry, default=str)


class ConsoleFormatter(logging.Formatter):
    """
    Formatter for console output - human-readable with colors (if supported).

    This is used for local development to make logs easier to read.
    In production, use JSON formatter for both console and file.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console output."""
        # Get request context if available
        context = request_context_var.get()

        # Build message with context
        message = record.getMessage()
        if context and context.get("request_id"):
            message = f"[{context['request_id'][:8]}] {message}"

        # Add color if supported
        if sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            level = f"{color}{record.levelname:8s}{reset}"
        else:
            level = f"{record.levelname:8s}"

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        # Build formatted message
        formatted = f"[{timestamp}] {level} [{record.name}] {message}"

        # Add exception if present
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


def setup_logging(log_level: str = "INFO", use_json: bool = True) -> None:
    """
    Set up logging configuration for the application.

    Configures both console and file logging with appropriate formatters
    and handlers. Creates the logs directory if it doesn't exist.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting (True for production)
    """
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True)

    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
    if use_json:
        console_formatter = JSONFormatter()
        file_formatter = JSONFormatter()
    else:
        console_formatter = ConsoleFormatter()
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler - logs to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler - logs to rotating file with JSON format
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Log the initialization
    root_logger.info(
        f"Logging initialized",
        extra={
            "log_level": log_level,
            "log_file": str(LOG_FILE.absolute()),
            "json_format": use_json
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module or component.

    This is the primary way to get a logger in the application.
    Each module should call this with __name__ to get a properly
    namespaced logger.

    Args:
        name: The name for the logger (typically __name__)

    Returns:
        A configured logger instance

    Example:
        >>> from app.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
    """
    return logging.getLogger(name)


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
    **kwargs
) -> None:
    """
    Set the current request context for logging.

    This context will be automatically included in all log entries
    for the current request. Uses contextvars for thread-safety.

    Args:
        request_id: Unique request correlation ID
        user_id: Authenticated user ID (if available)
        method: HTTP method (GET, POST, etc.)
        path: Request path
        **kwargs: Additional context fields
    """
    context = {
        "request_id": request_id,
        "user_id": user_id,
        "method": method,
        "path": path,
        **kwargs
    }
    request_context_var.set(context)


def clear_request_context() -> None:
    """Clear the current request context."""
    request_context_var.set(None)


def get_request_context() -> Optional[Dict[str, Any]]:
    """Get the current request context."""
    return request_context_var.get()


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
) -> None:
    """
    Log a message with additional context fields.

    This is a convenience function for adding extra fields to log entries
    beyond the standard request context.

    Args:
        logger: The logger to use
        level: Log level (debug, info, warning, error, critical)
        message: The log message
        **kwargs: Additional context fields to include

    Example:
        >>> logger = get_logger(__name__)
        >>> log_with_context(
        ...     logger, "info", "User logged in",
        ...     user_id="123", ip_address="192.168.1.1"
        ... )
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra=kwargs)


def log_exception(
    logger: logging.Logger,
    message: str,
    exc_info: bool = True,
    **kwargs
) -> None:
    """
    Log an exception with full traceback and context.

    Args:
        logger: The logger to use
        message: Description of what was being done when exception occurred
        exc_info: Whether to include exception info (default: True)
        **kwargs: Additional context fields

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_exception(logger, "Failed to process request", user_id="123")
    """
    logger.error(message, exc_info=exc_info, extra=kwargs)


# Convenience function to flush all handlers (useful on shutdown)
def flush_logs() -> None:
    """
    Flush all log handlers to ensure all messages are written.

    Call this during application shutdown to ensure no logs are lost.
    """
    for handler in logging.root.handlers:
        handler.flush()
