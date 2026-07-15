# Nexus - Agent Guidelines

## Architecture
Meta-repository for a multi-tenant SaaS platform. **Each component is a git submodule:**

```
Nexus/                  # This repo — only docker-compose, CI, shared config
  backend/              # Git submodule: FastAPI + PostgreSQL + Redis
  frontend/             # Git submodule: Admin web UI (React/Vue)
  mobile/               # Git submodule: iOS/Android app (Swift)
```

- Never create application code at the root level. Always work inside the correct submodule.
- Root-level changes are limited to: `docker-compose.yml`, `.github/workflows/`, `Makefile`, `.env.example`, shared tooling configs.
- Multi-tenant: each company has isolated data. Tenant resolution via subdomain or header (`X-Tenant-ID`).

## Tech Stack
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Auth**: JWT (local bcrypt), role-based: Admin, Manager, Employee, Customer
- **Testing**: Pytest + pytest-cov + httpx (async), coverage threshold 80%
- **Linting**: ruff (`pyproject.toml` in backend), mypy strict mode
- **Package manager**: uv (never pip/poetry)
- **Infrastructure**: Docker Compose (dev), GitHub Actions (CI/CD)
- **Observability**: Prometheus metrics, Grafana dashboards, Sentry error tracking
- **Reverse proxy**: Traefik

## Build and Test
All commands run from the **backend submodule** directory:

```sh
# Install dependencies
uv sync

# Run all checks (lint + typecheck + test)
uv run ruff check . && uv run mypy . && uv run pytest -v --cov=app --cov-report=term-missing

# Run only tests
uv run pytest -v

# Build and run with Docker
docker compose up --build
```

## Conventions

### Code Style
- **English only** for code, comments, commits, and docs.
- **Type hints everywhere** — mypy strict mode enforced. No `Any` without explicit justification.
- **All API endpoints are `async def`** — use async SQLAlchemy, async Redis clients.
- **SOLID principles**: single-responsibility classes, dependency injection via FastAPI `Depends()`.
- **Domain-Driven Design**: organize by bounded context, not technical layer:
  ```
  app/
    auth/           # Authentication domain
    customers/      # Customer management domain
    companies/      # Tenant/company domain
    appointments/   # Scheduling domain
    jobs/           # Work order domain
    invoices/       # Billing domain
    users/          # User & role management
    notifications/  # Email/SMS/push domain
    files/          # File upload & storage domain
  ```

### Database
- SQLAlchemy 2.0 style: `mapped_column()`, `Mapped[]` type annotations, `select()` with `session.execute()`.
- Alembic migrations for all schema changes. Never modify tables manually.
- Every table includes `id` (UUID), `created_at`, `updated_at` columns.
- Audit logging: every mutation writes to `audit_logs` table (who, what, when, old/new values).

### Testing
- Test file mirrors source structure: `tests/auth/test_login.py` for `app/auth/`.
- Use `httpx.AsyncClient` with FastAPI `TestClient` override for integration tests.
- Use `pytest-asyncio` with `asyncio_mode = "auto"`.
- Mock external services (email, storage), never mock the database.

### Git
- **Git Flow** branching: `feature/*`, `release/*`, `hotfix/*`, `develop`, `main`.
- Commit messages: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`).
- No direct commits to `main` or `develop` -- always via PR.
- Pagination: cursor-based for lists, `limit` + `offset` query params.
- All list endpoints support `?search=`, `?sort_by=`, `?order=asc|desc`.
- Error responses follow RFC 7807 (Problem Details).

## Key Patterns
- **Repository pattern**: data access behind interfaces, injected via `Depends()`.
- **Unit of Work**: transactional boundaries for write operations.
- **Domain events**: for cross-boundary communication (e.g., `AppointmentCreated` -> notification).
- **Background tasks**: FastAPI `BackgroundTasks` for emails, PDF generation. Redis queue for heavier jobs.
- **Rate limiting**: Redis-based, per-tenant and per-endpoint.
