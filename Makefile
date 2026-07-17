# Nexus SaaS — Development Makefile
# All deployment paths/credentials from .env
# Copy .env.example → .env and customize before use

include .env

.PHONY: help up down restart logs clean build test lint

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# ── Docker ──

up: ## Start all services (base compose — infra + api)
	docker compose --env-file .env up -d --build

up-dev: ## Start with dev overlay (exposed ports, hot-reload, no frontend)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env up -d --build

up-full: ## Start everything including frontend (requires frontend/ submodule)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile full --env-file .env up -d --build

up-build: ## Start all services with rebuild
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env up -d --build

up-base: ## Start infrastructure only (postgres, redis, pgadmin, mailpit)
	docker compose --env-file .env up -d

down: ## Stop all services
	docker compose down

down-clean: ## Stop and remove volumes (RESETS DATABASE)
	docker compose down -v

restart: ## Restart all services
	docker compose restart

logs: ## View all logs
	docker compose logs -f --tail=100

logs-api: ## View API logs only
	docker compose logs -f api

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

check: lint typecheck test ## Run all quality checks

# ── Database ──

migrate: ## Run Alembic migrations
	cd backend && uv run alembic upgrade head

migrate-create: ## Create migration (make migrate-create MSG="add customers table")
	cd backend && uv run alembic revision --autogenerate -m "$(MSG)"

migrate-rollback: ## Rollback last migration
	cd backend && uv run alembic downgrade -1

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

redis-shell: ## Open Redis CLI
	docker compose exec redis redis-cli

# ── Deploy ──
# Uses DEPLOY_USER_* from .env; falls back to current user ($USER) if not set

deploy-beta: ## Deploy to beta (rsync + pull + start)
	rsync -avz --delete ./ $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA):$(DEPLOY_PATH_BETA) --exclude='backend/' --exclude='frontend/' --exclude='mobile/' --exclude='.git/'
	ssh $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA) "cd $(DEPLOY_PATH_BETA) && docker compose --env-file .env pull && docker compose --env-file .env up -d"

deploy-mock-beta: ## Deploy mock Admin Portal to beta (ADR-0012)
	rsync -avz --delete ./mock/ $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA):$(DEPLOY_PATH_BETA)/mock/
	ssh $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA) "cd $(DEPLOY_PATH_BETA) && docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env up -d --build mock"

deploy-mock-client-portal: ## Deploy mock Client Portal to beta
	rsync -avz --delete ./mock/client-portal/ $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA):$(DEPLOY_PATH_BETA)/mock/client-portal/
	ssh $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA) "cd $(DEPLOY_PATH_BETA) && docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env up -d --build client-portal"

deploy-mock-admin-panel: ## Deploy mock Admin Panel to beta
	rsync -avz --delete ./mock/admin-panel/ $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA):$(DEPLOY_PATH_BETA)/mock/admin-panel/
	ssh $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA) "cd $(DEPLOY_PATH_BETA) && docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env up -d --build admin-panel"

deploy-stage: ## Deploy to staging (rsync + pull + start)
	rsync -avz --delete ./ $(or $(DEPLOY_USER_STAGE),$$USER)@$(DEPLOY_HOST_STAGE):$(DEPLOY_PATH_STAGE) --exclude='backend/' --exclude='frontend/' --exclude='mobile/' --exclude='.git/'
	ssh $(or $(DEPLOY_USER_STAGE),$$USER)@$(DEPLOY_HOST_STAGE) "cd $(DEPLOY_PATH_STAGE) && docker compose --env-file .env pull && docker compose --env-file .env up -d"

deploy-live: ## Deploy to production (rsync + pull + start)
	rsync -avz --delete ./ $(or $(DEPLOY_USER_LIVE),$$USER)@$(DEPLOY_HOST_LIVE):$(DEPLOY_PATH_LIVE) --exclude='backend/' --exclude='frontend/' --exclude='mobile/' --exclude='.git/'
	ssh $(or $(DEPLOY_USER_LIVE),$$USER)@$(DEPLOY_HOST_LIVE) "cd $(DEPLOY_PATH_LIVE) && docker compose --env-file .env pull && docker compose --env-file .env up -d"

start-beta: deploy-beta ## Alias: deploy + start beta
start-stage: deploy-stage ## Alias: deploy + start staging
start-live: deploy-live ## Alias: deploy + start production

restart-beta: ## Restart beta containers (no rsync)
	ssh $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA) "cd $(DEPLOY_PATH_BETA) && docker compose --env-file .env restart"

restart-stage: ## Restart staging containers (no rsync)
	ssh $(or $(DEPLOY_USER_STAGE),$$USER)@$(DEPLOY_HOST_STAGE) "cd $(DEPLOY_PATH_STAGE) && docker compose --env-file .env restart"

restart-live: ## Restart production containers (no rsync)
	ssh $(or $(DEPLOY_USER_LIVE),$$USER)@$(DEPLOY_HOST_LIVE) "cd $(DEPLOY_PATH_LIVE) && docker compose --env-file .env restart"

stop-beta: ## Stop beta containers
	ssh $(or $(DEPLOY_USER_BETA),$$USER)@$(DEPLOY_HOST_BETA) "cd $(DEPLOY_PATH_BETA) && docker compose down"

stop-stage: ## Stop staging containers
	ssh $(or $(DEPLOY_USER_STAGE),$$USER)@$(DEPLOY_HOST_STAGE) "cd $(DEPLOY_PATH_STAGE) && docker compose down"

stop-live: ## Stop production containers
	ssh $(or $(DEPLOY_USER_LIVE),$$USER)@$(DEPLOY_HOST_LIVE) "cd $(DEPLOY_PATH_LIVE) && docker compose down"

# ── Data ──

# ── E2E Tests (Playwright) ──
test-e2e: ## Run Playwright end-to-end tests against mock services
	@echo "Starting mock services..."
	docker compose -f docker-compose.yml up -d --build mock client-portal admin-panel
	@sleep 2
	cd tests/e2e && npm ci --silent && npx playwright test

test-e2e-main: ## Run only Main App e2e tests
	cd tests/e2e && npx playwright test --project=main-app

test-e2e-client: ## Run only Client Portal e2e tests
	cd tests/e2e && npx playwright test --project=client-portal

test-e2e-admin: ## Run only Admin Panel e2e tests
	cd tests/e2e && npx playwright test --project=admin-panel

test-e2e-headed: ## Run e2e tests in headed mode (see browser)
	cd tests/e2e && npx playwright test --headed

test-e2e-debug: ## Run e2e tests in debug mode (step-by-step)
	cd tests/e2e && npx playwright test --debug

test-e2e-report: ## Open Playwright HTML report
	cd tests/e2e && npx playwright show-report

test-e2e-install: ## Install Playwright browsers
	cd tests/e2e && npm ci && npx playwright install --with-deps chromium

backup-db: ## Backup PostgreSQL database locally
	docker compose exec postgres pg_dump -U $(POSTGRES_USER) $(POSTGRES_DB) > backup_$$(date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore from backup (make restore-db FILE=backup_20260715.sql)
	docker compose exec -T postgres psql -U $(POSTGRES_USER) $(POSTGRES_DB) < $(FILE)
