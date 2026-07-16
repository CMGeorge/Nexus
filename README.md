# Nexus SaaS

A production-ready multi-tenant SaaS platform for small businesses -- electricians, HVAC services, salons, restaurants -- to manage customers, appointments, teams, invoices, notifications, work history, and files. Built with AI-assisted software engineering at every layer.

> **Created by [WeSell.Solutions](https://wesell.ro)**

## Environments

All IPs, paths, ports, and credentials are defined in `.env` (never committed). Copy `.env.example` → `.env` and customize.

| Environment | Web App | API | Server | Path |
|-------------|---------|-----|--------|------|
| **Development** | localhost:${PORT_FRONTEND} | localhost:${PORT_API} | local | — |
| **Beta** | nexus-beta.wesell.ro | api-nexus-beta.wesell.ro | ${DEPLOY_HOST_BETA} | ${DEPLOY_PATH_BETA} |
| **Staging** | nexus-stage.wesell.ro | api-nexus-stage.wesell.ro | ${DEPLOY_HOST_STAGE} | ${DEPLOY_PATH_STAGE} |
| **Production** | nexus.wesell.ro | api-nexus.wesell.ro | ${DEPLOY_HOST_LIVE} | ${DEPLOY_PATH_LIVE} |

See `.env.example` for all 30+ configurable variables including ports, credentials, rate limits, and deploy targets.

## Architecture

Meta-repository with Git submodules -- each component is independently versioned:

```
Nexus/
├── backend/          # Git submodule: FastAPI + PostgreSQL + Redis
├── frontend/         # Git submodule: Admin web UI (React/Vue)
├── mobile/           # Git submodule: iOS/Android (Swift)
├── docs/
│   ├── adr/          # Architecture Decision Records
│   └── contracts/    # OpenAPI API contracts
├── .github/
│   ├── agents/       # Specialist AI agents (7 total)
│   ├── skills/       # Backend + Docker skills
│   ├── prompts/      # Task templates
│   └── hooks/        # Pre-commit validation
├── docker-compose.yml
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| **Database** | PostgreSQL 16 with Patroni HA + PgBouncer connection pooling |
| **Cache/Queue** | Redis 7 |
| **Auth** | JWT (bcrypt), role-based: Admin, Manager, Employee, Customer |
| **Testing** | Pytest + pytest-cov + httpx (async), 80%+ coverage threshold |
| **Linting** | ruff + mypy strict mode |
| **Package Manager** | uv |
| **Reverse Proxy** | Traefik |
| **Observability** | Prometheus, Grafana, Sentry |
| **Infrastructure** | Docker Compose (dev), k3s (production Phase 2) |
| **CI/CD** | GitHub Actions |

## High Availability & Disaster Recovery 🛡️

**RPO: < 1 minute | RTO: < 15 minutes**

Nexus is designed for zero data loss. The HA/DR strategy spans four layers:

### 1. Database Replication
- **Patroni + etcd** orchestrates PostgreSQL 16 with synchronous streaming replication
- **1 synchronous standby** (same DC) for zero-loss failover
- **1 asynchronous geo-replica** (separate DC) for site-level disaster recovery
- **PgBouncer** connection pooling with automatic failover routing

### 2. Automated Backups
- **pgBackRest**: daily full backups, 6-hour differentials, continuous WAL archiving (60s)
- **30-day local retention** on dedicated backup volume
- **Weekly offsite sync** to Backblaze B2 (immutable, versioned)
- **Point-in-time recovery** to any second within retention window

### 3. File Storage Redundancy
- **MinIO 4-node clusters** per datacenter with EC 4:2 erasure coding (tolerates 2 disk failures)
- **Cross-DC bucket replication** for uploaded documents, invoices, and images
- **S3-compatible API** -- drop-in migration path to AWS S3 if needed

### 4. Disaster Recovery Runbook
- **Scenario A**: Single node failure → Patroni automatic failover (< 30s)
- **Scenario B**: Primary DC partial outage → promote standby, redirect Traefik
- **Scenario C**: Full primary DC loss → promote geo-replica, DNS cutover
- **Scenario D**: Data corruption → pgBackRest PITR restore to point before corruption

```
                     DC-1 (Primary)
  ┌──────────────────────────────────────────┐
  │  Traefik HA  │  Patroni + PG 16          │
  │  (load bal.) │  ├─ Primary (r/w)         │
  │              │  ├─ Standby (sync rep.)   │
  │              │  └─ PgBouncer             │
  │              │                           │
  │  MinIO 4-Node Cluster (EC 4:2)          │
  │  pgBackRest → daily backup volume       │
  └──────────────┬───────────────────────────┘
                 │ async replication
  ┌──────────────┴───────────────────────────┐
  │              DC-2 (Geo-Replica)          │
  │  Traefik HA  │  PG Standby (async)       │
  │              │  MinIO 4-Node (replica)   │
  │              │  pgBackRest Repo          │
  └──────────────┬───────────────────────────┘
                 │ weekly sync
            Backblaze B2
         (immutable offsite)
```

See [docs/adr/](docs/adr/) for the full Architecture Decision Records:
- [ADR-0003](docs/adr/0003-postgresql-replication-strategy.md): PostgreSQL Replication Strategy
- [ADR-0004](docs/adr/0004-backup-strategy.md): Backup Strategy
- [ADR-0005](docs/adr/0005-file-storage-ha.md): File Storage HA
- [ADR-0006](docs/adr/0006-disaster-recovery-runbook.md): Disaster Recovery Runbook
- [ADR-0007](docs/adr/0007-security-architecture.md): Security Architecture — API Gateway, JWT, Rate Limiting, MFA
- [ADR-0008](docs/adr/0008-multi-factor-authentication.md): Multi-Factor Authentication — TOTP, Enrollment, Backup Codes

## AI-Driven Development

Nexus uses 7 specialist AI agents coordinated by an orchestrator through a structured pipeline:

| Phase | Agent | Role |
|-------|-------|------|
| 0. Track | Orchestrator | Create Redmine issue + task-packets |
| 1. Design | Architect | ADR, domain boundaries, API contracts, DB schema |
| 2. Build | API Designer + DB Migrator | Endpoints, schemas, Alembic migrations |
| 3. Test | Test Writer | Integration + unit tests, 80%+ coverage |
| 4. Review | Code Reviewer | SOLID, DDD, SQLAlchemy 2.0, tenant isolation |
| 5. Secure | Security Auditor | RBAC, JWT, rate limiting, tenant isolation |
| 6. Close | Orchestrator | Update Redmine, link task-packets |

## Design Quality 🎨

All UI work is filtered through **[Hallmark](https://github.com/Nutlope/hallmark)** — an anti-AI-slop design skill with **57 quality gates** that prevents AI-generated-looking interfaces. Hallmark ensures:
- **Structural variety** — two pages for different briefs feel like different sites, not color-swaps
- **20 themes** with distinct macrostructures (modern-minimal, atmospheric, editorial, etc.)
- **Custom mode** for creative briefs that don't fit catalog themes
- **Study verb** — extract design DNA from reference sites without pixel-cloning
- **Audit verb** — score existing UI against anti-patterns

Design follows the principle: *made, not generated*.

## Project Structure (DDD)

The backend uses **Domain-Driven Design (DDD)** with bounded contexts — NOT Clean Architecture.

**Why DDD?** Multi-tenant SaaS has natural business boundaries (customers, invoices, appointments). DDD maps each to an independent bounded context. This means:
- Tenant isolation is explicit at the architecture level, not buried in a repository layer
- Each context can be extracted into a microservice without re-architecture (see [ADR-0009](docs/adr/0009-microservice-strategy.md))
- Domain events handle cross-context communication (e.g., AppointmentCreated triggers Invoice)
- Repository + Dependency Injection patterns are used *within* contexts, not as a separate layer

**Microservice Path**: DDD's bounded contexts are the natural decomposition boundary for microservices. The platform follows a 4-phase migration: modular monolith → separate schemas → separate databases → full microservices on k3s.

```
app/
├── auth/           # JWT, refresh tokens, password hashing, MFA
├── customers/      # Customer CRUD, search, history
├── companies/      # Tenant settings, branding, subscription
├── appointments/   # Scheduling, calendar, reminders
├── jobs/           # Work orders, status tracking
├── invoices/       # Invoices, PDF generation, payments
├── users/          # User management, roles, permissions
├── notifications/  # Email, SMS, push templates
├── files/          # Upload, storage, thumbnails
└── core/           # Shared: config, deps, middleware, base models
```

Each context contains: `models.py`, `schemas.py`, `router.py`, `service.py`, `repository.py`, `deps.py`

## Redmine

All work tracked at [redmine.wesell.ro/projects/nexus-saas](https://redmine.wesell.ro/projects/nexus-saas):

```
Nexus SaaS (#57)
├── Backend API (#61)
├── Admin Portal (#59)
├── Mobile App (#60)
├── Infrastructure (#64)
├── Documentation (#63)
└── AI Engineering Playbook (#62)
```

## Build & Test

```sh
# First time setup
cp .env.example .env        # Customize ports, credentials, paths
make up                     # Start all services
make install                # Install backend dependencies

# Development workflow
make check                  # ruff + mypy + pytest
make test                   # Run tests with coverage
make migrate                # Apply database migrations

# Docker
make up-build               # Rebuild and start
make logs                   # Tail all service logs
make down-clean             # Stop and reset database

# Deploy
make start-beta             # Deploy + start beta (rsync + docker compose up)
make start-stage            # Deploy + start staging
make restart-live           # Restart production (no rsync)
```

All IPs, ports, and credentials are in `.env` — never committed to Git.

## Security 🔐

Nexus implements defense-in-depth across all layers, aligned with the OWASP API Security Top-10.

### Authentication & Authorization
| Control | Implementation |
|---|---|
| **Authentication** | JWT: access tokens (15 min) + refresh tokens (7 days) with rotation and Redis blacklisting |
| **Multi-Factor Auth** | TOTP (RFC 6238) primary, email OTP fallback, backup codes, remember-device (30 days) |
| **Role-Based Access** | Four roles (Admin, Manager, Employee, Customer) embedded in JWT claims |
| **Tenant Isolation** | Every query filtered by `tenant_id` — zero cross-tenant data access |
| **Password Policy** | bcrypt hashing, minimum 12 characters, complexity enforcement |

### Attack Surface Protection
| Control | Implementation |
|---|---|
| **API Gateway** | Traefik reverse proxy — single entry point, frontend never touches the database |
| **Rate Limiting** | Redis sliding window: per-tenant + per-endpoint, tiered by subscription |
| **SQL Injection** | SQLAlchemy 2.0 ORM exclusively — parameterized queries, no raw SQL |
| **Input Validation** | Pydantic v2 strict mode on all request/response schemas |
| **CORS & Headers** | Traefik middleware: HSTS, CSP, X-Content-Type-Options, X-Frame-Options |
| **HTTPS** | Traefik TLS termination, Let's Encrypt auto-renewal, TLS 1.2+ only |
| **Secrets** | Docker secrets / environment variables — never in code, config, or logs |

### Rate Limiting Tiers
| Tier | Auth Endpoints | CRUD Endpoints | File Uploads |
|---|---|---|---|
| Free | 30 req/min | 200 req/min | 10 req/min |
| Pro | 100 req/min | 1,000 req/min | 50 req/min |
| Enterprise | 300 req/min | 5,000 req/min | 200 req/min |

### Audit & Compliance
- **Audit Logging**: Every mutation writes to `audit_logs` (who, what, when, old/new values)
- **Error Handling**: RFC 7807 Problem Details — no stack traces in production
- **Dependency Scanning**: GitHub Dependabot + `uv lock --check` in CI
- **Observability**: Prometheus metrics, Grafana dashboards, Sentry error tracking

See [ADR-0007](docs/adr/0007-security-architecture.md) and [ADR-0008](docs/adr/0008-multi-factor-authentication.md) for full security architecture decisions.

## Documentation

| Resource | Location |
|----------|----------|
| ADRs | [docs/adr/](docs/adr/) |
| API Contracts | [docs/contracts/](docs/contracts/) |
| User Stories | [docs/user-stories.md](docs/user-stories.md) (59 stories, 10 domains) |
| Agent Guidelines | [AGENTS.md](AGENTS.md) |
| Agent Configurations | [.github/agents/](.github/agents/) |
| Redmine | [#57 nexus-saas](https://redmine.wesell.ro/projects/nexus-saas) |
