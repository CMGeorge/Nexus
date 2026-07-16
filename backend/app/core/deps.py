"""FastAPI dependency injection: auth, tenant, session."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Extract and validate the current user from the JWT bearer token.

    Returns the token payload dict containing at minimum:
        - sub: user UUID
        - tenant_id: tenant UUID
        - roles: list[str]
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return payload


async def get_current_tenant(
    request: Request,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UUID:
    """Resolve the current tenant ID.

    Priority:
    1. X-Tenant-ID header (for service-to-service calls)
    2. Subdomain (for browser requests)
    3. Token payload tenant_id (fallback)
    """
    tenant_id_str = request.headers.get("X-Tenant-ID")

    if tenant_id_str is not None:
        try:
            return UUID(tenant_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid X-Tenant-ID format",
            )

    # Fall back to token-embedded tenant
    token_tenant = current_user.get("tenant_id")
    if token_tenant is not None:
        return UUID(token_tenant)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unable to resolve tenant",
    )


# Re-export for convenience
__all__ = [
    "get_current_user",
    "get_current_tenant",
    "get_session",
]
