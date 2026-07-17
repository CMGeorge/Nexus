"""Auth domain dependency injection."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from app.core.database import get_session
from app.core.redis_client import get_redis


async def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    """Provide an AuthService instance with database session and Redis.

    Redis is auto-initialized on first call and used for:
    - Refresh token blacklisting (fast revocation checks)
    - Rate limiting (future)
    If Redis is unavailable, AuthService degrades gracefully (DB-only checks).
    """
    try:
        redis = await get_redis()
    except Exception:
        redis = None
    return AuthService(session=session, redis=redis)
