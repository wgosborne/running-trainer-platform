# Running Trainer - Monorepo Architecture

## Overview

This monorepo contains all microservices for the Running Trainer platform - a comprehensive training plan management system for runners. The architecture follows microservices patterns with clear separation of concerns and independent service deployment.

## Monorepo Structure

```
running_tracker/
├── services/                    # Backend microservices
│   ├── running-trainer/        # Core training plan service (Phase 1 - COMPLETE)
│   ├── auth/                   # Authentication & authorization (Phase 2)
│   ├── pdf/                    # PDF export service (Phase 2)
│   ├── strava/                 # Strava integration service (Phase 2)
│   └── api-gateway/            # API Gateway & routing (Phase 2)
├── frontend/                    # React/Vue frontend (Future)
├── docker-compose.yml          # Multi-service orchestration
├── Makefile                    # Development commands
├── .env.example                # Environment configuration template
└── docs/                       # Documentation
    ├── ARCHITECTURE.md         # This file
    └── SERVICES.md             # Service details
```

## Microservices

### 1. Running Trainer Service (Port 8001)
**Status:** Complete (Phase 1)

The core service managing training plans, workouts, and runs.

**Responsibilities:**
- CRUD operations for training plans
- CRUD operations for workouts
- CRUD operations for runs
- Data persistence with PostgreSQL
- Business logic for training schedules

**Technology Stack:**
- Python 3.11
- FastAPI
- PostgreSQL 15
- SQLAlchemy (ORM)
- Alembic (migrations)

**API Endpoints:**
- `GET /health` - Health check
- `GET /api/v1/plans` - List training plans
- `POST /api/v1/plans` - Create training plan
- `GET /api/v1/plans/{id}` - Get plan details
- `PUT /api/v1/plans/{id}` - Update plan
- `DELETE /api/v1/plans/{id}` - Delete plan
- Similar endpoints for workouts and runs

### 2. Auth Service (Port 8004)
**Status:** Planned (Phase 2)

Centralized authentication and authorization service.

**Responsibilities:**
- User registration and login
- JWT token generation and validation
- Password hashing and verification
- Role-based access control (RBAC)
- OAuth2 integration (Google, Strava)

**Technology Stack:**
- Python/FastAPI or Go
- PostgreSQL (user database)
- Redis (token blacklist)
- JWT for authentication

### 3. PDF Export Service (Port 8002)
**Status:** Planned (Phase 2)

Service for generating PDF training plans.

**Responsibilities:**
- Generate printable training plan PDFs
- Template management
- Custom branding/styling
- Email delivery integration

**Technology Stack:**
- Python (ReportLab/WeasyPrint) or Node.js (Puppeteer)
- S3-compatible storage for PDFs

### 4. Strava Integration Service (Port 8003)
**Status:** Planned (Phase 2)

Service for Strava API integration.

**Responsibilities:**
- Strava OAuth authentication
- Sync activities from Strava
- Push workouts to Strava
- Fetch athlete data
- Webhook handling for activity updates

**Technology Stack:**
- Python/FastAPI or Node.js
- Redis (webhook queue)
- Strava API v3

### 5. API Gateway (Port 8000)
**Status:** Planned (Phase 2)

Central entry point for all client requests.

**Responsibilities:**
- Request routing to appropriate services
- Rate limiting
- Request/response transformation
- API versioning
- Authentication middleware
- CORS handling
- Request logging

**Technology Stack:**
- Kong, Traefik, or custom FastAPI gateway
- Redis (rate limiting)

## Database Architecture

### PostgreSQL (Port 5432)

**Schema: running_tracker_dev**

Tables:
- `training_plans` - Training plan metadata
- `workouts` - Individual workout definitions
- `runs` - Completed run records
- `users` - User accounts (Phase 2)
- `strava_tokens` - OAuth tokens (Phase 2)

## Service Communication

### Internal Communication
- Services communicate via HTTP REST APIs
- All services on shared Docker network (`app_network`)
- Service discovery via container names

### External Communication
- Clients connect through API Gateway (Port 8000)
- Direct service access available for development:
  - Running Trainer: `http://localhost:8001`
  - Auth: `http://localhost:8004`
  - PDF: `http://localhost:8002`
  - Strava: `http://localhost:8003`

## Port Allocation

| Service           | Port | Status      |
|-------------------|------|-------------|
| API Gateway       | 8000 | Planned     |
| Running Trainer   | 8001 | Complete    |
| PDF Export        | 8002 | Planned     |
| Strava Integration| 8003 | Planned     |
| Auth Service      | 8004 | Planned     |
| PostgreSQL        | 5432 | Complete    |
| Redis (Future)    | 6379 | Planned     |

## Deployment Strategy

### Development
- Docker Compose for local development
- Hot reload enabled for all services
- Shared PostgreSQL instance
- Volume mounts for live code updates

### Production (Future)
- Kubernetes deployment
- Separate databases per service (optional)
- Horizontal scaling for stateless services
- Managed PostgreSQL (RDS/CloudSQL)
- API Gateway with load balancing

## Security

### Authentication Flow
1. Client authenticates with Auth Service
2. Auth Service returns JWT token
3. Client includes JWT in all requests
4. API Gateway validates JWT
5. Gateway routes to appropriate service
6. Services trust gateway-validated requests

### Service-to-Service Auth
- Internal network isolation
- Optional: mTLS for service mesh
- Service accounts with limited permissions

## Monitoring & Observability

### Logging
- Structured JSON logging
- Centralized log aggregation (Future: ELK/Loki)
- Request ID tracing across services

### Metrics
- Prometheus metrics endpoints
- Grafana dashboards
- Key metrics: latency, error rate, throughput

### Health Checks
- `/health` endpoint on all services
- Database connectivity checks
- Dependency health validation

## Development Workflow

### Getting Started
```bash
# Clone repository
git clone <repo-url>
cd running_tracker

# Copy environment variables
cp .env.example .env

# Start all services
make up

# View logs
make logs

# Run tests
make test
```

### Adding a New Service
1. Create service directory in `services/`
2. Add Dockerfile
3. Update root `docker-compose.yml`
4. Update `docs/SERVICES.md`
5. Add to Makefile if needed

## Future Enhancements

### Phase 3+
- **Frontend Application** - React/Vue SPA
- **Mobile Apps** - React Native or Flutter
- **Notification Service** - Email/SMS/Push notifications
- **Analytics Service** - Training analytics and insights
- **Coach Portal** - Multi-athlete management
- **Payment Service** - Subscription management

### Infrastructure
- CI/CD pipeline (GitHub Actions)
- Kubernetes deployment
- Message queue (RabbitMQ/Kafka)
- Caching layer (Redis)
- CDN for static assets

## References

- [Service Details](./SERVICES.md)
- [API Documentation](http://localhost:8001/docs) (Running Trainer)
- [Environment Configuration](../.env.example)

---
Last Updated: 2024-11-16
