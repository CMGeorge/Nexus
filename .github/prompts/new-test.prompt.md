---
description: "Generate Pytest test files for a domain module: unit tests for services, integration tests for API endpoints, with proper async fixtures and tenant-aware setup."
argument-hint: "domain-or-file"
agent: "agent"
---

Generate comprehensive tests for `$1` in the `backend/` submodule.

## Test Categories to Generate

### Integration Tests (`tests/$1/test_router.py`)
- CRUD happy paths (create, read, update, delete)
- Authentication (missing/invalid/expired token -> 401)
- Authorization (wrong role -> 403)
- Validation (invalid input -> 422)
- Tenant isolation (cannot access other tenant's data)
- Pagination (limit, offset, total count)
- Search and filtering

### Unit Tests (`tests/$1/test_service.py`)
- Business logic rules
- Edge cases (empty results, duplicate entries, boundary values)
- Error conditions and exception handling

### Conftest (`tests/$1/conftest.py`)
- `async_client` fixture with `httpx.AsyncClient(app, base_url="http://test")`
- `auth_headers` fixture for each role (admin, manager, employee)
- `sample_data` fixture for test records

## Patterns to Follow

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_requires_auth(async_client: AsyncClient):
    response = await async_client.get("/api/v1/$1/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_tenant_isolation(
    async_client: AsyncClient,
    tenant_a_headers: dict,
    tenant_b_headers: dict,
):
    # Create in tenant A
    r = await async_client.post("/api/v1/$1/", json={...}, headers=tenant_a_headers)
    assert r.status_code == 201

    # Tenant B cannot see it
    r = await async_client.get("/api/v1/$1/", headers=tenant_b_headers)
    assert len(r.json()) == 0
```

## Requirements
- Use `pytest-asyncio` (auto mode)
- Use `httpx.AsyncClient` for API tests
- Never mock the database - use real test DB
- Mock external services only (email, storage)
- Each test function is independent (no shared state)
- Use English test names: `test_<action>_<condition>_<expected>`
- Target 80%+ coverage per domain

## References
- See `AGENTS.md` for project conventions
- See `.github/skills/backend/SKILL.md` for test template
