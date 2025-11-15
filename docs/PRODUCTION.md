# Production Readiness Guide

This document describes the production infrastructure for the Running Training Tracker microservice.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Logging](#logging)
3. [Health Checks](#health-checks)
4. [Error Handling](#error-handling)
5. [Request Tracking](#request-tracking)
6. [Security](#security)
7. [Monitoring](#monitoring)
8. [Configuration](#configuration)
9. [Deployment](#deployment)

---

## Architecture Overview

The application includes production-ready infrastructure for:

- **Structured JSON Logging**: All logs in JSON format for easy aggregation
- **Health Checks**: Liveness, readiness, and detailed health endpoints
- **Error Handling**: Global error middleware with error tracking
- **Request Correlation**: Unique request IDs for tracing
- **Security Headers**: Protection against common web vulnerabilities
- **Graceful Shutdown**: Clean shutdown with in-flight request completion
- **Metrics Hooks**: Infrastructure ready for Prometheus integration

---

## Logging

### Format

All logs are output in JSON format for easy parsing by log aggregators (ELK, Splunk, CloudWatch):

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger_name": "app.api.v1.endpoints.plans",
  "message": "Plan created successfully",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/api/v1/plans",
  "extra": {
    "plan_id": "12345"
  }
}
```

### Log Levels

- **DEBUG**: Detailed diagnostic information (only in DEBUG mode)
- **INFO**: General informational messages (request start/complete, operations)
- **WARNING**: Warning messages (validation errors, slow queries)
- **ERROR**: Error messages with full tracebacks
- **CRITICAL**: Critical errors requiring immediate attention

### Log Files

- **Location**: `logs/app.log`
- **Rotation**: 50MB files, 10 backups
- **Format**: JSON (same as console)

### Configuration

```bash
LOG_LEVEL=INFO          # Set log verbosity
USE_JSON_LOGS=true      # Use JSON format (recommended for production)
```

### Request Context

All logs automatically include request context when available:
- `request_id`: Unique correlation ID
- `user_id`: Authenticated user (if available)
- `method`: HTTP method
- `path`: Request path

---

## Health Checks

### Endpoints

#### 1. Liveness Probe

```
GET /health/live
```

**Purpose**: Tells container orchestrators if the application is alive

**Returns**:
- `200 OK`: Application is running
- Response: `{"status": "alive"}`

**Use**: Kubernetes liveness probe, Docker health check

**Note**: Always returns 200 unless application is completely broken. Failures trigger container restart.

#### 2. Readiness Probe

```
GET /health/ready
```

**Purpose**: Tells load balancers if application can handle traffic

**Returns**:
- `200 OK`: Ready to handle requests
- `503 Service Unavailable`: Not ready (e.g., database down)

**Use**: Kubernetes readiness probe, load balancer health check

**Note**: Failures remove instance from load balancer pool but don't restart container.

#### 3. Detailed Health Check

```
GET /health
```

**Purpose**: Comprehensive health status for monitoring

**Returns**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600.5,
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 2.5,
      "error": null
    }
  }
}
```

**Status Values**:
- `healthy`: All systems operational
- `degraded`: Some non-critical systems failing
- `unhealthy`: Critical systems failing

---

## Error Handling

### Error Response Format

All errors return consistent JSON responses:

```json
{
  "error_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "error_code": "VALIDATION_ERROR",
  "message": "Plan end_date must be after start_date",
  "timestamp": "2024-01-15T10:30:00Z",
  "details": {
    "field": "end_date"
  }
}
```

### Error Fields

- **error_id**: Unique ID for tracking this specific error (UUID)
- **error_code**: Machine-readable error identifier
- **message**: Human-readable error description
- **timestamp**: When the error occurred (ISO 8601)
- **details**: Additional context (optional)

### HTTP Status Codes

- `400 Bad Request`: Validation errors, invalid input
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Request validation failed
- `500 Internal Server Error`: Unexpected server error
- `503 Service Unavailable`: Service degraded/unhealthy

### Error Tracking

Use the `error_id` to:
1. Search logs for the specific error occurrence
2. Track user-reported issues
3. Correlate errors across services
4. Debug production issues

Example log search:
```bash
# Search logs for specific error
grep "a1b2c3d4-e5f6-7890" logs/app.log
```

---

## Request Tracking

### Request IDs

Every request gets a unique `request_id` for correlation:

- **Generation**: Auto-generated UUID or from `X-Request-ID` header
- **Propagation**: Included in all logs for that request
- **Response Header**: Returned in `X-Request-ID` response header

### Tracing a Request

1. Client makes request, gets `X-Request-ID` in response
2. All logs for that request include the same `request_id`
3. Search logs by `request_id` to see full request flow

Example:
```bash
# Get request ID from response
curl -v http://localhost:8000/api/v1/plans
# Returns: X-Request-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Search logs for that request
grep "a1b2c3d4-e5f6-7890" logs/app.log | jq .
```

---

## Security

### Security Headers

All responses include security headers:

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevent MIME sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| X-XSS-Protection | 1; mode=block | Enable XSS filtering |
| Strict-Transport-Security | max-age=31536000 | Enforce HTTPS (prod only) |
| Content-Security-Policy | default-src 'self' | Restrict resource loading |

### CORS Configuration

Configure allowed origins via environment variable:

```bash
# Development (allow all)
ALLOWED_ORIGINS=*

# Production (specific origins)
ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
```

### Input Validation

- All input validated via Pydantic schemas
- SQL injection prevented via parameterized queries
- XSS prevented via proper content types and CSP

---

## Monitoring

### Metrics

The application tracks:

- **Request Metrics**
  - Total requests by endpoint
  - Request latency by endpoint
  - Status code distribution

- **Database Metrics**
  - Query count
  - Query latency
  - Connection pool usage

- **Error Metrics**
  - Error count by type
  - Error rate

### Logs to Monitor

```bash
# High error rate
grep '"level":"ERROR"' logs/app.log | wc -l

# Slow requests (>1s)
grep '"duration_ms"' logs/app.log | jq 'select(.duration_ms > 1000)'

# Failed health checks
grep '"status":"unhealthy"' logs/app.log

# Database errors
grep 'DATABASE_ERROR' logs/app.log
```

### Recommended Alerts

1. **High Error Rate**: >1% of requests failing
2. **Slow Requests**: p95 latency >1s
3. **Health Check Failures**: Readiness probe failing
4. **Database Latency**: Query latency >100ms
5. **Log Errors**: Any ERROR or CRITICAL logs

---

## Configuration

### Environment Variables

#### Required

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/running_trainer
```

#### Optional (with defaults)

```bash
# Logging
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
USE_JSON_LOGS=true                # Use JSON format for logs

# Application
APP_NAME="Running Trainer API"
API_VERSION=1.0.0
DEBUG=false                       # NEVER true in production

# Database
MAX_POOL_SIZE=20                  # Connection pool size
POOL_RECYCLE=3600                 # Recycle connections after 1 hour

# Security
ALLOWED_ORIGINS=*                 # Comma-separated list of origins

# Timeouts
REQUEST_TIMEOUT=30                # Request timeout in seconds
HEALTH_CHECK_INTERVAL=30          # Health check interval
```

### Configuration Validation

On startup, configuration is validated:
- Required variables are set
- Values are in valid ranges
- Directories exist
- Warnings for insecure settings (DEBUG=true, ALLOWED_ORIGINS=*)

---

## Deployment

### Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Graceful Shutdown

The application handles `SIGTERM` and `SIGINT`:
1. Stop accepting new requests
2. Allow in-flight requests to complete (30s timeout)
3. Close database connections
4. Flush logs
5. Exit cleanly

### Pre-Deployment Checklist

- [ ] `DEBUG=false`
- [ ] `LOG_LEVEL=INFO` (not DEBUG)
- [ ] `DATABASE_URL` points to production database
- [ ] `ALLOWED_ORIGINS` set to specific origins (not *)
- [ ] Health checks respond 200
- [ ] Logs are JSON formatted
- [ ] Error tracking working (error_id in responses)
- [ ] HTTPS enabled
- [ ] Monitoring/alerting configured

---

## Troubleshooting

### Application Won't Start

```bash
# Check configuration
python -c "from app.config import get_settings; settings = get_settings(); settings.validate_config()"

# Check database connectivity
python -c "from app.db.init_db import check_db_health; print(check_db_health())"

# Check logs
tail -f logs/app.log | jq .
```

### High Error Rate

```bash
# Check error types
grep '"level":"ERROR"' logs/app.log | jq -r '.error_code' | sort | uniq -c

# Check error details
grep '"level":"ERROR"' logs/app.log | jq '.exception'

# Find slow requests causing timeouts
jq 'select(.duration_ms > 1000)' logs/app.log
```

### Database Issues

```bash
# Check database health
curl http://localhost:8000/health/ready

# Check database latency
curl http://localhost:8000/health | jq '.checks.database'

# Check connection pool
grep 'pool' logs/app.log | tail -20
```

### Finding Specific Error

```bash
# User reports error_id from response
ERROR_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# Search logs
grep "$ERROR_ID" logs/app.log | jq .

# Get full request context
grep "$ERROR_ID" logs/app.log | jq '{timestamp, level, message, request_id, method, path, exception}'
```

---

## Additional Resources

- [Deployment Guide](DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/docs)
- [Health Check Dashboard](http://localhost:8000/health)

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
