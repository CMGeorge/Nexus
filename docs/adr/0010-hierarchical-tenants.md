# ADR-0010: Hierarchical Multi-Tenancy (Institution → Branches)

## Status
Accepted

## Date
2026-07-16

## Context
The initial multi-tenant model assumed a flat structure: each tenant is an independent company with no hierarchy. However, the real-world use case requires **institutions with multiple branches/locations**, where:

- An **Institution** (top-level tenant) may have multiple **Branches** (sub-tenants)
- Institution-level users should see data across ALL their branches
- Branch-level users should ONLY see data for their specific branch
- Users belong to exactly one tenant (either an institution or a branch)

Example: "Spitalul Municipal" (institution) has "Locatia Nord" and "Locatia Sud" (branches). A regional manager sees both locations; a nurse at Locatia Nord only sees Locatia Nord.

## Decision
We will implement a **self-referencing hierarchical tenant model**:

### 1. Database: `tenants` table with `parent_id`

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES tenants(id),    -- NULL = top-level institution
    subdomain VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT no_self_parent CHECK (id != parent_id)
);
```

- `parent_id IS NULL` → Institution (root-level tenant)
- `parent_id IS NOT NULL` → Branch (child of an institution)
- Only ONE level of nesting: institutions have branches, branches do NOT have sub-branches (enforced by application logic)

### 2. API Layer: `X-Tenant-ID` + `X-Branch-ID`

| User Level | Token `tenant_id` | `X-Tenant-ID` behavior | `X-Branch-ID` |
|---|---|---|---|
| **Institution user** | Institution UUID | Header = institution UUID → queries include institution + all child branches | Optional: filter to a specific branch |
| **Branch user** | Branch UUID | Header = branch UUID → queries scoped ONLY to that branch | Ignored |

**Resolution logic** (in `get_current_tenant`):
1. Parse `X-Tenant-ID` from header (or subdomain)
2. Look up tenant row. If `parent_id IS NULL`, the user is institution-level → `get_current_tenant()` returns the institution UUID, and `get_accessible_tenants()` returns `[institution_id] + [all child branch IDs]`
3. If `parent_id IS NOT NULL` → `get_accessible_tenants()` returns `[branch_id]` only

### 3. Query Pattern: `tenant_id IN (:accessible_tenants)`

Every repository query filters by `tenant_id IN get_accessible_tenants()` instead of `tenant_id = :single_id`. For institution-level users, this expands to include all branches. For branch-level users, it's only their branch.

```python
# In dependency
async def get_accessible_tenant_ids(
    current_tenant: UUID = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
) -> list[UUID]:
    stmt = select(Tenant).where(Tenant.id == current_tenant)
    tenant = (await session.execute(stmt)).scalar_one()
    if tenant.parent_id is None:
        # Institution — include all children
        children = select(Tenant.id).where(Tenant.parent_id == tenant.id)
        result = await session.execute(children)
        return [tenant.id] + [row[0] for row in result]
    else:
        # Branch — only this branch
        return [tenant.id]
```

### 4. Tenant Model

```python
class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(...)
    name: Mapped[str] = mapped_column(String(255))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tenants.id"), nullable=True
    )
    subdomain: Mapped[str | None] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at/updated_at: ...
```

## Rationale

### Why self-referencing table, not separate tables?
- Simpler: one schema, one set of foreign keys
- `parent_id IS NULL` cleanly distinguishes institution vs branch
- Future-proof: if we need deeper nesting later, it's just more FK levels (though currently we enforce 2 levels in app logic)

### Why `X-Tenant-ID` + `X-Branch-ID`, not just `X-Tenant-ID`?
- Backward compatible: existing code that sets `X-Tenant-ID` still works
- `X-Branch-ID` is an optional filter for institution-level users who want to drill down
- Clear separation of concerns: "who are you" (X-Tenant-ID) vs "what scope do you want" (X-Branch-ID)

### Why `IN (:accessible_tenants)` instead of `OR parent_id = X`?
- More efficient: a single IN clause vs a subquery
- The dependency pre-resolves the accessible tenant list (cached per request)

## Consequences

### Positive
- Real-world institution/branch modeling is straightforward
- Institution-level users get automatic roll-up views
- Branch-level data isolation is guaranteed at the query level
- `X-Branch-ID` enables drill-down filtering without complex sub-queries

### Negative
- All repository queries must use `tenant_id IN (:ids)` instead of `tenant_id = :id` — a refactor of existing queries
- Institution-level users may see more data than expected (by design, but worth documenting)
- Application-level enforcement of max-depth=2 nesting requires validation on tenant creation

### Mitigations
- Base repository class provides `_tenant_filter()` helper, so individual repos don't repeat the pattern
- `get_accessible_tenant_ids()` dependency is cached per request (no N+1 lookups)
- In the future, if deeper nesting is needed, the `IN (:ids)` pattern already supports it

## Validation Plan

| Test | Expected Result |
|------|----------------|
| **Institution admin** (login as Instalatii Bucuresti admin, request appointments) | Sees all appointments from both branches (Sediu Central + Sector 3) |
| **Branch user** (login as Sediu Central employee, request appointments) | Sees only Sediu Central appointments; branch-2 data invisible |
| **Cross-branch isolation** (Branch-1 user sends `X-Branch-ID: branch-2`) | Request rejected with **HTTP 403**; `"detail": "Access denied to this branch"` |
| **Missing X-Branch-ID** (branch user omits header) | Defaults to user's assigned branch; no institution-level data leaked |
| **Hierarchical query** (`get_accessible_tenant_ids()` for institution user) | Returns `[inst-1, branch-1, branch-2]` — all accessible tenant IDs |
| **New branch creation** (institution admin creates Branch-3) | `parent_id` set correctly; child branch inherits institution settings; appears in accessible scope immediately |

If any test fails, this ADR must be reconsidered.

| Alternative | Rejected Because |
|---|---|
| Separate `institutions` and `branches` tables | More complex schema, duplicate columns, harder to query across levels |
| Keep flat tenants but add `X-Scope` header with list of IDs | Security risk: client controls scope. Server must resolve from token. |
| PostgreSQL Row-Level Security (RLS) | Our app runs as a single DB user; RLS at the SQL level adds complexity we don't need yet |
| Use `tenant_id` column + `branch_id` on every table | Two columns everywhere, double indexes, messy queries. Single hierarchical `tenant_id` is cleaner. |
