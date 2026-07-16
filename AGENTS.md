# Nexus - Agent Guidelines

> Created by **WeSell.Solutions** — https://wesell.ro

## Platform Structure (3 Parts)

Nexus is a **business operations platform** with three distinct interfaces:

| Part | Users | Purpose |
|---|---|---|
| **Main App** | Business owners, managers, employees | Day-to-day operations: appointments, tasks, team, chat, invoices |
| **Client Portal** | End customers of the businesses | Self-service: book appointments, view invoices, chat, loyalty points |
| **Admin Panel** | WeSell platform admins | Cross-tenant: dashboards, reports, company settings, logs |

## Architecture
Monorepo for a multi-tenant SaaS platform (see ADR-0011).

```
Nexus/                  # Single repo — all components together
  backend/              # FastAPI + PostgreSQL + Redis (DDD)
  frontend/             # Admin web UI (React/Vue) — TBD
  desktop/              # Qt/QML desktop app (MVVM, C++17)
  mock/                 # Static HTML mock for beta validation (ADR-0012)
  mobile/               # iOS (SwiftUI) + Android (Kotlin)
    ios/                #   iOS: Clean Architecture, Swift 6, async/await
    android/            #   Android: Clean Architecture, Compose, Hilt
```

- Root-level changes are limited to: `docker-compose.yml`, `.github/workflows/`, `Makefile`, `.env.example`, shared tooling configs.
- Multi-tenant: each company has isolated data. Tenant resolution via subdomain or header (`X-Tenant-ID`).
- **Hierarchical tenants** (ADR-0010): Institutions can have multiple Branches. Institution users see all branches; branch users see only their branch. Uses `X-Tenant-ID` + optional `X-Branch-ID` header.
- **Architecture pattern**: Domain-Driven Design (DDD) with bounded contexts, NOT Clean Architecture.
- **Microservice-ready**: each bounded context can be extracted into an independent service with its own database (see ADR-0009).
- **Design quality**: use `hallmark` skill (57 slop-test gates) for all UI work — prevents AI-generated-looking designs.

### Why DDD, Not Clean Architecture

| | Clean Architecture | DDD (our choice) |
|---|---|---|
| **Organized by** | Technical layers (entities → use cases → adapters → frameworks) | Business domains (auth, customers, invoices, etc.) |
| **Best for** | Single-domain apps with deep business rules | Multi-domain SaaS with cross-context communication |
| **Multi-tenant** | Tenant logic scattered across layers | Tenant boundary is a first-class context (companies/) |
| **Microservice path** | Requires re-architecture | Each bounded context can be extracted independently |
| **Team alignment** | Teams organized by layer (backend team, frontend team) | Teams own entire contexts (auth team, billing team) |
| **Cross-cutting** | Difficult — spans all layers | Domain events for cross-context communication |

Clean Architecture creates unnecessary indirection for a multi-domain SaaS. DDD's bounded contexts map directly to business capabilities and make tenant isolation explicit at the architecture level.

> **Note on mobile apps**: iOS and Android use **Clean Architecture** (not DDD) because they are client-side apps — they don't own business logic, they consume the backend API. The backend's DDD bounded contexts map naturally to Clean Architecture domain layers in mobile.

> **Note on desktop app**: The Qt/QML desktop app uses **MVVM** (Model-View-ViewModel) because Qt's `Q_PROPERTY` + signal/slot system is purpose-built for MVVM data binding. QML Views declaratively bind to C++ ViewModels, which call Repository classes that consume the REST API. No need for controllers — QML handles user input directly.

## Tech Stack
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Auth**: JWT (local bcrypt), role-based: Admin, Manager, Employee, Customer
- **eFactura**: Romanian national e-invoicing (CIUS-RO XML, ANAF SPV integration)
- **iOS App**: Swift 6, SwiftUI, Clean Architecture, async/await, SPM, Swift Testing
- **Android App**: Kotlin 2.x, Jetpack Compose, Clean Architecture, Coroutines/Flow, Hilt, Gradle KTS
- **Desktop App**: Qt 6.11 LTS, QML, C++17, MVVM, CMake, Qt Network, SQLite (ADR-0013)
- **Testing**: Pytest + pytest-cov + httpx (async), coverage threshold 80%
- **Linting**: ruff (`pyproject.toml` in backend), mypy strict mode
- **Package manager**: uv (never pip/poetry)
- **Infrastructure**: Docker Compose (dev), GitHub Actions (CI/CD)
- **Observability**: Prometheus metrics, Grafana dashboards, Sentry error tracking
- **Reverse proxy**: Traefik
- **Project Management**: Redmine (project #57 nexus-saas at redmine.wesell.ro)

### Redmine Structure
Redmine mirrors the git submodule architecture with subprojects:

```
Nexus SaaS (#57)              # Parent: epics, cross-cutting features
├── Backend API (#61)         # DDD modules as categories: Auth, Customers, Companies, etc.
├── Admin Portal (#59)        # React/Vue frontend issues
├── Mobile App (#60)          # iOS/Android issues
├── Infrastructure (#64)      # Docker, Traefik, CI/CD, monitoring
├── Documentation (#63)       # ADRs, contracts, architecture docs
└── AI Engineering Playbook (#62)  # Agents, skills, prompts -- "how we build"
```

- DDD modules (Auth, Customers, Invoices, etc.) are **categories** within Backend API, not separate projects
- Cross-cutting features create the epic in the parent project; task-packets go to the relevant subproject

## Development Practices

### Redmine Tracking
All work is tracked in Redmine project **#57 (nexus-saas)**. Every feature:
- Has a Redmine issue before code is written
- Is broken into task-packets (child issues for Design, Build, Test, Review, Secure phases)
- Links commits via conventional commits: `feat(auth): add JWT refresh #123`
- Is resolved when all task-packets are complete
- Epics/cross-cutting features go in the parent project (#57)
- Task-packets target the appropriate subproject (Backend API, Admin Portal, etc.)

### ADR (Architecture Decision Records)
Significant architectural decisions are documented in `docs/adr/`:
- Format: `NNNN-title-with-dashes.md`
- Template: `docs/adr/template.md`
- When to create: new domain boundaries, technology choices, API patterns, data modeling decisions
- The architect agent produces ADRs; the orchestrator ensures they're committed

### Task-Packets
Features are decomposed into structured task-packets:
- Each packet = one phase (Design, Build, Test, Review, Secure)
- Contains: goal, acceptance criteria, estimated hours, dependencies
- Created as Redmine child issues under the feature issue
- Use `/task-packet` prompt to generate
- Each task-packet maps to one or more user stories from `docs/user-stories.md`

### Contract-First API Design
API endpoints follow contract-first development:
- Contract YAML written in `docs/contracts/{domain}.yaml` before implementation
- Pydantic schemas validate against the contract
- Contracts are the source of truth for integration tests
- The api-designer agent produces contracts; implementation follows the contract

### Mock-First Validation (ADR-0012)
Before building the real admin portal, we validate workflows with a static HTML mock:
- **Deploy**: `make deploy-mock-beta` → live at beta:3701
- **Test**: Share URL with business owners, watch them use it
- **Iterate**: Edit `mock/public/`, redeploy, repeat
- **Confirm**: Once workflows are validated, build the real app
- **Throw away**: Mock is disposable — no shared code with the real app
- Mock covers 3 personas: Business Owner (Admin), Manager, Technician

### Documentation Standards (CRITICAL)
Nexus is **polished, professional software**. Every piece of work must be crystal clear:

- **Every idea → ADR**: Architecture decisions are documented with rationale, alternatives, and consequences
- **Every API → Contract**: Endpoints are defined in `docs/contracts/{domain}.yaml` before a single line of code. Contracts include request/response examples, error codes, and auth requirements.
- **Every domain → Domain Doc**: Each bounded context has a `docs/domains/{domain}.md` explaining its purpose, entities, relationships, and business rules.
- **Every endpoint → Docstring**: Router functions have docstrings explaining what they do, what they return, and what errors they produce.
- **Every schema → Field descriptions**: Pydantic models use `Field(description="...")` — never leave a field unexplained.
- **Code is self-documenting**: Meaningful variable names, small functions, clear error messages. Comments explain WHY, not WHAT.
- **Romanian market requirement**: All user-facing strings and documentation should be available in Romanian (ro-RO). Internal code/comments stay in English.

### eFactura Romania Integration (MANDATORY)
Nexus MUST integrate with **eFactura** (Romanian national e-invoicing system):

- **What**: ANAF (Romanian tax authority) requires B2B invoices to be submitted via eFactura XML format (UBL 2.1 / CIUS-RO standard)
- **When**: Mandatory for all B2B transactions in Romania since January 2024
- **How**: Invoices generated in Nexus are automatically:
  1. Created as standard invoice in the system
  2. Converted to CIUS-RO XML format
  3. Submitted to ANAF via eFactura API (SPV — Spațiul Privat Virtual)
  4. Status tracked (submitted, accepted, rejected, downloaded by buyer)
- **Architecture**: The `invoices/` bounded context has an `efactura/` sub-module handling XML generation and ANAF communication
- **Integration points**:
  - Invoice creation → auto-triggers eFactura submission
  - Invoice status → synced with ANAF response
  - Company settings → ANAF certificate upload (digital signing required)
  - Dashboard → eFactura status overview (submitted today, pending, rejected)

### Software Quality Standards
Every line of code must reflect that Nexus is **production-grade, not a prototype**:

| Standard | Rule |
|---|---|
| **Type safety** | mypy `strict` mode — no `Any` without justification |
| **Test coverage** | ≥ 80% per domain, integration tests for all endpoints |
| **Error handling** | Every endpoint returns proper RFC 7807 responses. No bare 500s. |
| **Multi-tenant isolation** | Every query scoped by tenant. Zero cross-tenant data leaks. |
| **API consistency** | Pagination, filtering, sorting identical across all list endpoints |
| **Security** | OWASP Top-10 reviewed before merge. MFA for all roles. |
| **Observability** | Prometheus metrics, structured logging, request IDs on every response |
| **Design** | hallmark skill (57 gates) applied to all UI. No AI-slop looks. |
| **Mobile quality** | iOS Human Interface Guidelines + Material Design 3. Native feel, not web-wrapper. |
| **Accessibility** | WCAG AA for admin portal. VoiceOver/TalkBack for mobile apps. |
- Mock covers 3 personas: Business Owner (Admin), Manager, Technician

### AI Agent Tool Usage Rules
- **NEVER write files via shell commands** — no `cat`, `echo`, `tee`, `python3 -c "...write..."`, heredocs (`<< 'EOF'`), or redirects (`>`) to create or modify files. Use VS Code editing tools only (`replace_string_in_file`, `multi_replace_string_in_file`).
- **Terminal is for build/run/test only** — `uv sync`, `uv run pytest`, `docker compose up`, `make`, etc. Not for writing code.
- **Reason**: Shell-written files are frequently corrupted by terminal output processing. VS Code editing tools write directly to disk and are reliable.

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
    invoices/       # Billing domain (includes eFactura sub-module)
    chat/           # Internal team chat + customer messaging
    tasks/          # Internal task management
    loyalty/        # Loyalty points + referral program
    website/        # Website provisioning for clients
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

## Documentation Structure
```
docs/
  adr/              # Architecture Decision Records
    template.md      # ADR template
    0001-auth-strategy.md
    0002-multi-tenant-model.md
  contracts/         # API contracts (OpenAPI YAML)
    auth.yaml
    customers.yaml
  architecture.md    # High-level architecture overview
```

## Key Patterns
- **Repository pattern**: data access behind interfaces, injected via `Depends()`.
- **Unit of Work**: transactional boundaries for write operations.
- **Domain events**: for cross-boundary communication (e.g., `AppointmentCreated` -> notification).
- **Background tasks**: FastAPI `BackgroundTasks` for emails, PDF generation. Redis queue for heavier jobs.
- **Rate limiting**: Redis-based, per-tenant and per-endpoint.
