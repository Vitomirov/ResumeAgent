.PHONY: help install dev start stop docker-up docker-down docker-build test lint

help:
	@echo "ResumeAgent — available targets:"
	@echo "  install      Install backend (uv) and frontend (npm) dependencies"
	@echo "  dev          Run backend and frontend locally (requires .env)"
	@echo "  start        Alias for dev"
	@echo "  stop         Stop local dev processes"
	@echo "  docker-up    Start services via Docker Compose"
	@echo "  docker-down  Stop Docker Compose services"
	@echo "  docker-build Rebuild Docker images"
	@echo "  test         Run backend tests"
	@echo "  lint         Run frontend lint"

install:
	@command -v uv >/dev/null 2>&1 || (echo "Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh" && exit 1)
	cd backend && uv sync --all-extras
	cd frontend && npm install

dev start:
	./scripts/start.sh

stop:
	./scripts/stop.sh

docker-up:
	docker compose up

docker-down:
	docker compose down

docker-build:
	docker compose build

test:
	cd backend && uv run pytest

lint:
	cd frontend && npm run lint
