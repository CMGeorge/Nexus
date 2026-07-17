"""Auth domain test fixtures."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base


# Test data constants
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "SecurePass1"
TEST_TENANT_NAME = "Test Company"
TEST_MFA_SECRET = "JBSWY3DPEHPK3PXP"  # Known TOTP test secret


@pytest.fixture
async def test_session() -> AsyncSession:
    """Create an in-memory SQLite session for auth tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()

