# API Contracts

Contract-first API design. Each domain's contract is defined as an OpenAPI 3.0
YAML file **before** implementation begins. Both the backend (Pydantic schemas)
and iOS app (Swift DTOs) independently comply to the same contract.

## Contracts

| Domain | Contract | Status | Endpoints |
|--------|----------|--------|-----------|
| auth | [auth.yaml](auth.yaml) | ✅ Done | register, login, refresh, logout, MFA setup, MFA verify |
| customers | [customers.yaml](customers.yaml) | ✅ Done | CRUD, notes (list+create), history, CSV import |
| appointments | [appointments.yaml](appointments.yaml) | ✅ Done | CRUD, cancel, list with filters |
| jobs | [jobs.yaml](jobs.yaml) | ✅ Done | CRUD, cancel, list with filters |
| companies | companies.yaml | Pending | — |
| invoices | invoices.yaml | Pending | — |
| users | users.yaml | Pending | — |
| notifications | notifications.yaml | Pending | — |
| files | files.yaml | Pending | — |

## Compliance

### Backend
Pydantic v2 `BaseModel` schemas in `app/{domain}/schemas.py` must match the
contract's `components/schemas`. Field names, types, `minLength`, `maxLength`,
`pattern`, and `nullable` flags must all align.

To verify: diff the contract schema against the Pydantic model's JSON Schema output.

### iOS
Swift `Codable` DTOs in `mobile/ios/NexusApp/NexusApp/Data/DTOs/` must match
the contract's `CodingKeys` (snake_case ↔ camelCase), optionality, and types.

To verify: check that every field in the contract's response schema has a
corresponding property in the Swift DTO with the correct type and `CodingKey`.

## Shared patterns across all contracts

- **Pagination**: Cursor-based (`cursor` + `limit`). Response wraps `data[]` + `cursor{next, has_more}`.
- **Errors**: RFC 7807 (`{type, title, detail, status}`).
- **Auth**: All endpoints except register/login require `Authorization: Bearer <token>`.
- **Multi-tenant**: `X-Tenant-ID` header on all requests. Optional `X-Branch-ID` for hierarchical tenants.

