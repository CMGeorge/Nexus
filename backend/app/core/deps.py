"""FastAPI dependency injection: auth, tenant, session."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import decode_access_token
from app.core.tenant import Tenant, get_accessible_tenant_ids

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
        - institution_id: institution UUID (if user is at branch level)
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
    session: AsyncSession = Depends(get_session),
) -> Tenant:
    """Resolve the current tenant from X-Tenant-ID header, subdomain, or JWT.

    Returns the full Tenant ORM object (not just UUID) so downstream
    dependencies can check tenant.is_institution / tenant.is_branch.

    Priority:
    1. X-Tenant-ID header (explicit override — institution users may switch branches)
    2. Subdomain (for browser requests)
    3. JWT payload tenant_id (fallback)
    """
    tenant_id_str = request.headers.get("X-Tenant-ID")
    tenant_id: UUID | None = None

    if tenant_id_str is not None:
        try:
            tenant_id = UUID(tenant_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid X-Tenant-ID format",
            )

    # Fall back to token-embedded tenant
    if tenant_id is None:
        token_tenant = current_user.get("tenant_id")
        if token_tenant is not None:
            tenant_id = UUID(token_tenant)

    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to resolve tenant",
        )

    # Load the full Tenant row
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found",
        )

    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is inactive",
        )

    return tenant


async def get_accessible_scope(
    current_tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_session),
) -> list[UUID]:
    """Return the list of tenant IDs this request can access.

    Institution-level user → [institution_id, branch_1_id, branch_2_id, ...]
    Branch-level user → [branch_id]

    Use this in repository queries:
        WHERE tenant_id = ANY(:accessible_scope)
    """
    return await get_accessible_tenant_ids(current_tenant.id, session)


# Re-export for convenience
__all__ = [
    "get_current_user",
    "get_current_tenant",
    "get_accessible_scope",
    "get_session",
]
