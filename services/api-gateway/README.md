# API Gateway

Single entry point for all Running Tracker microservices. Routes requests to appropriate backend services.

## Features

- Centralized routing for all microservices
- Request forwarding with header propagation
- Service discovery via environment variables
- Error handling for unreachable services
- Request/response logging
- Backward compatible with Phase 1 API routes

## Architecture

The API Gateway acts as a reverse proxy, forwarding requests to:
- **Auth Service**: User registration and authentication
- **Running Trainer Service**: Training plans, workouts, and runs
- **PDF Service**: PDF import functionality
- **Strava Service**: Strava OAuth and activity sync

## Endpoints

### Public Routes (No Auth Required)

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Protected Routes (Require Auth)

#### Training Plans
- `GET /plans` - List all plans
- `GET /plans/{id}` - Get specific plan
- `POST /plans` - Create new plan
- `POST /plans/{id}/runs` - Add run to plan

#### Runs
- `GET /runs` - List all runs
- `GET /runs/{id}` - Get specific run
- `POST /runs` - Create new run

#### PDF Import
- `POST /import/pdf` - Import training plan from PDF

#### Strava Integration
- `GET /strava/auth` - Get Strava OAuth URL
- `GET /strava/callback` - Handle OAuth callback
- `POST /strava/sync` - Sync Strava runs to plan

### Backward Compatibility

All Phase 1 routes with `/api/v1` prefix are supported:
- `GET /api/v1/plans`
- `POST /api/v1/plans`
- `GET /api/v1/runs`
- `POST /api/v1/runs`
- etc.

## Environment Variables

- `RUNNING_TRAINER_URL`: URL of Running Trainer service (default: http://running-trainer:8000)
- `AUTH_URL`: URL of Auth service (default: http://auth:8000)
- `PDF_URL`: URL of PDF service (default: http://pdf:8000)
- `STRAVA_URL`: URL of Strava service (default: http://strava:8000)

## Running Locally

```bash
cd running_tracker/services/api-gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Running with Docker

```bash
docker-compose up api-gateway
```

## Public Endpoint

The API Gateway is the only service exposed to external clients:
- **External**: http://localhost:8000
- All other services run on internal Docker network

## Error Handling

- **503 Service Unavailable**: Returned when target service is unreachable
- All other status codes are forwarded from the target service

## Logging

The gateway logs all requests:
```
2025-11-16 12:00:00 - GET /plans -> http://running-trainer:8000/api/v1/plans
2025-11-16 12:00:00 - GET /plans <- 200
```

## Testing

```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Get plans (with JWT from login)
curl http://localhost:8000/plans \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Import PDF
curl -X POST http://localhost:8000/import/pdf \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@plan.pdf" \
  -F "user_id=1"

# Strava sync
curl -X POST "http://localhost:8000/strava/sync?user_id=1&plan_id=123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
