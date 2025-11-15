# Running Training Tracker API

A production-ready microservice for managing running training plans, workouts, and run tracking built with FastAPI and PostgreSQL.

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Server**: Uvicorn
- **Rate Limiting**: SlowAPI 0.1.9
- **Containerization**: Docker & Docker Compose
- **Python**: 3.11
- **Testing**: pytest, pytest-asyncio, httpx

## Features

### Core Functionality
- RESTful API for training plans, workouts, and runs
- Analytics and performance tracking
- Automatic OpenAPI documentation (Swagger UI & ReDoc)
- Comprehensive CRUD operations for all resources

### Production-Ready Features
- **Rate Limiting**: Per-endpoint rate limits to prevent abuse
- **Health Checks**: Database connectivity and service health monitoring
- **Structured Logging**: Console and file logging with configurable levels
- **Exception Handling**: Comprehensive error handling with meaningful responses
- **Middleware**: CORS, request size limiting, request logging
- **Database**: Connection pooling and health checks
- **Type Safety**: Full Pydantic validation and type hints
- **Testing**: Comprehensive unit and integration test suites

## Project Structure

```
polyglot-microservice/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── constants.py               # Application constants and enums
│   ├── exceptions.py              # Custom exception classes
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Main v1 router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── plans.py       # Training plan endpoints
│   │           ├── workouts.py    # Workout endpoints
│   │           ├── runs.py        # Run tracking endpoints
│   │           └── analytics.py   # Analytics endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Base model class
│   │   ├── plan.py                # TrainingPlan model
│   │   ├── workout.py             # Workout model
│   │   └── run.py                 # Run model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── plan.py                # Plan Pydantic schemas
│   │   ├── workout.py             # Workout Pydantic schemas
│   │   └── run.py                 # Run Pydantic schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── plan.py                # Plan database operations
│   │   ├── workout.py             # Workout database operations
│   │   └── run.py                 # Run database operations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── plan_service.py        # Plan business logic
│   │   ├── workout_service.py     # Workout business logic
│   │   ├── run_service.py         # Run business logic
│   │   └── analytics_service.py   # Analytics and statistics
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handler.py       # Global error handling
│   │   ├── request_context.py     # Request context management
│   │   └── security.py            # Security middleware
│   ├── health/
│   │   ├── __init__.py
│   │   ├── models.py              # Health check models
│   │   ├── checks.py              # Health check implementations
│   │   └── routes.py              # Health check endpoints
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── metrics.py             # Application metrics
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py            # Database connection and session
│   │   └── init_db.py             # Database initialization
│   └── utils/
│       ├── __init__.py
│       └── logger.py              # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Test configuration and fixtures
│   ├── fixtures/                  # Shared test fixtures
│   │   ├── __init__.py
│   │   ├── plans.py
│   │   ├── workouts.py
│   │   └── runs.py
│   ├── unit/                      # Unit tests
│   │   ├── __init__.py
│   │   ├── test_plan_service.py
│   │   ├── test_workout_service.py
│   │   ├── test_run_service.py
│   │   ├── test_analytics_service.py
│   │   └── test_validators.py
│   └── integration/               # Integration tests
│       ├── __init__.py
│       ├── test_plans_endpoints.py
│       ├── test_workouts_endpoints.py
│       ├── test_runs_endpoints.py
│       └── test_analytics_endpoints.py
├── docs/                          # Additional documentation
│   ├── DEPLOYMENT.md
│   ├── IMPLEMENTATION_GUIDE.md
│   └── PRODUCTION.md
├── logs/                          # Application logs (auto-created)
├── .env                           # Environment variables (create from .env.example)
├── .env.example                   # Environment variables template
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
# 1. Clone the repository
git clone <repository-url>
cd polyglot-microservice

# 2. Create environment file
cp .env.example .env

# 3. Start all services (PostgreSQL + API)
docker-compose up -d

# 4. Check if services are running
docker-compose ps

# 5. View logs
docker-compose logs -f api
```

The API will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Training Plans
- `POST /api/v1/plans` - Create a new training plan
- `GET /api/v1/plans` - List all training plans
- `GET /api/v1/plans/{plan_id}` - Get a specific plan
- `PUT /api/v1/plans/{plan_id}` - Update a plan
- `DELETE /api/v1/plans/{plan_id}` - Delete a plan

### Workouts
- `POST /api/v1/workouts` - Create a new workout
- `GET /api/v1/workouts` - List workouts (filterable by plan)
- `GET /api/v1/workouts/{workout_id}` - Get a specific workout
- `PUT /api/v1/workouts/{workout_id}` - Update a workout
- `DELETE /api/v1/workouts/{workout_id}` - Delete a workout

### Runs
- `POST /api/v1/runs` - Log a new run
- `GET /api/v1/runs` - List runs (filterable by workout/plan)
- `GET /api/v1/runs/{run_id}` - Get a specific run
- `PUT /api/v1/runs/{run_id}` - Update a run
- `DELETE /api/v1/runs/{run_id}` - Delete a run

### Analytics
- `GET /api/v1/analytics/summary` - Get overall statistics
- `GET /api/v1/analytics/plan/{plan_id}` - Get plan-specific analytics

All endpoints include rate limiting and comprehensive error handling. See interactive documentation at `/docs` for detailed schemas and examples.

## Local Development Setup

For local development without Docker:

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip

### Installation

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Update DATABASE_URL in .env to point to your local PostgreSQL
# Example: DATABASE_URL=postgresql://user:password@localhost:5432/running_tracker_dev
```

### Database Setup

```bash
# 1. Create PostgreSQL database
createdb running_tracker_dev

# 2. The application will automatically create tables on startup
```

### Running the Application

```bash
# Start the server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Configure the application using environment variables in `.env`:

### Database Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection URL | - | Yes |
| `MAX_POOL_SIZE` | Maximum database connections in pool | 20 | No |
| `POOL_RECYCLE` | Recycle connections after N seconds | 3600 | No |

### Logging Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO | No |
| `USE_JSON_LOGS` | Use JSON formatting for logs | true | No |

### Application Settings
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | Running Trainer API | No |
| `API_TITLE` | API title for OpenAPI docs | Running Training Tracker API | No |
| `API_VERSION` | API version | 1.0.0 | No |
| `API_DESCRIPTION` | API description | A production-ready microservice... | No |
| `DEBUG` | Enable debug mode | false | No |

### Security Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | * | No |

### Performance Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REQUEST_TIMEOUT` | Request timeout in seconds | 30 | No |
| `HEALTH_CHECK_INTERVAL` | Health check interval in seconds | 30 | No |

## API Documentation

Once the application is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Health Check

Check if the application and its dependencies are healthy:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "service": "Running Trainer API",
  "version": "1.0.0",
  "database": "connected"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Read operations** (GET): 100 requests per minute
- **Write operations** (POST, PUT, DELETE): 30 requests per minute

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

## Logging

The application logs to both console and file:

- **Console**: All logs are printed to stdout/stderr with color coding (development)
- **File**: `logs/app.log` (auto-rotated at 10MB, keeps 5 backups)
- **Format**: Configurable between human-readable and JSON (set `USE_JSON_LOGS`)

Log format: `[timestamp] [level] [module] message`

## Running Tests

The project includes comprehensive unit and integration tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_plan_service.py

# Run with verbose output
pytest -v
```

Test coverage includes:
- Service layer unit tests
- CRUD operation tests
- API endpoint integration tests
- Validation and error handling tests

## Docker Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Stop services and remove volumes (deletes database data)
docker-compose down -v

# Rebuild containers
docker-compose up -d --build

# Execute command in running container
docker-compose exec api python -m pytest

# Access database
docker-compose exec postgres psql -U tracker -d running_tracker_dev
```

## Development Workflow

1. Make changes to code in `app/` directory
2. If using Docker with volumes, changes are reflected immediately
3. If running locally with `--reload`, uvicorn automatically reloads
4. Check logs for any errors
5. Test endpoints using the Swagger UI at `/docs`
6. Run tests with `pytest` before committing

## Architecture

The application follows a layered architecture:

- **API Layer** (`app/api/v1/endpoints/`): FastAPI routes and endpoint handlers
- **Service Layer** (`app/services/`): Business logic and orchestration
- **CRUD Layer** (`app/crud/`): Database operations and queries
- **Model Layer** (`app/models/`): SQLAlchemy ORM models
- **Schema Layer** (`app/schemas/`): Pydantic models for validation and serialization

Additional components:
- **Middleware** (`app/middleware/`): Request/response processing, security
- **Health Checks** (`app/health/`): Service health monitoring
- **Monitoring** (`app/monitoring/`): Application metrics and observability

## Troubleshooting

### Database connection fails

- Check if PostgreSQL is running: `docker-compose ps`
- Verify DATABASE_URL in `.env` is correct
- Check logs: `docker-compose logs postgres`
- Ensure database exists: `docker-compose exec postgres psql -U tracker -l`

### Port 8000 already in use

- Change the port in `docker-compose.yml`: `"8001:8000"`
- Or stop the process using port 8000: `lsof -ti:8000 | xargs kill`

### Import errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

### Permission issues (Linux/macOS)

- Check file permissions for logs directory
- Ensure Docker has proper permissions
- Run with appropriate user permissions

### Rate limit errors

- Check rate limit headers in response
- Wait for rate limit window to reset
- Adjust rate limits in `app/constants.py` if needed for development

### Tests failing

- Ensure test database is set up correctly
- Check if all dependencies are installed: `pip install -r requirements.txt`
- Run tests with verbose output: `pytest -v`
- Check test logs for specific failures

## Contributing

1. Create a feature branch from `main`
2. Make changes with appropriate tests
3. Ensure all tests pass: `pytest`
4. Update documentation if needed
5. Submit pull request with clear description

## Production Deployment

For production deployment guidance, see:
- `docs/DEPLOYMENT.md` - Deployment strategies and best practices
- `docs/PRODUCTION.md` - Production readiness checklist
- `docs/IMPLEMENTATION_GUIDE.md` - Detailed implementation guide

Key production considerations:
- Set `DEBUG=false`
- Use `LOG_LEVEL=INFO` or `WARNING`
- Set `USE_JSON_LOGS=true`
- Configure specific `ALLOWED_ORIGINS` (not `*`)
- Use managed PostgreSQL service
- Implement Redis for rate limiting (instead of in-memory)
- Set up proper monitoring and alerting
- Use environment-specific secrets management

## Contact

Wagner Osborne - wgosborne@outlook.com
