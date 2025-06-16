# Makefile for SwarmCraft

# Use .PHONY to ensure these commands run even if a file with the same name exists.
.PHONY: help setup up down build redis test test-integration test-all test-cov clean

# Default command to run when you just type "make"
help:
	@echo "Available commands:"
	@echo "  setup            - Install/sync all project dependencies using uv."
	@echo "  up               - Start all services (api, redis) with Docker Compose."
	@echo "  down             - Stop and remove all services."
	@echo "  build            - Rebuild the Docker images."
	@echo "  redis            - Start only the Redis container in the background."
	@echo "  test             - Run fast, local unit tests (no Redis required)."
	@echo "  test-integration - Run integration tests (requires Redis)."
	@echo "  test-all         - Run all tests (local and integration)."
	@echo "  test-cov         - Run all tests and generate a coverage report."
	@echo "  clean            - Remove temporary Python/test files."

# Project Setup
setup:
	uv sync

# Docker Compose Management
# We set COMPOSE_BAKE=true here to enable better build performance.
up:
	COMPOSE_BAKE=true docker compose up

down:
	docker compose down

build:
	COMPOSE_BAKE=true docker compose build

redis:
	docker compose up redis -d

# Testing
test:
	pytest

test-integration:
	pytest -m integration

test-all:
	pytest -m "integration or not integration"

test-cov:
	pytest -m "integration or not integration" --cov=src/swarmcraft --cov-report=term-missing

# Housekeeping
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f .coverage
	rm -rf .pytest_cache
	rm -rf htmlcov

