# ADR-0014: Customers Domain Design

## Status
Proposed

## Date
2026-07-17

---

## Context

Redmine epic #542. The Customers bounded context manages the **end-customers of a tenant's business** — the people who receive services, have appointments, get invoiced, and interact via the client portal. These are NOT platform users (that's the `auth` domain); they are the tenant's own client base.

### Existing Foundation
- **Auth domain** implemented: `users` table with `tenant_id`, JWT with role claims (`Admin`, `Manager`, `Employee`, `Customer`), MFA support
- **Hierarchical tenants** (ADR-0010): Institution → Branch. Institution-level users see all branches; branch users see only their branch.
- **DDD bounded contexts** (ADR-0009): Each context maps to a microservice boundary.
- **Monorepo** (ADR-0011): All components in one repo.

### Requirements (from user-stories.md)
| ID | Story | Role | Priority |
|----|-------|------|----------|
| CUST-01 | Create customer (name, email, phone, address) | Employee+ | P0 |
| CUST-02 | Search customers by name, email, phone | Employee+ | P0 |
| CUST-03 | View customer full history (appointments, jobs, invoices, files) | Employee+ | P1 |
| CUST-04 | Edit customer info | Employee+ | P0 |
| CUST-05 | Add notes to customer profile | Employee+ | P2 |
| CUST-06 | Import customers from CSV | Manager+ | P2 |

---

## Decision

### 1. Customers is its own Bounded Context

Customers do **not** belong to any existing context:

| Would it fit in... | Why not |
|---|---|
| `auth` | Auth manages platform users (login, JWT, MFA). Customers don't log in. |
| `companies` | Companies manages tenant configuration. Customers are the tenant's operational data. |
| `users` | Users manages platform user profiles and roles. Customers are not platform users. |

### 2. Data Model: Two Tables

#### `customers` — Core customer identity

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Public identifier |
| `tenant_id` | `UUID` | NOT NULL, indexed | Multi-tenant isolation |
| `first_name` | `VARCHAR(100)` | NOT NULL | |
| `last_name` | `VARCHAR(100)` | NOT NULL | |
| `email` | `VARCHAR(255)` | NULLABLE, indexed | Unique per tenant (partial unique index) |
| `phone` | `VARCHAR(30)` | NULLABLE, indexed | E.164 format preferred |
| `address_line1` | `VARCHAR(255)` | NULLABLE | |
| `address_line2` | `VARCHAR(255)` | NULLABLE | |
| `city` | `VARCHAR(100)` | NULLABLE | |
| `county` | `VARCHAR(100)` | NULLABLE | Romanian: "județ" |
| `postal_code` | `VARCHAR(20)` | NULLABLE | |
| `country` | `VARCHAR(2)` | NULLABLE, default `'RO'` | ISO 3166-1 alpha-2 |
| `is_active` | `BOOLEAN` | NOT NULL, default `TRUE` | Soft delete |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, `server_default=now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, `server_default=now(), onupdate=now()` | |

**Indexes**:
- `idx_customers_tenant_id` on `(tenant_id)`
- `idx_customers_tenant_name` on `(tenant_id, last_name, first_name)`
- `idx_customers_tenant_email` on `(tenant_id, email)`
- `idx_customers_tenant_phone` on `(tenant_id, phone)`
- `idx_customers_tenant_active` on `(tenant_id, is_active)`

**Unique constraint**: `uq_customers_tenant_email` → `UNIQUE (tenant_id, email)` (partial, excludes NULLs)

#### `customer_notes` — Free-text notes

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | PK | |
| `customer_id` | `UUID` | FK → `customers.id` CASCADE, NOT NULL, indexed | |
| `tenant_id` | `UUID` | NOT NULL, indexed | Redundant for query efficiency |
| `content` | `TEXT` | NOT NULL | Free-text note |
| `created_by` | `UUID` | FK → `users.id`, NOT NULL | Platform user who wrote the note |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, `server_default=now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, `server_default=now(), onupdate=now()` | |

### 3. Email Uniqueness: Per-Tenant, Not Global

Two different tenants may both have `john@example.com`. Within a tenant, duplicate emails are prevented.

### 4. Hierarchical Tenant Scoping (ADR-0010)

- Institution user: sees customers from all branches
- Branch user: sees only their branch's customers
- Customer `tenant_id` records which branch the customer belongs to

### 5. Cursor-Based Pagination

For `GET /api/v1/customers` — cursor encodes `id` + sort value of the last returned item.

### 6. CSV Import (CUST-06)

`POST /api/v1/customers/import` (Manager+): multipart/form-data, max 10MB, batch insert of 100, returns summary with errors.

### 7. Customer History (CUST-03)

Aggregated read-model via internal API calls to appointments, jobs, invoices, files contexts. Circuit breakers and 2s timeouts per call.

---

## API Contract Summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/customers` | Employee+ | Create customer |
| `GET` | `/api/v1/customers` | Employee+ | List/search (cursor-paginated) |
| `GET` | `/api/v1/customers/{id}` | Employee+ | Get detail |
| `PATCH` | `/api/v1/customers/{id}` | Employee+ | Partial update |
| `DELETE` | `/api/v1/customers/{id}` | Admin only | Soft-delete |
| `GET` | `/api/v1/customers/{id}/history` | Employee+ | Aggregated history |
| `POST` | `/api/v1/customers/{id}/notes` | Employee+ | Add note |
| `GET` | `/api/v1/customers/{id}/notes` | Employee+ | List notes |
| `POST` | `/api/v1/customers/import` | Manager+ | CSV import |

---

## Integration Points

### Domain Events (Emitted)
- `CustomerCreated` → notifications, loyalty
- `CustomerUpdated` → audit_logs
- `CustomerDeactivated` → appointments, notifications

### Domain Events (Consumed)
- `AppointmentCreated`, `InvoicePaid`, `CompanyDeleted`

---

## Consequences

### Positive
- Clear bounded context with well-defined boundaries
- Tenant isolation at every query via `tenant_id = ANY(:accessible_tenant_ids)`
- Hierarchical tenant support works out-of-the-box
- Cursor pagination prevents drift
- CSV import enables migration
- Soft-delete preserves referential integrity

### Negative
- History endpoint depends on 4 downstream services — mitigated by circuit breakers and timeouts
- Per-tenant email uniqueness adds partial unique index complexity
- CSV import is synchronous — acceptable for MVP, should move to background job for large imports

---

## Validation Plan

| # | Test | Expected Result |
|---|------|----------------|
| V1 | Create customer in Tenant A, query as Tenant B | Customer NOT visible to Tenant B |
| V2 | Create in Branch X, query as Institution | Customer IS visible |
| V3 | Create in Branch X, query as Branch Y (same institution) | Customer NOT visible to Branch Y |
| V4 | Duplicate email within same tenant | Returns 409 Conflict |
| V5 | Same email in different tenants | Both succeed |
| V6 | Search by name (case-insensitive) | Returns matching customer |
| V7 | Search by phone partial | Returns matching customer |
| V8 | Cursor pagination stability after insertions | No duplicates, no gaps |
| V9 | Soft delete: DELETE then GET | Returns 404; appears with `?is_active=false` |
| V10 | Soft delete preserves related data | Appointment still references customer |
| V11 | Customer history aggregated | Returns counts + recent from all contexts |
| V12 | History degraded when downstream unavailable | Returns partial data, no 500 |
| V13 | Add note, then fetch notes | Note appears, newest first |
| V14 | CSV import: 50 valid rows | All 50 created |
| V15 | CSV import: partially invalid rows | Valid created, invalid reported as errors |
