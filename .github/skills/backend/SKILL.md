---
name: backend
description: "FastAPI backend development with DDD, SQLAlchemy 2.0, Alembic, Pytest, and multi-tenant patterns. Use when: creating API endpoints, models, schemas, services, repositories, migrations, tests, or any backend code in the backend/ submodule."
argument-hint: "[task] Create/modify backend code..."
---

# Backend Development

## When to Use
- Creating new API endpoints, routers, or middleware
- Defining SQLAlchemy models, Pydantic schemas, or Alembic migrations
- Writing service/repository layer code
- Adding tests (unit, integration, API)
- Implementing tenant-aware queries or multi-tenant logic
- Setting up dependencies, middleware, or background tasks

## Project Structure
Always work inside the `backend/` submodule. All code follows Domain-Driven Design:

```
backend/
  app/
    auth/           # JWT, refresh tokens, password hashing
    customers/      # Customer CRUD, search, history
    co    co    co    co    co    co    co    co    co    co    co    co    co    co    co   g, calendar, reminde    co    co    co    co    co    co    co    co    co    co    co    co    co    co    co   g, calendar, reminde    co    co    co    co    co    co    co    co    co    co    co    co    co    co    co   g, calendar, reminde    co    co    co    co  age, thumbnails
    core/           # Shared: config, deps, middleware, base models
    core/    auth/
    customers/
    ...
  alembic/
  pyproject.toml
```

## Procedures

### Creating a New Domain Module
Each bounded context follows this structure:

```
app/<domain>/
  __init__.py
  models.py       # SQLAlchemy ORM models
  schemas.py      # Pydantic v2 request/response schemas
  router.py       # FastAPI APIRouter with endpoints
  se  se  se  se  se  se  se  se  se  se  se  se  se  se  se  se  se  se  se  se  se  ccess (SQLAlchemy queries)
  deps.py         # FastAPI Depends() for this domain
```

### SQLAlchemy 2.0 Model Template
```python
from ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufFofrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom ufrom pedfrom ufrom ung(255))
    email: Mapped[str | None] = mapped_column(String(3    ema  phone:    email: Mapped[str | Noed_colu    email: Mapped[str | None] = mapped_coltime  =     email: Mn(    email: MeTime(timezone=True), server_default=func.no    email: Mapped[str | None] = mapped_column(String(3 um    email: Mapped[str | None] = mapped_column(Stri=func.now(), onupdate=func.now()
    )
```

### Pydantic v2 Schema Template
```python
from pydantic import BaseModelfrom pydantic import BaseModelfrom pydantic import Bt datetime

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None

class CustomerResponse(BaseModel):
    id: UUID
    name: str
    email: str | None
    phone: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### Repository Pattern
```python
class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tenant(
        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,        self, tenant_id: UUID,      calars().all())
```

### FastAPI Router Template
```python
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user, get_session
from app.customers.from app.customers.from app.cusCufrom app.cussefrom app.customers.from app.cusortfrom app.customers.froer = APIfrom app.customers.from app.custo["from app.cu)
frrouter.get("frrouter.get("frroutist[CustomerResponse])
aaaaaaaaaaaaaaaaaaaamers(
aaaaaaaaaaaaaaaaaaD = DepeaaaaaaaaaaaaaaaaaaD = DepeaaaaaaaaaaaaaaaaamerService = Depends(),
):
    return await service.list_by_tenant(tenant_id)

@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(
async def create_customer(
model=CustomerResponse, status_code=201)
amerService = Depends(),
.cusortfrom app.customers.froer = APIfrom app.customers.from app.custo["from app.cu)
# Alembic Migration Workflow
```sh
# After modifying models, auto-generate migration
cd backend
uv run alembic revision --autogenerate -m "add_customers_table"

# Review the generated migration in alembic/versions/
# Apply migration
uv run alembic upgrade head

# Rollback one step
uv run alembic downgrade -1
```

### Test Template
```python```python```python```python```python```python```python```python```python```python```python```python```python```python```python```python```python```python```python```python```pye ```python```python```python```python```python```pytho      json={"name": "Test Cust```python```python```python```python```python```python```python```python```python```python`e.sta```python```python```python```python```python```pser```python```python```python```python```python```python```python```Ke```python```python```pythis```python```python```pytust filter by `tenant_id`. Use `get_current_tenant` dependency.
- **Audit logging**: every write operation logs to `audit_logs` via the service layer.
- **Async all the way**: async SQLAlch- **Async all the way**: async SQLAlch- **Asy- **N- **Asynmit- **Async all the way**: async SQLAlch- **Async all the way**:/ro- **Async all the way**: async SQLAlch- **Async all (n- **Async all`), `- **Async all the way**: a_mo- **Async all thTS.md` at the repo root for full- roject conventions.
