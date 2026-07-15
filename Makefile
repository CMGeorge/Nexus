# Nexus SaaS — Development Makefile

.PHONY: help up down restart logs clean build test lint

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# ── Docker ──

up: ## Start all services
	docker compose up -d

up-build: ## Start all services with rebuild
	docker compose up -d --build

down: ## Stop all services
	docker compose down

down-clean: ## Stop all services and remove volumes (RESETS DATABASE)
	docker compose down -v

restart: ## Restart all services
	docker compose restart

logs: ## View all logs
	docker compose logs -f --tail=100

logs-api: ## View API logs only
	docker compose logs -f api

logs-pg: ## View PostgreSQL logs only
	docker compose logs -f postgres

# ── Backend ──

install: ## Install backend dependencies
	cd backend && uv sync

test: ## Run all tests with coverage
	cd backend && uv run pytest -v --cov=app --cov-report=term-missing

test-domain: ## Run tests for a specific domain (make test-domain DOMAIN=customers)
	cd backend && uv run pytest tests/$(DOMAIN)/ -v

lint: ## Run ruff linter
	cd backend && uv run ruff check .

typecheck: ## Run mypy type checker
	cd backend && uv run mypy .

check: lint typecheck test ## Run all quality checks (lint + typecheck + test)

# ── Database ──

migrate: ## Run Alembic migrations
	cd backend && uv run alembic upgrade head

migrate-create: ## Create a new Alembic migration (make migrate-create MSG="add customers table")
	cd backend && uv run alembic revision --autogenerate -m "$(MSG)"

migrate-rollback: ## Rollback last migration
	cd backend && uv run alembic downgrade -1

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U nexus -d nexus

redis-shell: ## Open Redis CLI
	docker compose exec redis redis-cli

# ── Deploy ──

deploy-beta: ## Deploy to beta (192.168.1.31:/home/projects/nexus.ro/beta)
	rsync -avz --delete ./ root@192.168.1.31:/home/projects/nexus.ro/beta/
	ssh root@192.168.1.31 "cd /home/projects/nexus.ro/beta && docker compose up -d --build"

deploy-stage: ## Deploy to staging (192.168.1.31:/home/projects/nexus.ro/stage)
	rsync -avz --delete ./ root@192.168.1.31:/home/projects/nexus.ro/stage/
	ssh root@192.168.1.31 "cd /home/projects/nexus.ro/stage && docker compose up -d --build"

deploy-live: ## Deploy to production (192.168.1.30:/mnt/hdd/proiecte/nexus.ro/live)
	rsync -avz --delete ./ root@192.168.1.30:/mnt/hdd/proiecte/nexus.ro/live/
	ssh root@192.168.1.30 "cd /mnt/hdd/proiecte/nexus.ro/live && docker compose up -d --build"

# ── Data ──

backup-db: ## Backup PostgreSQL database locally
	docker compose exec postgres pg_dump -U nexus nexus > backup_$$(date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore PostgreSQL from backup (make restore-db FILE=backup_20260715.sql)
	docker compose exec -T postgres psql -U nexus nexus < $(FILE)
