"""Customers domain test fixtures and dependency overrides."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.deps import get_current_user
from app.core.database import Base, get_session
from app.core.tenant import Tenant

TEST_DATABASE_URL = "postgresql+asyncpg://nexus:nexus_dev@localhost:3671/nexus"

TEST_TENANT_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000001")
TEST_TENANT_B_ID = uuid.UUID("b0000000-0000-0000-0000-000000000002")
TEST_USER_ID = uuid.UUID("c0000000-0000-0000-0000-000000000003")
TEST_USER_ID_B = uuid.UUID("c0000000-0000-0000-0000-000000000004")


def _make_tenant(tenant_id, name, parent_id=None):
    """Create a Tenant ORM object without a DB session."""
    tenant = Tenant.__new__(Tenant)
    tenant.id = tenant_id
    tenant.name = name
    tenant.parent_id = parent_id
    tenant.subdomain = None
    tenant.is_active = True
    return tenant


def _make_user_payload(user_id, tenant_id, roles="Admin,Manager"):
    """Create a mock JWT payload dict for get_current_user."""
    return {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "type": "access",
    }


# ── HTTP client fixture (replaces root conftest) ────────────────


@pytest_asyncio.fixture
async def async_client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ── Session fixture ────────────────────────────────────────────


@pytest_asyncio.fixture
async def db_session():
    """Create a fresh async session connected to the test PostgreSQL DB."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


# ── Tenant fixtures ────────────────────────────────────────────


@pytest_asyncio.fixture
async def tenant_a(db_session):
    """Ensure test tenant A exists and return its Tenant object."""
    from sqlalchemy import select
    stmt = select(Tenant).where(Tenant.id == TEST_TENANT_A_ID)
    result = await db_session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    tenant = Tenant(
        id=TEST_TENANT_A_ID, name="Test Company A",
        parent_id=None, subdomain="test-a", is_active=True,
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


@pytest_asyncio.fixture
async def tenant_b(db_session):
    """Ensure test tenant B exists and return its Tenant object."""
    from sqlalchemy import select
    stmt = select(Tenant).where(Tenant.id == TEST_TENANT_B_ID)
    result = await db_session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    tenant = Tenant(
        id=TEST_TENANT_B_ID, name="Test Company B",
        parent_id=None, subdomain="test-b", is_active=True,
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


# ── Auth override fixtures for router tests ────────────────────

# Use NullPool to avoid "another operation is in progress" errors
# when tests send multiple requests that reuse the same asyncpg connection.
_test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
_test_session_factory = async_sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False,
)


async def _override_get_session():
    """Session override for tests — uses NullPool to avoid connection sharing."""
    async with _test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
def override_auth_tenant_a():
    """Override auth deps for tenant A — returns single-tenant scope."""
    from app.core.deps import get_current_tenant_id

    user_payload = _make_user_payload(TEST_USER_ID, TEST_TENANT_A_ID)
    app.dependency_overrides[get_current_user] = lambda: user_payload
    app.dependency_overrides[get_current_tenant_id] = lambda: TEST_TENANT_A_ID
    app.dependency_overrides[get_session] = _override_get_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_auth_tenant_b():
    """Override auth deps for tenant B — returns single-tenant scope."""
    from app.core.deps import get_current_tenant_id

    user_payload = _make_user_payload(TEST_USER_ID_B, TEST_TENANT_B_ID)
    app.dependency_overrides[get_current_user] = lambda: user_payload
    app.dependency_overrides[get_current_tenant_id] = lambda: TEST_TENANT_B_ID
    app.dependency_overrides[get_session] = _override_get_session
    yield
    app.dependency_overrides.clear()
