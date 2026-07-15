# API Contracts

Contract-first API design. Each domain's contract is defined as an OpenAPI-compatible
YAML file before implementation begins.

## Format
`{domain}.yaml` -- one file per bounded context.

## Contract Template
See `api-designer` agent for the contract template structure.

## Contracts

| Domain | Contract | Status |
|--------|----------|--------|
| auth | auth.yaml | Pending |
| customers | customers.yaml | Pending |
| companies | companies.yaml | Pending |
| appointments | appointments.yaml | Pending |
| jobs | jobs.yaml | Pending |
| invoices | invoices.yaml | Pending |
| users | users.yaml | Pending |
| notifications | notifications.yaml | Pending |
| files | files.yaml | Pending |

## Usage
Contracts are the source of truth for:
1. API implementation (Pydantic schemas validate against contracts)
2. Integration tests (test responses match contract schemas)
3. Frontend API client generation
4. API documentation (Swagger/OpenAPI)
