"""
Metrics collection and timing utilities.

Provides hooks for monitoring request latency, database queries,
and other performance metrics. Ready for Prometheus integration.
"""

import time
from functools import wraps
from typing import Callable, Any

from app.utils.logger import get_logger


logger = get_logger(__name__)


def timeit(operation_name: str) -> Callable:
    """
    Decorator to measure and log execution time.

    Use this to track slow operations and identify performance bottlenecks.

    Args:
        operation_name: Name of the operation being timed

    Returns:
        Decorated function

    Example:
        >>> @timeit("database_query")
        >>> def get_user(user_id):
        >>>     return db.query(User).get(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000

                logger.debug(
                    f"{operation_name} completed",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "function": func.__name__
                    }
                )

                # Log slow operations
                if duration_ms > 1000:
                    logger.warning(
                        f"Slow operation detected: {operation_name}",
                        extra={
                            "operation": operation_name,
                            "duration_ms": round(duration_ms, 2),
                            "threshold_ms": 1000
                        }
                    )

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000

                logger.debug(
                    f"{operation_name} completed",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "function": func.__name__
                    }
                )

                # Log slow operations
                if duration_ms > 1000:
                    logger.warning(
                        f"Slow operation detected: {operation_name}",
                        extra={
                            "operation": operation_name,
                            "duration_ms": round(duration_ms, 2),
                            "threshold_ms": 1000
                        }
                    )

        # Return appropriate wrapper based on whether function is async
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class MetricsCollector:
    """
    Metrics collector for Prometheus integration (Phase 2).

    This is a placeholder for future Prometheus metrics collection.
    Currently logs metrics; can be extended to export to Prometheus.

    Metrics to track:
    - Request count (by method, path, status)
    - Request latency (by endpoint)
    - Database query count
    - Database query latency
    - Error count (by type)
    - Active connections
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.request_count = 0
        self.error_count = 0
        self.db_query_count = 0

    def increment_request(self, method: str, path: str, status: int):
        """Record a completed request."""
        self.request_count += 1
        logger.debug(
            "Request metric recorded",
            extra={
                "metric": "request_count",
                "method": method,
                "path": path,
                "status": status
            }
        )

    def increment_error(self, error_type: str):
        """Record an error occurrence."""
        self.error_count += 1
        logger.debug(
            "Error metric recorded",
            extra={
                "metric": "error_count",
                "error_type": error_type
            }
        )

    def record_latency(self, operation: str, latency_ms: float):
        """Record operation latency."""
        logger.debug(
            "Latency metric recorded",
            extra={
                "metric": "latency",
                "operation": operation,
                "latency_ms": latency_ms
            }
        )


# Global metrics collector instance
metrics_collector = MetricsCollector()
