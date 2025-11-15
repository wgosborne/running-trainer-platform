# Production Readiness - Implementation Guide

This guide details the remaining tasks to complete the production readiness implementation.

## ✅ Completed

The following components are **already implemented**:

1. **✅ app/utils/logger.py** - Structured JSON logging with request context
2. **✅ app/config.py** - Production configuration with validation
3. **✅ app/middleware/** - Error handling, request context, security headers
4. **✅ app/health/** - Health check models, checks, and routes
5. **✅ app/exceptions.py** - Error tracking with error_id
6. **✅ app/monitoring/metrics.py** - Metrics collection hooks
7. **✅ docs/PRODUCTION.md** - Comprehensive production guide
8. **✅ docs/DEPLOYMENT.md** - Deployment instructions
9. **✅ .env.example** - Updated with all configuration options

## 🔨 Remaining Tasks

### 1. Update `app/main.py`

**Purpose**: Integrate all the production infrastructure

**Changes needed**:

```python
# Add imports at top
from contextlib import asynccontextmanager
import signal
import sys

from app.middleware import (
    error_handler_middleware,
    request_context_middleware,
    add_security_headers
)
from app.health import router as health_router
from app.utils.logger import setup_logging, get_logger, flush_logs
from app.config import get_settings

settings = get_settings()
logger = get_logger(__name__)

# Replace lifespan with:
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("="*70)
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info("="*70)

    # Setup logging
    setup_logging(settings.LOG_LEVEL, settings.USE_JSON_LOGS)

    # Validate configuration
    try:
        settings.validate_config()
        logger.info("Configuration validated successfully")
        logger.info(f"Config: {settings.log_config()}")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    logger.info(f"{settings.APP_NAME} started successfully")
    logger.info("="*70)

    yield

    # Shutdown
    logger.info("="*70)
    logger.info("Shutting down gracefully...")
    logger.info("="*70)

    # Flush logs
    flush_logs()

    logger.info("Shutdown complete")

# Update FastAPI app creation:
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware (ORDER MATTERS!)
@app.middleware("http")
async def _error_handler(request, call_next):
    return await error_handler_middleware(request, call_next)

@app.middleware("http")
async def _request_context(request, call_next):
    return await request_context_middleware(request, call_next)

@app.middleware("http")
async def _security_headers(request, call_next):
    return await add_security_headers(request, call_next)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(health_router)  # Health checks
app.include_router(api_v1_router)  # Main API

# Remove existing exception handlers (middleware handles them now)
# Keep /health and / endpoints
```

### 2. Update `app/db/database.py`

**Purpose**: Add production-ready connection pooling

**Changes**:

```python
# Update engine creation:
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.MAX_POOL_SIZE,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=settings.POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections
    echo=settings.DEBUG,  # Log SQL in debug mode
)

# Add at end of file:
def dispose_pool():
    """Dispose database connection pool on shutdown."""
    logger.info("Disposing database connection pool...")
    engine.dispose()
    logger.info("Database pool disposed")
```

### 3. Create Test Files

**a) `tests/integration/test_health_endpoints.py`**:

```python
import pytest

class TestHealthEndpoints:
    def test_liveness_check_success(self, client):
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}

    def test_readiness_check_success(self, client, db_session):
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_detailed_health_check(self, client, db_session):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
```

**b) `tests/integration/test_error_middleware.py`**:

```python
import pytest
from uuid import UUID

class TestErrorHandling:
    def test_not_found_returns_error_id(self, client):
        response = client.get("/api/v1/plans/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        data = response.json()
        assert "error_id" in data
        # Verify error_id is valid UUID
        UUID(data["error_id"])

    def test_validation_error_returns_error_id(self, client):
        response = client.post("/api/v1/plans", json={})
        assert response.status_code == 422
        data = response.json()
        assert "error_id" in data
```

**c) `tests/integration/test_request_context.py`**:

```python
import pytest

class TestRequestContext:
    def test_request_id_in_response_header(self, client):
        response = client.get("/health/live")
        assert "X-Request-ID" in response.headers

    def test_custom_request_id_preserved(self, client):
        custom_id = "test-request-123"
        response = client.get(
            "/health/live",
            headers={"X-Request-ID": custom_id}
        )
        assert response.headers["X-Request-ID"] == custom_id
```

### 4. Update `Dockerfile`

**Add health check**:

```dockerfile
# Add before CMD
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

# Use exec form for proper signal handling
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5. Update `docker-compose.yml`

**Add health checks to services**:

```yaml
services:
  api:
    # ... existing config ...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    # ... existing config ...
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracker"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 6. Update `README.md`

**Add sections**:

```markdown
## Production Readiness

This application includes production-ready infrastructure:

- **Structured Logging**: JSON logs with request correlation
- **Health Checks**: `/health/live`, `/health/ready`, `/health`
- **Error Tracking**: All errors include `error_id` for debugging
- **Request Tracing**: `X-Request-ID` headers for correlation
- **Security Headers**: Protection against common vulnerabilities
- **Graceful Shutdown**: Clean shutdown with in-flight request completion

### Health Check Endpoints

- `GET /health/live` - Liveness probe (always 200 if running)
- `GET /health/ready` - Readiness probe (200 if can handle traffic)
- `GET /health` - Detailed health status

### Logging

Logs are in JSON format for easy aggregation:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "abc123...",
  "method": "POST",
  "path": "/api/v1/plans"
}
```

### Error Handling

All errors return consistent JSON responses with `error_id` for tracking:
```json
{
  "error_id": "a1b2c3d4-e5f6-7890...",
  "error_code": "VALIDATION_ERROR",
  "message": "Plan end_date must be after start_date",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Documentation

- [Production Guide](docs/PRODUCTION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/docs)
```

### 7. Update `requirements.txt`

**Add if not present**:

```txt
# Add to existing requirements
psutil==5.9.6         # For system metrics
```

---

## Verification Steps

After implementing the above changes:

### 1. Configuration Validation

```bash
python -c "from app.config import get_settings; s = get_settings(); s.validate_config(); print('OK')"
```

### 2. Start Application

```bash
# With Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### 3. Test Health Checks

```bash
# Liveness (should always return 200)
curl http://localhost:8000/health/live

# Readiness (200 if database connected)
curl http://localhost:8000/health/ready

# Detailed health
curl http://localhost:8000/health | jq .
```

### 4. Test Error Handling

```bash
# Should return error with error_id
curl http://localhost:8000/api/v1/plans/00000000-0000-0000-0000-000000000000

# Should include X-Request-ID header
curl -v http://localhost:8000/health/live 2>&1 | grep X-Request-ID
```

### 5. Check Logs

```bash
# Should be JSON formatted
tail -f logs/app.log | jq .

# Should include request_id
grep request_id logs/app.log | head -1 | jq .
```

### 6. Run Tests

```bash
# Run all tests including new health/error tests
pytest

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/integration/test_health_endpoints.py -v
```

### 7. Security Headers

```bash
# Check security headers are present
curl -v http://localhost:8000/health/live 2>&1 | grep -E "X-Content-Type|X-Frame|X-XSS"
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All tasks above completed
- [ ] Tests passing: `pytest`
- [ ] Health checks working: `curl http://localhost:8000/health`
- [ ] Logs are JSON: `tail logs/app.log`
- [ ] Error responses include `error_id`
- [ ] Security headers present
- [ ] `DEBUG=false` in .env
- [ ] `ALLOWED_ORIGINS` set (not *)
- [ ] Database URL points to production
- [ ] Connection pool sized appropriately
- [ ] Monitoring/alerting configured

---

## Quick Implementation

If you want to implement everything quickly:

```bash
# 1. Update main.py (see section 1 above)
vim app/main.py

# 2. Update database.py (see section 2 above)
vim app/db/database.py

# 3. Create test files
mkdir -p tests/integration
touch tests/integration/test_health_endpoints.py
touch tests/integration/test_error_middleware.py
touch tests/integration/test_request_context.py
# (Add content from section 3 above)

# 4. Update Dockerfile
vim Dockerfile
# (Add healthcheck from section 4)

# 5. Update docker-compose.yml
vim docker-compose.yml
# (Add healthchecks from section 5)

# 6. Update README.md
vim README.md
# (Add sections from section 6)

# 7. Install dependencies
pip install psutil==5.9.6

# 8. Verify
docker-compose up -d
curl http://localhost:8000/health
pytest
```

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs -f api`
2. Verify config: `python -c "from app.config import get_settings; get_settings().validate_config()"`
3. Test database: `python -c "from app.db.init_db import check_db_health; print(check_db_health())"`
4. Review documentation: `docs/PRODUCTION.md` and `docs/DEPLOYMENT.md`

---

**Last Updated**: 2024-01-15
