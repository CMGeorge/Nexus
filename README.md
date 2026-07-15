# Nexus SaaS

A production-ready multi-tenant SaaS platform for small businesses -- electricians, HVAC services, salons, restaurants -- to manage customers, appointments, teams, invoices, notifications, work history, and files. Built with AI-assisted software engineering at every layer.

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

## Project Structure (DDD)

The backend is organized by bounded context, not technical layer:

```
app/
├── auth/           # JWT, refresh tokens, password hashing
├── customers/      # Customer CRUD, search, history
├── companies/      # Tenant settings, branding, subscription
├── appointments/   # Scheduling, calendar, reminders
├── jobs/           # Work orders, status tracking
├── invoices/       # Invoices, PDF generation, payments
├── users/          # User management, roles, permissions
├── notifications/  # Email, SMS, push templates
├── files/          # Upload, storage, thumbnails
└── core/           # Shared: config, deps, middleware
```

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
# Install dependencies
cd backend && uv sync

# Run all checks
uv run ruff check . && uv run mypy . && uv run pytest -v --cov=app --cov-report=term-missing

# Docker
docker compose up --build
```

## Documentation

| Resource | Location |
|----------|----------|
| ADRs | [docs/adr/](docs/adr/) |
| API Contracts | [docs/contracts/](docs/contracts/) |
| Agent Guidelines | [AGENTS.md](AGENTS.md) |
| Agent Configurations | [.github/agents/](.github/agents/) |
| Redmine | [#57 nexus-saas](https://redmine.wesell.ro/projects/nexus-saas) |
