---
description: "Scaffold a new bounded context (domain module) following DDD structure: models, schemas, router, service, repository, deps, and tests."
argument-hint: "domain-name"
agent: "agent"
---

Scaffold a new bounded context called `$1` in the `backend/` submodule.

## Structure to Create
```
backend/app/$1/
  __init__.py       # Empty
  models.py         # SQLAlchemy 2.0 ORM model with id (UUID), tenant_id, created_at, updated_at
  schemas.py        # Pydantic v2 Create/Update/Response schemas with from_attributes=True
  router.py         # FastAPI APIRouter with CRUD endpoints (list, create, get, update, delete)
  service.py        # Business logic class, injected via Depends()
  repository.py     # Data access class, tenant-filtered queries
  deps.py           # FastAPI dependencies: get_service, get_repository

backend/tests/$1/
  __init__.py
  test_router.py    # Integration tests with httpx.AsyncClient  test_router.py    # Integration tests with httpx.AsyncClient  test_router.py    # Integrat
---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll---ll--- what, when)
- Models use `mapped_column()` and `Mapped[]` type annotations
- Schemas use Pydantic v2 with `model_config = {"from_attributes": True}`
- Router registers in `backend/app/main.py` under `/api/v1/$1`
- Tests use `pytest-asyncio` and `httpx.AsyncClient`
- Follow patterns from existing domains (e.g., `customers/`, `appointments/`)
- Use English for all code and comments- Use English for all code and comments- Use English for all code and comments- Use English fomd` for detailed code templates
