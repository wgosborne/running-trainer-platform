# ==============================================================================
# Running Trainer Monorepo - Makefile
# ==============================================================================
#
# Quick commands for managing the Running Trainer microservices
#
# ==============================================================================

.PHONY: help up down logs rebuild clean test ps

# Default target
help:
	@echo "Running Trainer Monorepo - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "  make up        - Start all services with docker-compose"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - Follow logs from all services"
	@echo "  make rebuild   - Rebuild all services (no cache)"
	@echo "  make clean     - Stop services and remove volumes"
	@echo "  make test      - Run tests in running-trainer service"
	@echo "  make ps        - Show running containers"
	@echo ""

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Follow logs from all services
logs:
	docker-compose logs -f

# Rebuild all services without cache
rebuild:
	docker-compose build --no-cache

# Stop services and remove volumes (clean slate)
clean:
	docker-compose down -v

# Run tests in running-trainer service
test:
	docker-compose exec running-trainer pytest

# Show running containers
ps:
	docker-compose ps
