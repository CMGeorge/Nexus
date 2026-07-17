---
description: "Scaffold a new bounded context (domain module) following DDD structure: models, schemas, router, service, repository, deps, and tests."
argument-hint: "domain-name"
---

Scaffold a new bounded context called `$1` in the `backend/` submodule.

## Structure to Create
```
backend/app/$1/
  __init__.py       # Module docstring
  models.py         # SQLAlchemy 2.0 ORM: mapped_column(), Mapped[], id (UUID), tenant_id, created_at, updated_at
  schemas.py        # Pydantic v2: Create/Update/Response schemas, from_attributes=True, Field(description="...")
  router.py         # FastAPI APIRouter: list, create, get, update, delete endpoints
  service.py        # Business logic class, injected via Depends()
  repository.py     # Data access class, all queries filtered by tenant_id
  deps.py           # FastAPI dependencies: get_service, get_repository

backend/tests/$1/
  __init__.py
  conftest.py       # async_client fixture, auth headers, sample data
  test_router.py    # Integration tests with httpx.AsyncClient
  test_service.py   # Unit tests for business logic
```

## Conventions
- Models use `mapped_column()` and `Mapped[]` type annotations
- Every table has `id` (UUID, primary key), `tenant_id` (Foreign Key), `created_at`, `updated_at`
- Schemas use Pydantic v2 with `model_config = {"from_attributes": True}`
- All schema fields have `Field(description="...")`
- Router registers in `backend/app/main.py` under `/api/v1/$1`
- All endpoints are `async def` with proper RFC 7807 error responses
- All public functions have docstrings
- Business logic in service layer only, never in router
- Repository queries always filtered by `tenant_id`
- Tests use `pytest-asyncio` and `httpx.AsyncClient`
- Tests cover: happy path, auth (401), roles (403), validation (422), tenant isolation
- Follow patterns from existing domains (auth/, core/)
- Use English for all code and comments
