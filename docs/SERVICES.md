# Running Trainer - Service Details

## Service Overview

This document provides detailed information about each microservice in the Running Trainer platform.

---

## 1. Running Trainer Service

**Port:** 8001
**Status:** Complete (Phase 1)
**Repository:** `services/running-trainer/`

### Description

The core service for managing running training plans, workouts, and run records. This service handles all CRUD operations and business logic for training plan management.

### Technology Stack

- **Language:** Python 3.11
- **Framework:** FastAPI
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Testing:** pytest
- **Validation:** Pydantic

### Database Schema

**Tables:**
- `training_plans` - Training plan definitions
- `workouts` - Individual workout templates
- `runs` - Completed run records

**Key Fields:**

Training Plans:
- `id` (UUID) - Primary key
- `name` (String) - Plan name
- `description` (Text) - Plan description
- `start_date` (Date) - Plan start date
- `end_date` (Date) - Plan end date
- `goal_race_date` (Date) - Target race date
- `created_at`, `updated_at` (Timestamp)

Workouts:
- `id` (UUID) - Primary key
- `plan_id` (UUID) - Foreign key to training_plans
- `name` (String) - Workout name
- `workout_type` (Enum) - easy_run, tempo, intervals, long_run, etc.
- `description` (Text)
- `scheduled_date` (Date)
- `distance_km` (Decimal)
- `duration_minutes` (Integer)

Runs:
- `id` (UUID) - Primary key
- `workout_id` (UUID) - Foreign key to workouts
- `actual_date` (Date) - Date run was completed
- `distance_km` (Decimal)
- `duration_minutes` (Integer)
- `average_pace` (Decimal)
- `notes` (Text)

### API Endpoints

#### Training Plans
- `GET /api/v1/plans` - List all training plans (with pagination)
- `POST /api/v1/plans` - Create new training plan
- `GET /api/v1/plans/{id}` - Get plan by ID
- `PUT /api/v1/plans/{id}` - Update training plan
- `DELETE /api/v1/plans/{id}` - Delete training plan

#### Workouts
- `GET /api/v1/workouts` - List workouts (filterable by plan_id)
- `POST /api/v1/workouts` - Create new workout
- `GET /api/v1/workouts/{id}` - Get workout by ID
- `PUT /api/v1/workouts/{id}` - Update workout
- `DELETE /api/v1/workouts/{id}` - Delete workout

#### Runs
- `GET /api/v1/runs` - List completed runs
- `POST /api/v1/runs` - Record new run
- `GET /api/v1/runs/{id}` - Get run by ID
- `PUT /api/v1/runs/{id}` - Update run record
- `DELETE /api/v1/runs/{id}` - Delete run

#### Analytics
- `GET /api/v1/analytics/summary` - Get training summary statistics
- `GET /api/v1/analytics/plans/{id}/progress` - Get plan progress

#### Health
- `GET /health` - Service health check

### Features

- RESTful API design
- OpenAPI/Swagger documentation (`/docs`)
- Request validation with Pydantic
- Database connection pooling
- Structured logging
- Error handling and custom exceptions
- Unit and integration tests
- Docker containerization
- Database migrations with Alembic

### Running Locally

```bash
# From monorepo root
docker-compose up running-trainer

# Access API
curl http://localhost:8001/health

# View API docs
open http://localhost:8001/docs
```

### Testing

```bash
# Run all tests
make test

# Or directly
docker-compose exec running-trainer pytest

# Run specific test file
docker-compose exec running-trainer pytest tests/unit/test_plans.py
```

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `DEBUG` - Enable debug mode (True/False)
- `APP_NAME` - Application name for logging

---

## 2. Auth Service (Coming Soon)

**Port:** 8004
**Status:** Planned (Phase 2)
**Repository:** `services/auth/` (to be created)

### Description

Centralized authentication and authorization service providing user management, JWT token generation, and OAuth2 integration.

### Planned Features

- User registration and login
- Password hashing (bcrypt/argon2)
- JWT token generation and validation
- Token refresh and revocation
- Role-based access control (RBAC)
- OAuth2 integration (Google, Strava)
- Email verification
- Password reset functionality

### Technology Stack (Proposed)

- **Language:** Python 3.11 or Go
- **Framework:** FastAPI or Gin
- **Database:** PostgreSQL (users, roles, permissions)
- **Cache:** Redis (token blacklist, sessions)
- **Authentication:** JWT, OAuth2

### API Endpoints (Planned)

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout (blacklist token)
- `GET /auth/me` - Get current user
- `POST /auth/oauth/google` - Google OAuth login
- `POST /auth/oauth/strava` - Strava OAuth login

---

## 3. PDF Export Service (Coming Soon)

**Port:** 8002
**Status:** Planned (Phase 2)
**Repository:** `services/pdf/` (to be created)

### Description

Service for generating printable PDF training plans with custom templates and styling.

### Planned Features

- Generate training plan PDFs
- Custom templates (weekly, monthly views)
- Workout calendar visualization
- Progress tracking charts
- Custom branding/logos
- Email delivery integration
- S3/MinIO storage for generated PDFs

### Technology Stack (Proposed)

- **Language:** Python or Node.js
- **PDF Libraries:** ReportLab, WeasyPrint, or Puppeteer
- **Storage:** S3-compatible (MinIO, AWS S3)
- **Queue:** Redis/RabbitMQ for async generation

### API Endpoints (Planned)

- `POST /pdf/plans/{id}/generate` - Generate PDF for plan
- `GET /pdf/{pdf_id}` - Download generated PDF
- `GET /pdf/plans/{id}/status` - Check generation status

---

## 4. Strava Integration Service (Coming Soon)

**Port:** 8003
**Status:** Planned (Phase 2)
**Repository:** `services/strava/` (to be created)

### Description

Service for integrating with Strava API to sync activities, push workouts, and manage athlete data.

### Planned Features

- Strava OAuth authentication
- Import activities from Strava
- Push planned workouts to Strava calendar
- Sync athlete profile data
- Webhook handling for activity updates
- Activity matching (planned vs actual)
- Real-time activity notifications

### Technology Stack (Proposed)

- **Language:** Python or Node.js
- **Framework:** FastAPI or Express
- **Database:** PostgreSQL (Strava tokens, activity cache)
- **Queue:** Redis (webhook processing)
- **API:** Strava API v3

### API Endpoints (Planned)

- `GET /strava/auth` - Initiate OAuth flow
- `POST /strava/callback` - OAuth callback handler
- `GET /strava/activities` - List imported activities
- `POST /strava/sync` - Trigger activity sync
- `POST /strava/workouts/{id}/push` - Push workout to Strava
- `POST /strava/webhook` - Handle Strava webhooks

---

## 5. API Gateway (Coming Soon)

**Port:** 8000
**Status:** Planned (Phase 2)
**Repository:** `services/api-gateway/` (to be created)

### Description

Central entry point for all client requests, providing routing, authentication, rate limiting, and request transformation.

### Planned Features

- Request routing to backend services
- JWT authentication middleware
- Rate limiting (per user, per IP)
- Request/response logging
- CORS handling
- API versioning
- Request validation
- Circuit breaker pattern
- Load balancing

### Technology Stack (Proposed)

- **Option 1:** Kong API Gateway
- **Option 2:** Traefik
- **Option 3:** Custom FastAPI gateway
- **Cache/Rate Limit:** Redis

### Routes (Planned)

- `/api/v1/plans/*` → Running Trainer Service (8001)
- `/api/v1/workouts/*` → Running Trainer Service (8001)
- `/api/v1/runs/*` → Running Trainer Service (8001)
- `/api/v1/auth/*` → Auth Service (8004)
- `/api/v1/pdf/*` → PDF Service (8002)
- `/api/v1/strava/*` → Strava Service (8003)

---

## Service Communication Matrix

| From Service    | To Service      | Protocol | Purpose              |
|-----------------|-----------------|----------|----------------------|
| API Gateway     | Running Trainer | HTTP     | Route plan requests  |
| API Gateway     | Auth            | HTTP     | Validate tokens      |
| API Gateway     | PDF             | HTTP     | Route PDF requests   |
| API Gateway     | Strava          | HTTP     | Route Strava requests|
| PDF Service     | Running Trainer | HTTP     | Fetch plan data      |
| Strava Service  | Running Trainer | HTTP     | Create/update runs   |

---

## Database Strategy

### Current (Phase 1)
- Single PostgreSQL instance
- One database: `running_tracker_dev`
- All tables in one schema

### Future (Phase 2+)
**Option 1: Shared Database**
- One PostgreSQL instance
- Separate schemas per service
- Easier for small deployments

**Option 2: Database Per Service**
- Separate PostgreSQL instances
- True microservices isolation
- Better for production scaling
- Recommended for Phase 3+

---

## Testing Strategy

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Fast execution

### Integration Tests
- Test service with real database
- Test API endpoints end-to-end
- Docker-based test environment

### End-to-End Tests (Future)
- Test complete user flows
- Multiple services working together
- Selenium/Cypress for UI tests

---

## Monitoring & Logging

### Current (Phase 1)
- Basic structured logging
- Health check endpoint
- Docker logs

### Future (Phase 2+)
- Prometheus metrics on all services
- Grafana dashboards
- ELK/Loki for log aggregation
- Distributed tracing (Jaeger/Zipkin)
- Alert manager for critical issues

---

## References

- [Architecture Overview](./ARCHITECTURE.md)
- [Running Trainer API Docs](http://localhost:8001/docs)
- [Environment Configuration](../.env.example)

---
Last Updated: 2024-11-16
