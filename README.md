# Running Trainer - Training Plan Management Platform

A comprehensive microservices-based platform for managing running training plans, workouts, and performance tracking.

## Overview

Running Trainer is a modular, scalable platform built with microservices architecture. It provides tools for runners and coaches to create training plans, track workouts, integrate with Strava, and generate printable training schedules.

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd running_tracker

# Copy environment configuration
cp .env.example .env

# Start all services
make up

# View logs
make logs

# Access the Running Trainer API
open http://localhost:8001/docs
```

That's it! The Running Trainer service is now available at `http://localhost:8001`.

## Services

### Currently Available

#### Running Trainer Service (Port 8001) - ✅ Complete
Core training plan management service providing CRUD operations for plans, workouts, and runs.

- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Repository**: `services/running-trainer/`

### Coming Soon

- **API Gateway** (Port 8000) - Central routing and authentication
- **PDF Export Service** (Port 8002) - Generate printable training plans
- **Strava Integration** (Port 8003) - Sync activities with Strava
- **Auth Service** (Port 8004) - User authentication and authorization

## Technologies

### Backend
- **Python 3.11** - Primary language
- **FastAPI** - Web framework
- **PostgreSQL 15** - Database
- **SQLAlchemy** - ORM
- **Docker & Docker Compose** - Containerization

### Testing
- **pytest** - Testing framework
- **httpx** - HTTP testing
- **pytest-asyncio** - Async testing

## Architecture

This is a monorepo containing multiple microservices:

```
running_tracker/
├── services/
│   ├── running-trainer/     # Core training plan service (Complete)
│   ├── auth/               # Authentication service (Planned)
│   ├── pdf/                # PDF generation service (Planned)
│   ├── strava/             # Strava integration (Planned)
│   └── api-gateway/        # API Gateway (Planned)
├── frontend/                # Frontend application (Future)
├── docker-compose.yml       # Service orchestration
├── Makefile                 # Development commands
└── docs/                    # Documentation
    ├── ARCHITECTURE.md      # Architecture overview
    └── SERVICES.md          # Service details
```

For detailed architecture information, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Available Commands

The project includes a Makefile for common operations:

```bash
make up        # Start all services
make down      # Stop all services
make logs      # Follow service logs
make rebuild   # Rebuild services without cache
make clean     # Stop services and remove volumes
make test      # Run tests
make ps        # Show running containers
```

## API Endpoints

### Running Trainer Service

#### Training Plans
- `POST /api/v1/plans` - Create training plan
- `GET /api/v1/plans` - List all plans
- `GET /api/v1/plans/{id}` - Get plan details
- `PUT /api/v1/plans/{id}` - Update plan
- `DELETE /api/v1/plans/{id}` - Delete plan

#### Workouts
- `POST /api/v1/workouts` - Create workout
- `GET /api/v1/workouts` - List workouts
- `GET /api/v1/workouts/{id}` - Get workout details
- `PUT /api/v1/workouts/{id}` - Update workout
- `DELETE /api/v1/workouts/{id}` - Delete workout

#### Runs
- `POST /api/v1/runs` - Log a run
- `GET /api/v1/runs` - List runs
- `GET /api/v1/runs/{id}` - Get run details
- `PUT /api/v1/runs/{id}` - Update run
- `DELETE /api/v1/runs/{id}` - Delete run

#### Analytics
- `GET /api/v1/analytics/summary` - Overall statistics
- `GET /api/v1/analytics/plans/{id}/progress` - Plan progress

For complete API documentation with interactive examples, visit http://localhost:8001/docs after starting the services.

## Environment Configuration

Key environment variables (see `.env.example` for full list):

```bash
# Database
DATABASE_URL=postgresql://tracker:tracker@localhost:5432/running_tracker_dev

# Application
LOG_LEVEL=INFO
DEBUG=False

# Security
JWT_SECRET=your-secret-key-change-in-production

# Integrations (Optional)
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
```

## Development

### Running Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs for specific service
docker-compose logs -f running-trainer

# Access database
docker-compose exec postgres psql -U tracker -d running_tracker_dev
```

### Running Tests

```bash
# Run all tests
make test

# Or directly with docker-compose
docker-compose exec running-trainer pytest

# Run specific test file
docker-compose exec running-trainer pytest tests/unit/test_plan_service.py

# Run with coverage
docker-compose exec running-trainer pytest --cov=app
```

### Adding a New Service

1. Create service directory: `services/your-service/`
2. Add `Dockerfile` and code
3. Update `docker-compose.yml` with new service
4. Update documentation in `docs/SERVICES.md`
5. Add service-specific tests

## Project Structure

### Monorepo Layout
```
running_tracker/
├── services/running-trainer/     # Running Trainer Service
│   ├── app/                      # Application code
│   │   ├── api/                  # API routes
│   │   ├── models/               # Database models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   ├── crud/                 # Database operations
│   │   └── main.py               # FastAPI app
│   ├── tests/                    # Test suite
│   ├── Dockerfile                # Container definition
│   └── requirements.txt          # Python dependencies
├── docker-compose.yml            # Service orchestration
├── Makefile                      # Development commands
└── .env.example                  # Environment template
```

## Health Checks

Check if services are running properly:

```bash
# Running Trainer service health
curl http://localhost:8001/health

# Expected response:
# {"status":"ok","service":"Running Trainer API","version":"v1","database":"connected"}
```

## Troubleshooting

### Services won't start
```bash
# Check service logs
docker-compose logs

# Rebuild containers
make rebuild

# Clean start (removes volumes)
make clean
make up
```

### Database connection errors
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Verify database exists
docker-compose exec postgres psql -U tracker -l
```

### Port conflicts
If port 8001 is already in use, modify `docker-compose.yml`:
```yaml
running-trainer:
  ports:
    - "8002:8000"  # Change 8001 to another port
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - System architecture and design
- [Service Details](docs/SERVICES.md) - Individual service documentation
- [API Documentation](http://localhost:8001/docs) - Interactive API docs (when running)

## Roadmap

### Phase 1 - Complete ✅
- Running Trainer core service
- PostgreSQL database
- Docker containerization
- Basic API endpoints
- Testing suite

### Phase 2 - In Progress
- Monorepo restructuring ✅
- Auth service
- PDF export service
- Strava integration service
- API Gateway

### Phase 3 - Planned
- Frontend application (React/Vue)
- Advanced analytics
- Coach portal
- Mobile apps
- Notification service

## Testing

The project includes comprehensive tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

## Contributing

1. Create feature branch from `phase-two`
2. Make changes with appropriate tests
3. Ensure all tests pass: `make test`
4. Update documentation
5. Submit pull request

## Contact

**Wagner Osborne** - wgosborne@outlook.com

## License

[Your License Here]

---

**Current Status**: Phase 2 - Monorepo restructuring complete, running-trainer service operational at port 8001
