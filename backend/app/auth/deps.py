"""Auth domain dependency injection."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from app.core.database import get_session


async def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    """Provide an AuthService instance with database session.

    Redis client is not injected here since it requires async initialization.
    In production, use a lifespan-managed Redis connection pool.
    """
    return AuthService(session=session)
