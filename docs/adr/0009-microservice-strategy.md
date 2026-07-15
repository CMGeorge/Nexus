# ADR-0009: DDD Bounded Contexts as Microservice Decomposition

## Status
Accepted

## Date
2026-07-15

## Context
Nexus is designed with Domain-Driven Design (DDD) using bounded contexts. As the platform grows, we need a clear path from the modular monolith to independently deployable microservices. The question: can we decompose into microservices using DDD, and what's the migration path?

## Decision
**Yes. DDD bounded contexts ARE the microservice boundary.** Each context becomes an independent service with its own database, API, and event bus connectivity.

### Phase 1: Modular Monolith (Current)
```
┌─────────────────────────────────────┐
│           Traefik (API Gateway)      │
├─────────────────────────────────────┤
│           FastAPI App                │
│  ┌──────┐ ┌────────┐ ┌───────────┐  │
│  │ auth │ │customers│ │invoices   │  │
│  └──────┘ └────────┘ └───────────┘  │
│  ┌──────┐ ┌────────┐ ┌───────────┐  │
│  │ jobs │ │apptmts │ │notify     │  │
│  └──────┘ └────────┘ └───────────┘  │
├─────────────────────────────────────┤
│       PostgreSQL (shared DB)         │
└─────────────────────────────────────┘
```
- One deployable, one database
- Contexts communicate via direct imports + domain events (Redis pub/sub)
- Shared `core/` module for base models, deps, config

### Phase 2: Separate Schemas
- Each context gets its own PostgreSQL schema (`auth.`, `customers.`, `invoices.`, etc.)
- Alembic migrations per-schema
- No cross-schema foreign keys — reference by UUID only
- Repository pattern already enforces schema boundaries

### Phase 3: Separate Databases
- Each context gets its own PostgreSQL instance
- Domain events replace direct service calls for writes
- API calls for cross-context reads (with circuit breakers)
- PgBouncer per-service connection pool

### Phase 4: Full Microservices
```
                    ┌──────────────┐
                    │   Traefik     │
                    │ (API Gateway) │
                    └──┬──┬──┬──┬──┘
                       │  │  │  │
          ┌────────────┘  │  │  └────────────┐
          ▼               ▼  ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────────┐
    │ auth-svc │    │cust-svc  │    │ invoice-svc  │
    │ PG: auth │    │ PG: cust │    │ PG: invoice  │
    └────┬─────┘    └────┬─────┘    └──────┬───────┘
         │               │                 │
         └───────────────┼─────────────────┘
                         │
              ┌──────────┴──────────┐
              │   Redis Streams /    │
              │   RabbitMQ (events)  │
              └─────────────────────┘
```
- Each service independently deployable (Docker → k3s pods)
- Service-level rate limiting, auth, and monitoring
- Distributed tracing (Jaeger) for cross-service calls

## Rationale
- **DDD is purpose-built for this**: bounded contexts map 1:1 to microservices without re-architecture
- **Incremental migration**: any context can be extracted independently when it needs to scale
- **No shared database antipattern**: Phase 3 explicitly moves to per-service databases
- **Kubernetes-ready**: k3s (already planned for production) handles service discovery, scaling, health checks
- **Cost-efficient**: Not every context needs its own DB day one. Phased approach prevents over-engineering.

## Consequences

### Positive
- Clear migration path from monolith to microservices
- Each team can own a context end-to-end (code + database + deployment)
- Independent scaling: scale `appointments` without scaling `auth`
- Technology freedom: future contexts could use Go/Rust if needed

### Negative
- Cross-context queries become harder in Phase 3+ (no JOINs across services)
- Eventual consistency replaces ACID transactions across contexts
- More infrastructure complexity (service mesh, distributed tracing)
- Phase 4 requires DevOps maturity

## Alternatives Considered
| Alternative | Rejected Because |
|-------------|-----------------|
| Start as microservices | Premature — over-engineering for a new project. Modular monolith validates boundaries first. |
| Clean Architecture + services by layer | Layers don't map to business capabilities. Hard to split into services. |
| Monolith forever | SaaS with 9+ domains will outgrow a single deployable. Performance, team contention, deployment coupling. |

## Migration Triggers
Extract a context to its own service when:
1. **Scale**: Context has 10× traffic of other contexts
2. **Team**: A dedicated team owns the context
3. **Deployment**: Context changes independently from others
4. **Technology**: Context needs a different tech stack (e.g., Go for high-throughput)

## References
- ADR-0003: PostgreSQL Replication Strategy
- ADR-0007: Security Architecture
- [DDD & Microservices — Martin Fowler](https://martinfowler.com/bliki/BoundedContext.html)
- Redmine: #57 nexus-saas
