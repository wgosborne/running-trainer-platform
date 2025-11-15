# Deployment Guide

Quick start guide for deploying the Running Training Tracker to production.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL 15+ database
- Python 3.11+ (for local development)

---

## Quick Start

### 1. Environment Setup

Create `.env` file with production values:

```bash
# Copy example
cp .env.example .env

# Edit with production values
vim .env
```

**Critical Settings**:
```bash
# REQUIRED
DATABASE_URL=postgresql://user:password@db-host:5432/running_trainer

# SECURITY (Change for production!)
DEBUG=false
ALLOWED_ORIGINS=https://your-frontend.com

# LOGGING
LOG_LEVEL=INFO
USE_JSON_LOGS=true
```

### 2. Database Setup

```bash
# Create database
createdb running_trainer

# Or using Docker:
docker-compose up -d postgres

# Tables are created automatically on first run
```

### 3. Run with Docker

```bash
# Build image
docker build -t running-tracker:latest .

# Run container
docker run -d \
  --name running-tracker \
  -p 8000:8000 \
  --env-file .env \
  running-tracker:latest

# Check health
curl http://localhost:8000/health/live
```

### 4. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Check health
curl http://localhost:8000/health
```

### 5. Verify Deployment

```bash
# Liveness check
curl http://localhost:8000/health/live
# Should return: {"status": "alive"}

# Readiness check
curl http://localhost:8000/health/ready
# Should return 200 if database connected

# Detailed health
curl http://localhost:8000/health | jq .

# API docs
open http://localhost:8000/docs
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Review and update `.env` file
- [ ] Set `DEBUG=false`
- [ ] Set appropriate `LOG_LEVEL` (INFO or WARNING)
- [ ] Configure `ALLOWED_ORIGINS` (not `*` in production)
- [ ] Verify `DATABASE_URL` is correct
- [ ] Ensure database exists and is accessible
- [ ] Review `MAX_POOL_SIZE` based on expected load

### Deployment

- [ ] Build Docker image
- [ ] Tag with version: `docker tag running-tracker:latest running-tracker:v1.0.0`
- [ ] Push to registry (if using)
- [ ] Deploy to environment
- [ ] Wait for health checks to pass
- [ ] Verify `/health/live` returns 200
- [ ] Verify `/health/ready` returns 200
- [ ] Check logs for errors: `docker logs running-tracker`

### Post-Deployment

- [ ] Test critical endpoints
- [ ] Verify error responses include `error_id`
- [ ] Check response headers include `X-Request-ID`
- [ ] Verify security headers are present
- [ ] Monitor error rates
- [ ] Set up log aggregation
- [ ] Configure alerts

---

## Docker Deployment

### Build Image

```bash
# Build with version tag
docker build -t running-tracker:v1.0.0 .

# Also tag as latest
docker tag running-tracker:v1.0.0 running-tracker:latest
```

### Run Container

```bash
docker run -d \
  --name running-tracker \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/running_trainer" \
  -e LOG_LEVEL="INFO" \
  -e DEBUG="false" \
  -e ALLOWED_ORIGINS="https://app.example.com" \
  --restart unless-stopped \
  running-tracker:v1.0.0
```

### Health Check

Docker automatically health checks using:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health/live || exit 1
```

Check health status:
```bash
docker ps  # Shows (healthy) status
docker inspect running-tracker | jq '.[0].State.Health'
```

---

## Docker Compose Deployment

### Configuration

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://tracker:password@postgres:5432/running_trainer
      LOG_LEVEL: INFO
      DEBUG: "false"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: running_trainer
      POSTGRES_USER: tracker
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracker"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart API
docker-compose restart api

# Stop all services
docker-compose down

# Stop and remove data
docker-compose down -v
```

---

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: running-tracker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: running-tracker
  template:
    metadata:
      labels:
        app: running-tracker
    spec:
      containers:
      - name: api
        image: running-tracker:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: running-tracker-secrets
              key: database-url
        - name: LOG_LEVEL
          value: "INFO"
        - name: DEBUG
          value: "false"
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
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: running-tracker
spec:
  selector:
    app: running-tracker
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Deploy

```bash
# Create secrets
kubectl create secret generic running-tracker-secrets \
  --from-literal=database-url='postgresql://user:pass@db:5432/running_trainer'

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get svc running-tracker

# View logs
kubectl logs -f deployment/running-tracker

# Check health
kubectl port-forward svc/running-tracker 8000:80
curl http://localhost:8000/health
```

---

## Environment-Specific Configuration

### Development

```bash
DEBUG=true
LOG_LEVEL=DEBUG
USE_JSON_LOGS=false  # Human-readable logs
ALLOWED_ORIGINS=*
```

### Staging

```bash
DEBUG=false
LOG_LEVEL=INFO
USE_JSON_LOGS=true
ALLOWED_ORIGINS=https://staging.example.com
```

### Production

```bash
DEBUG=false
LOG_LEVEL=INFO  # or WARNING
USE_JSON_LOGS=true
ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
MAX_POOL_SIZE=50  # Increase for high traffic
```

---

## Monitoring Setup

### Log Aggregation

**Using ELK Stack**:
```bash
# Point Filebeat to logs/app.log
# Logs are already in JSON format
filebeat.inputs:
- type: log
  paths:
    - /app/logs/app.log
  json.keys_under_root: true
```

**Using CloudWatch**:
```bash
# Install CloudWatch agent
# Configure to read logs/app.log
```

### Alerts

**Recommended Alerts**:

1. **High Error Rate**
```
Alert if: error_count/request_count > 0.01 (1%)
Severity: Warning
```

2. **Service Down**
```
Alert if: health_check_status != "healthy"
Severity: Critical
```

3. **Slow Requests**
```
Alert if: p95(request_duration_ms) > 1000
Severity: Warning
```

4. **Database Issues**
```
Alert if: db_health_status != "healthy"
Severity: Critical
```

---

## Rollback

### Docker

```bash
# List images
docker images running-tracker

# Roll back to previous version
docker stop running-tracker
docker rm running-tracker
docker run -d --name running-tracker running-tracker:v0.9.0
```

### Kubernetes

```bash
# View rollout history
kubectl rollout history deployment/running-tracker

# Roll back to previous version
kubectl rollout undo deployment/running-tracker

# Roll back to specific revision
kubectl rollout undo deployment/running-tracker --to-revision=2
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs running-tracker

# Common issues:
# - Missing DATABASE_URL
# - Database not accessible
# - Port already in use
```

### Health Checks Failing

```bash
# Check readiness
curl http://localhost:8000/health/ready

# Check detailed health
curl http://localhost:8000/health | jq .

# Common causes:
# - Database connection issues
# - Network problems
# - Incorrect DATABASE_URL
```

### High Memory Usage

```bash
# Check current usage
docker stats running-tracker

# If memory is high:
# - Reduce MAX_POOL_SIZE
# - Increase container memory limits
# - Check for memory leaks in logs
```

### Database Connection Issues

```bash
# Test database connectivity
docker exec running-tracker python -c "
from app.db.init_db import check_db_health
print(check_db_health())
"

# Common fixes:
# - Verify DATABASE_URL format
# - Check database is running
# - Verify network connectivity
# - Check firewall rules
```

---

## Additional Resources

- [Production Guide](PRODUCTION.md)
- [API Documentation](http://localhost:8000/docs)
- [Health Checks](http://localhost:8000/health)

---

**Last Updated**: 2024-01-15
